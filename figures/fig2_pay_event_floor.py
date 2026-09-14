"""Figure 2. Pay event study with and without exposure to the wage floor.

Both series are read from the delivered files. The accent series conditions on
occupation and release effects only, and the grey series adds a floor-exposure
path that is free to differ by release.
"""

import csv
import os

import matplotlib.pyplot as plt
import numpy as np

from paperstyle import (ACCENT, ANNOT, GREY, TEXT_WIDTH_IN, apply_style,
                        save_all)

HERE = os.path.dirname(os.path.abspath(__file__))
DATA = os.path.join(HERE, "data")
N_ACCENT, N_GREY = 366, 347   # occupations behind each series, from the draft


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
    ya, ba, loa, hia = read_event("v2_fig_event_pay.csv")
    yg, bg, log_, hig = read_event("v2_fig_event_pay_nlw.csv")
    ref = int(ya[ba == 0][0])
    off = 0.11

    fig, ax = plt.subplots(figsize=(TEXT_WIDTH_IN, 3.6))
    ax.axhline(0.0, color="black", lw=0.7, zorder=1)
    ax.axvline(ref + 0.5, color=GREY, lw=0.8, ls=(0, (3, 3)), zorder=1)

    mg = yg == ref
    ax.errorbar(yg[~mg] + off, bg[~mg], yerr=[(bg - log_)[~mg], (hig - bg)[~mg]],
                fmt="o", ms=4.0, mfc="white", mec=GREY, mew=0.9, ecolor=GREY,
                elinewidth=0.8, capsize=0, ls="none", zorder=3)
    ax.plot(yg[mg] + off, bg[mg], "o", ms=4.0, mfc="white", mec=GREY, mew=0.9,
            zorder=3)

    ma = ya == ref
    ax.errorbar(ya[~ma] - off, ba[~ma], yerr=[(ba - loa)[~ma], (hia - ba)[~ma]],
                fmt="o", ms=4.6, color=ACCENT, ecolor=ACCENT, elinewidth=1.3,
                capsize=0, ls="none", zorder=4)
    ax.plot(ya[ma] - off, ba[ma], "o", ms=4.6, mfc="white", mec=ACCENT, mew=1.3,
            zorder=5)
    ax.text(ref - off - 0.14, 0.006, "ref.", color=ACCENT, fontsize=ANNOT,
            ha="right", va="bottom")

    ylo = float(min(loa.min(), log_.min())) - 0.035
    yhi = float(max(hia.max(), hig.max())) + 0.065
    ax.text(ref + 0.62, ylo + 0.55 * (yhi - ylo), "post-2016", color=GREY,
            fontsize=ANNOT, ha="left", va="center", rotation=90)

    ax.text(2020.5, yhi - 0.004,
            f"occupation and release effects only, {N_ACCENT} occupations",
            color=ACCENT, fontsize=ANNOT, ha="right", va="top")
    ax.text(2016.35, ylo + 0.006,
            f"floor exposure controlled, {N_GREY} occupations",
            color=GREY, fontsize=ANNOT, ha="left", va="bottom")

    ax.set_xlim(2013.6, 2020.6)
    ax.set_ylim(ylo, yhi)
    ax.set_xticks(list(range(2014, 2021)))
    ax.set_xlabel("ASHE release (April reference date)")
    ax.set_ylabel("Change in slope of log pay on\n"
                  "automation probability, relative\n"
                  "to 2015 (log points)")

    save_all(fig, os.path.join(HERE, "fig2_pay_event_floor"))
    plt.close(fig)


if __name__ == "__main__":
    main()
