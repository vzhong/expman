from .logger import Logger
import wandb


class WandbLogger(Logger):

    def __init__(self, name):
        super().__init__()
        self.name = name
        self.wandb_config = None

    def start(self, dlog, config=None, delete_existing=False):
        super().start(dlog, config=config, delete_existing=delete_existing)
        wandb.init(project=self.name, config=config)
        self.wandb_config = wandb.config

    def log(self, content: dict):
        wandb.log(content)

    def finish(self):
        wandb.finish()
        self.wandb_config = None
