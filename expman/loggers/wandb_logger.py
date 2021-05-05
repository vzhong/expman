from .logger import Logger
import wandb


class WandbLogger(Logger):

    def __init__(self, project, name=None, **kwargs):
        super().__init__()
        self.project = project
        self.name = name or project
        self.kwargs = kwargs
        self.run = None
        self.wandb_config = None

    def start(self, dlog, config=None, delete_existing=False):
        super().start(dlog, config=config, delete_existing=delete_existing)
        self.run = wandb.init(project=self.project, id=self.name, config=config, resume=None if delete_existing else 'must', **self.kwargs)
        self.wandb_config = wandb.config

    def log(self, content: dict):
        wandb.log(content)

    def finish(self):
        wandb.finish()
        self.run = None
        self.wandb_config = None
