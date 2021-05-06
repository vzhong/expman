import os
import glob
import datetime
import logging
import ujson as json
from pathlib import Path


class Experiment:

    def __init__(self, config, loggers=tuple(), name_field='name', logdir_field='logdir', step=0, last_written_time=None):
        self.name_field = name_field
        self.logdir_field = logdir_field
        self.config = config
        self.loggers = list(loggers)
        self.step = step
        self.last_written_time = last_written_time
        self.started = False
        self.config['seedless_name'] = self.name.split('-seed')[0]

    @property
    def name(self):
        return self.config[self.name_field]

    @property
    def logdir(self):
        return Path(self.config[self.logdir_field])

    @property
    def expdir(self):
        return self.logdir.joinpath(self.name)

    @property
    def explog(self):
        return self.expdir.joinpath('exp.json')

    @classmethod
    def from_namespace(cls, args, name_field='name', logdir_field='logdir', loggers=tuple()):
        return cls(vars(args), name_field=name_field, logdir_field=logdir_field, loggers=loggers)

    @classmethod
    def from_fconfig(cls, fname):
        with open(fname) as f:
            return cls(**json.load(f))

    def time_since_last_written(self):
        return datetime.datetime.utcnow() - datetime.datetime.fromisoformat(self.last_written_time)

    def save(self, fout=None):
        fout = fout or self.explog
        root = Path(fout).parent
        if not root.exists():
            os.makedirs(root)
        with open(fout, 'wt') as f:
            json.dump(dict(
                name_field=self.name_field,
                logdir_field=self.logdir_field,
                config=self.config,
                step=self.step,
                last_written_time=self.last_written_time,
            ), f, indent=2)

    def load(self):
        with open(self.explog) as f:
            d = json.load(f)
            for k, v in d.items():
                setattr(self, k, v)

    def start(self, delete_existing=False):
        if not self.exists():
            logging.critical('Making directory at {}'.format(self.expdir))
            os.makedirs(self.expdir)
        for logger in self.loggers:
            logger.start(self.expdir, self.config, delete_existing=delete_existing)
        self.started = True
        self.save()
        return self

    def load_logs(self, logger, ignore=('time',)):
        assert self.exists(), 'Experiment does not exist at {}'.format(self.expdir)
        logger.start(self.expdir, self.config, delete_existing=False)
        logs = logger.load_logs(ignore=ignore)
        ret = []
        for d in logs:
            ret.append(d)
        logger.finish()
        return ret

    @classmethod
    def discover_logs(self, glob_path, logger, ignore=('time',)):
        dirs = glob.glob(glob_path)
        exps = []
        for d in dirs:
            f = os.path.join(d, 'exp.json')
            if os.path.isfile(f):
                exp = Experiment.from_fconfig(f)
                logs = exp.load_logs(logger, ignore=ignore)
                exps.append((exp, logs))
        return exps

    def exists(self):
        return os.path.isdir(self.expdir)

    def log(self, content: dict):
        assert self.started, 'Please run experiment.start()'
        content['step'] = self.step
        self.last_written_time = content['time'] = datetime.datetime.utcnow().isoformat()
        for logger in self.loggers:
            logger.log(content)
        self.save()
        self.step += 1

    def finish(self):
        for logger in self.loggers:
            logger.finish()
