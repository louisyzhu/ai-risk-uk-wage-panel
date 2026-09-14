"""Figure D.1. The classification join.

The accent series uses the seven releases published on SOC 2010. The grey
series adds the 2021 to 2023 releases, published on SOC 2020 and joined to the
SOC 2010 risk scores by numeric code. The script computes the agreement between
the two series over the years they share.
"""

import csv
import os

import matplotlib.pyplot as plt
import numpy as np

from paperstyle import (ACCENT, ANNOT, GREY, SHADE, TEXT_WIDTH_IN, apply_style,
                        save_all)

HERE = os.path.dirname(os.path.abspath(__file__))
DATA = os.path.join(HERE, "data")
MISMATCH = "SOC 2020 releases,\n125 of 261 codes mismatched"


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
    yg, bg, log_, hig = read_event("v2_fig_event_contaminated.csv")
    ref = int(ya[ba == 0][0])
    off = 0.11

    shared = np.intersect1d(ya, yg)
    gap = float(np.max(np.abs(ba[np.isin(ya, shared)] - bg[np.isin(yg, shared)])))
    extra = yg[~np.isin(yg, ya)]
    span = (float(extra.min()) - 0.5, float(extra.max()) + 0.5)

    fig, ax = plt.subplots(figsize=(TEXT_WIDTH_IN, 3.4))
    ax.axvspan(*span, color=SHADE, lw=0, zorder=0)
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
    ax.text(ref - off - 0.16, 0.012, "ref.", color=ACCENT, fontsize=ANNOT,
            ha="right", va="bottom")

    ylo = float(min(loa.min(), log_.min())) - 0.05
    yhi = float(max(hia.max(), hig.max())) + 0.16
    ax.text(ref + 0.68, ylo + 0.62 * (yhi - ylo), "post-2016", color=GREY,
            fontsize=ANNOT, ha="left", va="center", rotation=90)

    ax.text(span[1], yhi - 0.012, MISMATCH, color=GREY, fontsize=ANNOT - 0.5,
            ha="right", va="top", linespacing=1.25)
    ax.text(2016.9, yhi - 0.012,
            "the two series agree to within\n"
            f"{gap:.4f} log points before {int(extra.min())}",
            color=GREY, fontsize=ANNOT, ha="left", va="top", linespacing=1.3)

    k = list(ya).index(2019)
    ax.text(ya[k] - off - 0.16, hia[k] + 0.010, "SOC 2010 releases only",
            color=ACCENT, fontsize=ANNOT, ha="right", va="bottom")
    ax.text(span[1], 0.24, "with SOC 2020 releases\njoined by code",
            color=GREY, fontsize=ANNOT, ha="right", va="top", linespacing=1.25)

    ax.set_xlim(2013.55, 2023.6)
    ax.set_ylim(ylo, yhi)
    ax.set_xticks(list(range(2014, 2024)))
    ax.set_xlabel("ASHE release (April reference date)")
    ax.set_ylabel("Change in slope of log pay on\n"
                  "automation probability, relative\n"
                  "to 2015 (log points)")

    save_all(fig, os.path.join(HERE, "figD1_classification_join"))
    plt.close(fig)


if __name__ == "__main__":
    main()
