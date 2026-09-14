"""Export the figure data files from the locked sheet.

Run this after any change to locked_numbers_v2.json so the CSVs cannot drift
from the tables. Every file is written from the same dictionary the tables read.
"""
import json, pandas as pd
o = json.load(open('analysis/locked_numbers_v2.json'))
SPEC = [('v2_fig_event_pay.csv', o['event_study']),
        ('v2_fig_event_pay_nlw.csv', o['event_study_nlw_controlled']),
        ('v2_fig_event_jobs.csv', o['employment']['event_study_balanced']),
        ('v2_fig_event_contaminated.csv', o['event_study_contaminated'])]
for fn, d in SPEC:
    rows = [{'year': int(y), **{k: v for k, v in r.items()}} for y, r in d.items()]
    pd.DataFrame(rows).sort_values('year').to_csv('analysis/' + fn, index=False)
    print('wrote', fn, len(rows), 'rows')
