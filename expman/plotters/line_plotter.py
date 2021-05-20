from .plotter import Plotter
from matplotlib import pyplot as plt
import pandas as pd
import logging
import numpy as np
import seaborn as sns


class LinePlotter(Plotter):

    def plot_group(self, data, x, y, label, ax, xpid=None, read_every=1, smooth_window=10, align_x=1, alpha=0.4, linewidth=3):
        color = next(ax._get_lines.prop_cycler)['color']
        if xpid is not None:
            all_data = []
            unique_xpids = sorted(data[xpid].unique())
            for xid in unique_xpids:
                xp_data = data[data[xpid] == xid][::read_every]
                xp_data[y+'_smooth'] = xp_data[y].rolling(smooth_window, min_periods=smooth_window//2).mean()
                all_data.append(xp_data)
                xs = xp_data[x].to_numpy()
                ys = xp_data[y+'_smooth'].to_numpy()

                order = np.argsort(xs)
                xs = np.take_along_axis(xs, order, axis=0)
                ys = np.take_along_axis(ys, order, axis=0)

                ax.plot(xs, ys, linestyle='dashed', color=color, label='_nolegend_', alpha=alpha)
            data = pd.concat(all_data)
        else:
            data = data[::read_every]
            data[y+'_smooth'] = data[y].rolling(smooth_window, min_periods=smooth_window//2).mean()
        if label is not None:
            data[x] = data[x] // align_x * align_x
            sns.lineplot(data=data, x=x, y=y+'_smooth', label=label, ax=ax, color=color, linewidth=linewidth)

    def plot(self, exps_and_logs, x, y, group=None, xpid=None, read_every=1, smooth_window=10, align_x=1, ax=None, linewidth=3, alpha=0.4, force_label=None):
        if ax is None:
            fig, ax = plt.subplots(figsize=(10, 10))

        data = []
        for exp, logs in exps_and_logs:
            for r in logs:
                r = r.copy()
                r.update(exp.config)
                data.append(r)
        if not data:
            logging.critical('Nothing to plot!')
            return ax

        data = pd.DataFrame(data)

        if group is None:
            self.plot_group(data=data, x=x, y=y, label=force_label, ax=ax, xpid=xpid, read_every=read_every, smooth_window=smooth_window, align_x=align_x, alpha=alpha, linewidth=linewidth)
        else:
            unique_groups = sorted(data[group].unique())
            for g in unique_groups:
                group_data = data[data[group] == g]
                label = force_label or g
                self.plot_group(data=group_data, x=x, y=y, label=label, ax=ax, xpid=xpid, read_every=read_every, smooth_window=smooth_window, align_x=align_x)
        return ax
