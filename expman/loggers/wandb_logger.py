from .logger import Logger
from .json_logger import JSONLogger
from ..experiment import Experiment
import wandb
import logging


class WandbLogger(Logger):

    def __init__(self, project, name=None, **kwargs):
        super().__init__()
        self.project = project
        self.name = name or project
        self.kwargs = kwargs
        self.run = None
        self.wandb_config = None
        self.started = False

    def start(self, dlog=None, config=None, delete_existing=False):
        super().start(dlog, config=config, delete_existing=delete_existing)
        self.run = wandb.init(project=self.project, id=self.name, config=config, resume=None if delete_existing else 'allow', **self.kwargs)
        self.wandb_config = wandb.config
        self.started = True
        return self

    def log(self, content: dict):
        wandb.log(content)

    def finish(self):
        wandb.finish()
        self.run = None
        self.wandb_config = None

    @classmethod
    def convert_exp(cls, fexp, project):
        exp = Experiment.from_fconfig(fexp)
        json_log = exp.load_logs(JSONLogger())
        logger = cls(project=project, name=exp.name).start(dlog=exp.logdir, config=exp.config, delete_existing=True)
        for r in json_log:
            logger.log(r)
        logger.finish()
        logging.info('Uploaded {} to project {}'.format(fexp, project))
