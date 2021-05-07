#!/usr/bin/env bash
import argparse
import plotille
import pandas as pd
from expman import Experiment, JSONLogger


def main():
    parser = argparse.ArgumentParser(description='Plots an experiment in terminal')
    parser.add_argument('glob', help='directory of experiment to plot')
    parser.add_argument('--window', help='smoothing window', type=int, default=100)
    parser.add_argument('--width', help='smoothing window', type=int)
    parser.add_argument('--height', help='smoothing window', type=int)
    parser.add_argument('-x', help='x axis', default='frames')
    parser.add_argument('-y', help='y axis', default='mean_win_rate')
    args = parser.parse_args()

    exps_and_logs = Experiment.discover_logs(args.glob, JSONLogger())
    print('loaded {} experiments'.format(len(exps_and_logs)))

    fig = plotille.Figure()
    kwargs = {}
    for exp, log in exps_and_logs:
        if log:
            df = pd.DataFrame(log)
            fig.plot(
                X=df[args.x], 
                Y=df[args.y].rolling(args.window, min_periods=1).mean(),
                label=exp.name,
                **kwargs
            )
    fig.x_label = args.x
    fig.y_label = args.y
    if args.height:
        fig.height = args.height
    if args.width:
        fig.width = args.width

    print(fig.show(legend=True))
