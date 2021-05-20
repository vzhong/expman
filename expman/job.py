import submitit
import logging
import torch
import argparse
import glob
import os
from .experiment import Experiment


class Job:

    def __init__(self, exp=None):
        self.exp = exp

    @property
    def flags(self):
        """
        Experiment configs accessible through the form of a `argparse.Namespace`.
        """
        return argparse.Namespace(**self.exp.config)

    def non_user_state_dict(self) -> dict:
        return {}

    def load_non_user_state_dict(self, d: dict):
        return

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
        d = self.non_user_state_dict()
        d.update(self.state_dict())
        fjob = self.job_checkpoint_path(explog)
        logging.critical('Saving job to {}'.format(fjob))
        torch.save(d, fjob)

    @classmethod
    def from_fconfig(cls, explog, job=None):
        assert os.path.isfile(explog), 'Cannot launch job without experiment config'
        exp = Experiment.from_fconfig(explog)
        job = job or cls(exp)
        if job.exp is None:
            job.exp = exp
        logging.critical('Loading experiment from {}'.format(explog))
        fjob = job.job_checkpoint_path(explog)
        if os.path.isfile(fjob):
            logging.critical('Resuming job from {}'.format(fjob))
            try:
                d = torch.load(fjob)
                job.load_non_user_state_dict(d)
                job.load_state_dict(d)
            except Exception:
                logging.critical('Failed to load job... restarting')
        return job

    def __call__(self, explog):
        """
        Runs the job, resuming from checkpoint if it exists.
        """
        self.from_fconfig(explog, job=self)
        self.forward(explog)

    @classmethod
    def discover_jobs(cls, glob_path, explog_fname='exp.json'):
        jobs = []
        for d in glob.glob(glob_path):
            files = os.listdir(d)
            if explog_fname in files:
                jobs.append(cls.from_fconfig(os.path.join(d, explog_fname)))
        return jobs


class SlurmJob(Job):
    """
    This supports preemption through submitit
    """

    def __init__(self):
        super().__init__()
        self.job_id = None

    def non_user_state_dict(self) -> dict:
        return dict(job_id=self.job_id)

    def load_non_user_state_dict(self, d: dict):
        self.job_id = d.get('job_id', None)

    def checkpoint(self, explog) -> submitit.helpers.DelayedSubmission:
        super().checkpoint(explog)
        training_callable = self.__class__()
        return submitit.helpers.DelayedSubmission(training_callable, explog)

    def launch_slurm(self, explog, slurm_kwargs=None, executor=None):
        if executor is None:
            executor = submitit.SlurmExecutor(folder=os.path.join(self.exp.logdir, 'slurm'), max_num_timeout=3)
            executor.update_parameters(**slurm_kwargs)
        slurm_job = executor.submit(self, explog)
        self.job_id = slurm_job.job_id
        return slurm_job
