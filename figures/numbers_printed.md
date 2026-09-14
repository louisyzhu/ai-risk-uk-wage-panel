# Numerals rendered on each figure, with the source of each

One line per figure, listing every numeral that reaches the canvas so that
Claude can check each against the locked sheet. Figure 1 is unchanged from round
one and stays in `figures/`, where its own inventory line still holds. The `p`
column of all four data files goes unread, because no figure marks significance,
and each script says so in its reader.

Figure 2 prints the vertical tick values -0.10, -0.05, 0.00, 0.05, 0.10, 0.15, 0.20 and 0.25 and the
horizontal tick values 2014 to 2020 as axis scale, the fourteen coefficients and
interval bounds it draws from the `b`, `lo` and `hi` columns of
`v2_fig_event_pay.csv` and `v2_fig_event_pay_nlw.csv`, the occupation counts 366
and 347 inside the two direct labels, and the years 2016 and 2015 inside the
post-2016 label and the vertical axis label. The two counts are the only numerals
on the figure that the data files do not carry; the script declares them at the
top as constants, taken from the occupation rows of Table 4 columns (1) and (3)
of the draft.

Figure 3 prints the vertical tick values -0.10, -0.05, 0.00, 0.05, 0.10, 0.15, 0.20 in panel A and
-1.0, -0.8, -0.6, -0.4, -0.2, 0.0, 0.2 in panel B and the horizontal tick
values 2014, 2016, 2018 and 2020 as axis scale, the fourteen coefficients and
interval bounds it draws from the `b`, `lo` and `hi` columns of
`v2_fig_event_pay.csv` and `v2_fig_event_jobs.csv`, the occupation counts 366 and
309 inside the two bold panel titles, and the year 2016 inside the post-2016
label of each panel. The two counts come from the panel titles the brief
specifies, which match the occupation rows of Table 4 column (1) and Table 8
column (1); the data files carry no count and none was sought.

Figure D.1 prints the vertical tick values 0.0, 0.2, 0.4, 0.6, 0.8 and the horizontal
tick values 2014 to 2023 as axis scale, the twenty coefficients and interval
bounds it draws from the `b`, `lo` and `hi` columns of `v2_fig_event_pay.csv` and
`v2_fig_event_contaminated.csv`, the value 0.0031 which the script computes as
the largest absolute difference between the two `b` columns across the seven
years both files share, the year 2021 which the script takes as the first year
present in the contaminated file alone, the counts 125 and 261 inside the shading
label, and the years 2016, 2015, 2010 and 2020 inside the post-2016 label, the
vertical axis label and the two classification labels. The largest difference
falls in 2020 and its unrounded value is 0.003080, so the printed 0.0031 states a
bound the data respect at four decimal places.
