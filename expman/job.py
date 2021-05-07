import submitit
import logging
import torch
import argparse
import os
from .experiment import Experiment


class Job:

    def __init__(self):
        self.exp = None

    @property
    def flags(self):
        """
        Experiment configs accessible through the form of a `argparse.Namespace`.
        """
        return argparse.Namespace(**self.exp.config)

    def state_dict(self) -> dict:
        """
        Return things to be saved.
        """
        raise NotImplementedError()

    def load_state_dict(self, d: dict):
        """
        Load from saved dict.
        """
        raise NotImplementedError()

    def forward(self, explog: str):
        """
        Start from experiment specified in explog.
        At this point `self.exp` has been loaded.
        """
        raise NotImplementedError()

    def job_checkpoint_path(self, explog):
        """
        Where the job's state_dict is saved.
        """
        root = os.path.dirname(explog)
        return os.path.join(root, 'job.tar')

    def checkpoint(self, explog):
        """
        Saves the checkpoint to `explog`.
        """
        assert self.exp is not None, 'Cannot checkpoint empty experiment!'
        logging.critical('Saving experiment to {}'.format(explog))
        self.exp.save(explog)
        d = self.state_dict()
        fjob = self.job_checkpoint_path(explog)
        logging.critical('Saving job to {}'.format(fjob))
        torch.save(d, fjob)

    def __call__(self, explog):
        """
        Runs the job, resuming from checkpoint if it exists.
        """
        assert os.path.isfile(explog), 'Cannot launch job without experiment config'
        self.exp = Experiment.from_fconfig(explog)
        logging.critical('Loading experiment from {}'.format(explog))
        fjob = self.job_checkpoint_path(explog)
        if os.path.isfile(fjob):
            logging.critical('Resuming job from {}'.format(fjob))
            d = torch.load(fjob)
            self.load_state_dict(d)
        self.forward(explog)


class SlurmJob(Job):
    """
    This supports preemption through submitit
    """

    def checkpoint(self, explog) -> submitit.helpers.DelayedSubmission:
        super().checkpoint(explog)
        training_callable = self.__class__()
        return submitit.helpers.DelayedSubmission(training_callable, explog)

    def launch_slurm(self, explog, slurm_kwargs=None, executor=None):
        if executor is None:
            executor = submitit.SlurmExecutor(folder=os.path.join(self.exp.logdir, 'slurm'), max_num_timeout=3)
            executor.update_parameters(**slurm_kwargs)
        slurm_job = executor.submit(self, explog)
        return slurm_job
