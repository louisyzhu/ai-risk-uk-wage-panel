# Font and conventions, round three

Helvetica is installed on the rendering machine and is the embedded font in all
nine image files, with Arial as the coded fallback in `paperstyle.py`. Greek
letters do not appear in this set, so the sans-serif maths font that Figure 1
needed goes unused here.

Nothing in the first-round conventions note changed. The reference period still
carries no interval, a thin rule still marks zero, a dashed rule still marks the
boundary at 2015 and 2016, the axis labels still state the unit, no legend box
appears, and colour still carries one distinction with grey taking every
secondary series.

Two notes on execution. Figure 3 shortened its vertical axis label to one line,
which renders 2.95 in tall in a 2.62 in panel, so the label overruns the panel by
0.33 in without clipping. Figures 2 and D.1 set that label over three lines,
1.66 in tall, because one line ran past the top of the canvas and clipped.
