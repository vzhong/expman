class Logger:

    def __init__(self):
        self.dlog = None

    def start(self, dlog, config=None, delete_existing=False):
        self.dlog = dlog

    def log(self, content: dict):
        raise NotImplementedError()

    def load_logs(self, ignore=tuple()):
        raise NotImplementedError()

    def finish(self):
        pass
