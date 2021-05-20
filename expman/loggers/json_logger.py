from .logger import Logger
import logging
import os
import ujson as json


class JSONLogger(Logger):

    def __init__(self, logname='log.jsonl'):
        super().__init__()
        self.logname = logname
        self.fname = None
        self.started = False

    def start(self, dlog, config=None, delete_existing=False):
        super().start(dlog, config=config, delete_existing=delete_existing)
        self.fname = os.path.join(self.dlog, self.logname)
        if delete_existing and os.path.isfile(self.fname):
            os.remove(self.fname)
        self.started = True
        return self

    def log(self, content: dict):
        assert self.started
        with open(self.fname, 'at') as f:
            f.write(json.dumps(content) + '\n')

    def load_logs(self, ignore=tuple(), error='warn'):
        logs = []
        if not os.path.isfile(self.fname):
            if error == 'warn':
                logging.critical('file doesnt exist {}'.format(self.fname))
                return logs
            elif error == 'ignore':
                return logs
            else:
                raise Exception('file doesnt exist {}'.format(self.fname))
        with open(self.fname, 'rt') as f:
            for line in f:
                try:
                    d = {k: v for k, v in json.loads(line).items() if k not in ignore}
                    logs.append(d)
                except Exception as e:
                    if error == 'warn':
                        logging.critical('In {}'.format(self.fname))
                        logging.critical(repr(e))
                    elif error == 'ignore':
                        pass
                    else:
                        raise e
        return logs

    def finish(self):
        self.name = None

    @classmethod
    def convert_rl_log(cls, frl, delete_existing=False):

        def try_num(n):
            try:
                return float(n)
            except Exception:
                return n

        log = cls().start(os.path.dirname(frl), delete_existing=delete_existing)
        with open(frl) as f:
            try:
                header = next(f).strip('#').strip().split(',')
            except StopIteration as e:
                return []
            for line in f:
                if line.startswith('#'):
                    continue
                read = line.strip().split(',')
                row = [try_num(e) for e in read]
                log.log(dict(zip(header, row)))
        logging.info('Converted {} to {}'.format(frl, log.fname))
        return log
