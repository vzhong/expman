from .logger import Logger
import pprint


class StdoutLogger(Logger):

    def log(self, content: dict):
        pprint.pprint(content)
