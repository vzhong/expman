#!/usr/bin/env python
import os
import tqdm
import argparse
from ..loggers.json_logger import JSONLogger
from ..loggers.wandb_logger import WandbLogger
from ..experiment import Experiment


def main():
    parser = argparse.ArgumentParser(formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    parser.add_argument('-i', '--input_type', choices=('expman', 'rl'), default='expman', help='input format')
    parser.add_argument('-o', '--output_type', choices=('expman', 'rl', 'wandb'), default='expman', help='output format')
    parser.add_argument('--project', help='wandb project name')
    parser.add_argument('--ignore', nargs='*', help='fields to ignore in config file', default=tuple())
    parser.add_argument('log_files', nargs='+', help='logs to convert')
    args = parser.parse_args()

    files = [os.path.abspath(f) for f in args.log_files]

    # convert to expman format
    if args.input_type == 'expman':
        pass
    elif args.input_type == 'rl':
        for frl in tqdm.tqdm(files, '{}2expman'.format(args.input_type)):
            Experiment.convert_rl_exp(frl)
            flog = os.path.join(os.path.dirname(frl), 'logs.csv')
            if os.path.isfile(flog):
                JSONLogger.convert_rl_log(flog, delete_existing=True)
    else:
        raise NotImplementedError()

    # convert to output
    if args.output_type == 'expman':
        return
    elif args.output_type == 'wandb':
        assert args.project, 'Must give project to wandb'
        for flog in tqdm.tqdm(files, 'expman2{}'.format(args.output_type)):
            fexp = os.path.join(os.path.dirname(flog), 'exp.json')
            WandbLogger.convert_exp(fexp, args.project, ignore=args.ignore)
    else:
        raise NotImplementedError()
