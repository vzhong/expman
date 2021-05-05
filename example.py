from expman import Experiment, StdoutLogger, JSONLogger
import argparse
import random
import os

parser = argparse.ArgumentParser()
parser.add_argument('--delete_existing', action='store_true')
parser.add_argument('--project', default='myproj')
parser.add_argument('--logdir', default='logs')
parser.add_argument('--wandb', action='store_true')
parser.add_argument('--plot')
args = parser.parse_args()

# instantiate some loggers we want to use
loggers = [StdoutLogger(), JSONLogger()]
if args.wandb:
    from expman.loggers.wandb_logger import WandbLogger
    loggers.append(WandbLogger(project=args.project))

# build experiment from argparse namespace
exp = Experiment.from_namespace(args, loggers=loggers).start(delete_existing=args.delete_existing)

# make a fake experiment, you can check out the outputs in `logdir`
for i in range(10):
    exp.log(dict(loss=i*0.5, name='hi'))


if args.plot:
    # a more complex example with random seeds and plotting
    from expman.plotters import LinePlotter
    from matplotlib import pylab as plt
    noise = 10
    for seed in range(5):
        for t in ['linear', 'quadratic']:
            # generate two types of experiments, linear and quadratic, each with 5 seeds
            random.seed(seed)
            name = 'exp-seed{}-type{}'.format(seed, t)
            loggers = [JSONLogger()]
            if args.wandb:
                loggers.append(WandbLogger(project='seeded', name=name))
            exp = Experiment(config=dict(seed=seed, type=t, name=name, logdir=os.path.join(args.logdir, 'seeded')), loggers=loggers).start(delete_existing=args.delete_existing)
            for i in range(100):
                if t == 'linear':
                    score = i + random.uniform(-noise, noise)
                elif t == 'quadratic':
                    score = (i/10)**2 + random.uniform(-noise*2, noise*2)
                exp.log(dict(score=score))
            exp.finish()

    exps_and_logs = Experiment.discover_logs(glob_path=os.path.join(args.logdir, 'seeded', '*'), logger=JSONLogger())

    if args.wandb:
        WandbLogger.upload_logs(exps_and_logs, project='seeded_upload')

    plotter = LinePlotter()
    fig, ax = plt.subplots(figsize=(5, 5))
    plotter.plot(exps_and_logs, x='step', y='score', group='type', xpid='name', read_every=2, smooth_window=10, ax=ax)
    fig.savefig(args.plot)
