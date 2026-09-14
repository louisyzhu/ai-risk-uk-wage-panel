"""Rebuild the occupation-year panel from the raw ASHE Table 14 workbooks.

Reads the 'All' sheet of the named table in each release, keeps four-digit
occupation rows, and writes a long panel with pay, jobs, hours and percentiles.
Suppression markers (x, .., :, -) become missing.
"""
import glob, os, re, sys
import pandas as pd, numpy as np

RAW = 'raw/ex'
PCTL = ['10.0', '20.0', '25.0', '30.0', '40.0', '60.0', '70.0', '75.0', '80.0', '90.0']
COLS = ['desc', 'code', 'jobs', 'median', 'med_chg', 'mean', 'mean_chg'] + ['p' + p.split('.')[0] for p in PCTL]
MISSING = {'x', '..', ':', '-', '', 'nan', 'none'}

YEAR_DIR = {
    2014: 'rft-14(1)', 2015: 'table142015revised', 2016: 'table142016revised',
    2017: 'table142017revised', 2018: 'table142018revised', 2019: 'table142019revised',
    2020: 'table142020revised', 2021: 'ashetable142021revised',
    2022: 'ashetable142022revised', 2023: 'ashetable142023revised',
}


def num(v):
    if v is None:
        return np.nan
    s = str(v).strip()
    if s.lower() in MISSING:
        return np.nan
    s = s.replace(',', '')
    try:
        return float(s)
    except ValueError:
        return np.nan


def find_book(year, table):
    d = os.path.join(RAW, YEAR_DIR[year])
    hits = [f for f in glob.glob(os.path.join(d, '*'))
            if re.search(r'Table %s\b' % re.escape(table), os.path.basename(f))
            and '__MACOSX' not in f and ' CV' not in os.path.basename(f)]
    if len(hits) != 1:
        raise SystemExit('year %d table %s -> %d matches: %s' % (year, table, len(hits), hits))
    return hits[0]


def read_all_sheet(path):
    """Return the 'All' sheet as a list of row lists, for .xls or .xlsx."""
    if path.lower().endswith('.xlsx'):
        import openpyxl
        wb = openpyxl.load_workbook(path, data_only=True, read_only=True)
        sh = wb['All']
        return [[c for c in row] for row in sh.values]
    import xlrd
    sh = xlrd.open_workbook(path).sheet_by_name('All')
    return [[sh.cell_value(r, c) for c in range(sh.ncols)] for r in range(sh.nrows)]


def header_row(rows):
    for i, row in enumerate(rows[:15]):
        vals = [str(v).strip().lower() for v in row[:3]]
        if vals[:2] == ['description', 'code']:
            return i
    raise SystemExit('no header row found')


def parse(year, table):
    path = find_book(year, table)
    rows = read_all_sheet(path)
    h = header_row(rows)
    hdr = [str(v).strip() for v in rows[h]]
    # locate the percentile block by its header labels
    idx = {}
    for want in PCTL:
        if want in hdr:
            idx[want] = hdr.index(want)
    out = []
    for row in rows[h + 1:]:
        code = str(row[1]).strip() if len(row) > 1 and row[1] is not None else ''
        code = code.split('.')[0]
        if not re.fullmatch(r'\d{4}', code):
            continue
        rec = {
            'year': year, 'soc': int(code),
            'desc': str(row[0]).strip(),
            'jobs': num(row[2]), 'median': num(row[3]), 'mean': num(row[5]),
        }
        for want in PCTL:
            rec['p' + want.split('.')[0]] = num(row[idx[want]]) if want in idx else np.nan
        out.append(rec)
    df = pd.DataFrame(out)
    if df.soc.duplicated().any():
        dup = df.soc[df.soc.duplicated()].tolist()
        raise SystemExit('duplicate codes in %d %s: %s' % (year, table, dup[:5]))
    return df, os.path.basename(path)


def build(table, tag):
    frames, provenance = [], []
    for year in sorted(YEAR_DIR):
        df, name = parse(year, table)
        df['basis'] = 'SOC20' if 'SOC20' in name else 'SOC10'
        frames.append(df)
        provenance.append({'year': year, 'table': table, 'file': name,
                           'basis': df.basis.iloc[0], 'n_four_digit': len(df),
                           'n_mean': int(df['mean'].notna().sum()),
                           'n_median': int(df['median'].notna().sum()),
                           'n_jobs': int(df['jobs'].notna().sum())})
    panel = pd.concat(frames, ignore_index=True)
    panel.to_csv('build/%s_raw.csv' % tag, index=False)
    pd.DataFrame(provenance).to_csv('build/%s_provenance.csv' % tag, index=False)
    return panel, pd.DataFrame(provenance)


if __name__ == '__main__':
    os.makedirs('build', exist_ok=True)
    for table, tag in [('14.5a', 'hourly_gross'), ('14.6a', 'hourly_exovt'), ('14.9a', 'hours_total')]:
        panel, prov = build(table, tag)
        print('==', table, tag, len(panel))
        print(prov.to_string(index=False))
