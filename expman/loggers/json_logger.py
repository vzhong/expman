from .logger import Logger
import os
import ujson as json


class JSONLogger(Logger):

    def __init__(self, logname='log.jsonl'):
        super().__init__()
        self.logname = logname
        self.fname = None

    def start(self, dlog, config=None, delete_existing=False):
        super().start(dlog, config=config, delete_existing=delete_existing)
        self.fname = os.path.join(self.dlog, self.logname)
        if delete_existing and os.path.isfile(self.fname):
            os.remove(self.fname)

    def log(self, content: dict):
        with open(self.fname, 'at') as f:
            f.write(json.dumps(content) + '\n')

    def load_logs(self, ignore=tuple()):
        logs = []
        with open(self.fname, 'rt') as f:
            for line in f:
                d = {k: v for k, v in json.loads(line).items() if k not in ignore}
                logs.append(d)
        return logs

    def finish(self):
        self.name = None
