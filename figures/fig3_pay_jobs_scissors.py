"""Figure 3. Pay and employment across the automation-risk gradient.

Two panels on a shared x-axis with separate y-scales, because the employment
coefficients run four to seven times the pay coefficients and one scale would
flatten the pay panel.
"""

import csv
import os

import matplotlib.pyplot as plt
import numpy as np

from paperstyle import (ACCENT, ANNOT, GREY, TEXT_WIDTH_IN, apply_style,
                        save_all)

HERE = os.path.dirname(os.path.abspath(__file__))
DATA = os.path.join(HERE, "data")
YLAB = "Change in slope on automation probability (log points)"
PANELS = [("v2_fig_event_pay.csv", "Log mean hourly pay, 366 occupations"),
          ("v2_fig_event_jobs.csv", "Log employee jobs, 309 occupations")]


def read_event(name):
    """Read year, coefficient and interval bounds. The p column goes unread."""
    year, b, lo, hi = [], [], [], []
    with open(os.path.join(DATA, name)) as fh:
        for r in csv.DictReader(fh):
            year.append(int(r["year"]))
            b.append(float(r["b"]))
            lo.append(float(r["lo"]))
            hi.append(float(r["hi"]))
    return np.array(year), np.array(b), np.array(lo), np.array(hi)


def main():
    apply_style()
    fig, axes = plt.subplots(1, 2, figsize=(TEXT_WIDTH_IN, 3.4))
    fig.subplots_adjust(wspace=0.36)

    for ax, (name, title) in zip(axes, PANELS):
        y, b, lo, hi = read_event(name)
        ref = int(y[b == 0][0])
        ax.axhline(0.0, color="black", lw=0.7, zorder=1)
        ax.axvline(ref + 0.5, color=GREY, lw=0.8, ls=(0, (3, 3)), zorder=1)

        m = y == ref
        ax.errorbar(y[~m], b[~m], yerr=[(b - lo)[~m], (hi - b)[~m]], fmt="o",
                    ms=4.2, color=ACCENT, ecolor=ACCENT, elinewidth=1.2,
                    capsize=0, ls="none", zorder=3)
        ax.plot(y[m], b[m], "o", ms=4.2, mfc="white", mec=ACCENT, mew=1.3,
                zorder=4)

        span = float(hi.max() - lo.min())
        ax.set_ylim(float(lo.min()) - 0.10 * span, float(hi.max()) + 0.14 * span)
        ax.text(ref - 0.18, 0.012 * span, "ref.", color=ACCENT, fontsize=ANNOT,
                ha="right", va="bottom")
        ax.text(ref + 0.62, ax.get_ylim()[0] + 0.30 * (ax.get_ylim()[1] -
                ax.get_ylim()[0]), "post-2016", color=GREY, fontsize=ANNOT,
                ha="left", va="center", rotation=90)

        ax.set_title(title, fontweight="bold", loc="left", fontsize=ANNOT + 0.5)
        ax.set_xlabel("ASHE release (April reference date)")
        ax.set_ylabel(YLAB)
        ax.set_xlim(2013.6, 2020.5)
        ax.set_xticks([2014, 2016, 2018, 2020])

    save_all(fig, os.path.join(HERE, "fig3_pay_jobs_scissors"))
    plt.close(fig)


if __name__ == "__main__":
    main()
