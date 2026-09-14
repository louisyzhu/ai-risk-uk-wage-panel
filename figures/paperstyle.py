"""Shared style for the three figures of the automation-risk wage paper.

House rules applied here, so that each figure script carries only its own
content. Sans-serif type throughout, Okabe-Ito accent, vector output, and a
three-step font ladder mapped to role.
"""

import matplotlib as mpl
import matplotlib.pyplot as plt
import matplotlib.font_manager as fm

# Okabe-Ito. Blue carries the claim in every figure; vermillion is reserved for
# a second highlighted element and is used only where one is needed.
ACCENT = "#0072B2"
VERMILLION = "#D55E00"
GREY = "#999999"
BLACK = "#000000"
SHADE = "#E8E8E8"

# Role-mapped ladder: base for titles, axis labels and direct labels;
# one step down for annotations; one further for tick labels.
BASE, ANNOT, TICK = 9.0, 8.0, 7.0

TEXT_WIDTH_IN = 6.3


def sans_family():
    """Return Helvetica if the system provides it, otherwise Arial."""
    installed = {f.name for f in fm.fontManager.ttflist}
    for candidate in ("Helvetica", "Arial"):
        if candidate in installed:
            return candidate
    raise RuntimeError("neither Helvetica nor Arial is installed")


def apply_style():
    family = sans_family()
    mpl.rcParams.update({
        "font.family": "sans-serif",
        "font.sans-serif": [family, "Arial", "DejaVu Sans"],
        "font.size": BASE,
        "axes.titlesize": BASE,
        "axes.labelsize": BASE,
        "xtick.labelsize": TICK,
        "ytick.labelsize": TICK,
        "legend.fontsize": ANNOT,
        # Greek letters are drawn from a sans-serif maths set so that no serif
        # glyph enters the figure.
        "mathtext.fontset": "stixsans",
        "axes.spines.top": False,
        "axes.spines.right": False,
        "axes.linewidth": 0.7,
        "xtick.direction": "out",
        "ytick.direction": "out",
        "xtick.major.size": 3.0,
        "ytick.major.size": 3.0,
        "xtick.major.width": 0.7,
        "ytick.major.width": 0.7,
        "lines.solid_capstyle": "round",
        "savefig.dpi": 300,
        "savefig.bbox": "tight",
        "savefig.pad_inches": 0.02,
        "pdf.fonttype": 42,
        "ps.fonttype": 42,
        "svg.fonttype": "none",
    })
    return family


def save_all(fig, stem):
    """Write the same figure to PDF, SVG and PNG at 300 dpi."""
    paths = []
    for ext in ("pdf", "svg", "png"):
        path = f"{stem}.{ext}"
        fig.savefig(path, format=ext, dpi=300)
        paths.append(path)
    return paths
