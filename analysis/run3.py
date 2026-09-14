"""Estimation on the rebuilt 2014-2020 SOC 2010 panel, plus the pending analyses.

Writes analysis/locked_numbers_v2.json. Every number the paper reports comes
from this file.
"""
import json, warnings
import numpy as np, pandas as pd, pyfixest as pf
warnings.filterwarnings('ignore')
rng = np.random.default_rng(20260912)

PCT = [10, 20, 25, 30, 40, 60, 70, 75, 80, 90]
out = {}


def load(tag):
    d = pd.read_csv('build/%s_raw.csv' % tag)
    return d[d.year <= 2020].copy()


risk = pd.read_stata('data_work/risk.dta')
risk['soc'] = risk.soc.astype(int)

gross = load('hourly_gross')
exovt = load('hourly_exovt')
hours = load('hours_total')

# ---------------------------------------------------------------- main panel
df = gross[gross['mean'].notna()].merge(risk, on='soc')
df['lnwage'] = np.log(df['mean'])
df['post'] = (df.year >= 2016).astype(int)
df['risk_post'] = df.risk * df.post
df['trend'] = df.year - 2015
df['risk_trend'] = df.risk * df.trend
df['major'] = df.soc // 1000
df['submajor'] = df.soc // 100

occ = df[['soc', 'risk']].drop_duplicates()
out['sample'] = {
    'n_obs': int(len(df)), 'n_occ': int(df.soc.nunique()),
    'years': [int(y) for y in sorted(df.year.unique())],
    'n_by_year': {int(y): int(n) for y, n in df.groupby('year').size().items()},
    'risk_mean_occ': float(occ.risk.mean()), 'risk_sd_occ': float(occ.risk.std()),
    'risk_min': float(occ.risk.min()), 'risk_max': float(occ.risk.max()),
    'risk_median_occ': float(occ.risk.median()),
    'lnw_mean': float(df.lnwage.mean()), 'lnw_sd': float(df.lnwage.std()),
    'wage_mean': float(df['mean'].mean()), 'wage_min': float(df['mean'].min()),
    'wage_max': float(df['mean'].max()), 'share_post': float(df.post.mean()),
    'n_risk_file': int(len(risk)),
}

# ------------------------------------------------- classification break facts
g_all = pd.read_csv('build/hourly_gross_raw.csv')
a20 = g_all[g_all.year == 2020][['soc', 'desc']]
b21 = g_all[g_all.year == 2021][['soc', 'desc']]
mrg = a20.merge(b21, on='soc', suffixes=('_2020', '_2021'))


def norm(s):
    return ' '.join(str(s).lower().replace(',', ' ').split())


mrg['same'] = [norm(x) == norm(y) for x, y in zip(mrg.desc_2020, mrg.desc_2021)]
in_risk = mrg[mrg.soc.isin(set(risk.soc))]
out['classification_break'] = {
    'n_soc10_2020': int(a20.soc.nunique()), 'n_soc20_2021': int(b21.soc.nunique()),
    'n_codes_in_both': int(len(mrg)),
    'n_same_description': int(mrg.same.sum()),
    'n_different_description': int((~mrg.same).sum()),
    'n_codes_in_both_and_risk': int(len(in_risk)),
    'n_different_description_in_risk': int((~in_risk.same).sum()),
    'n_soc20_codes_new': int(len(set(b21.soc) - set(a20.soc))),
    'n_soc10_codes_gone': int(len(set(a20.soc) - set(b21.soc))),
    'examples': [
        {'soc': int(r.soc), 'soc10_2020': r.desc_2020, 'soc20_2021': r.desc_2021}
        for _, r in in_risk[~in_risk.same].head(6).iterrows()
    ],
}


def fit(formula, data, names, weights=None):
    m = pf.feols(formula, data=data, vcov={'CRV1': 'soc'}, weights=weights)
    t = m.tidy()
    r = {k: dict(b=float(t.loc[k, 'Estimate']), se=float(t.loc[k, 'Std. Error']),
                 lo=float(t.loc[k, '2.5%']), hi=float(t.loc[k, '97.5%']),
                 p=float(t.loc[k, 'Pr(>|t|)'])) for k in names}
    r['n'] = int(m._N); r['nclus'] = int(data.soc.nunique())
    r['r2_within'] = float(m._r2_within)
    return r


# ------------------------------------------------------------------ baseline
out['baseline'] = fit('lnwage ~ risk_post | soc + year', df, ['risk_post'])
sd = out['sample']['risk_sd_occ']
out['baseline']['effect_1sd'] = out['baseline']['risk_post']['b'] * sd
out['baseline']['effect_1sd_pct'] = (np.exp(out['baseline']['risk_post']['b'] * sd) - 1) * 100

cnt = df.groupby('soc').size(); bal = cnt[cnt == 7].index
out['balanced'] = fit('lnwage ~ risk_post | soc + year', df[df.soc.isin(bal)], ['risk_post'])
out['balanced']['n_occ_balanced'] = int(len(bal))
out['pre_covid_2014_19'] = fit('lnwage ~ risk_post | soc + year', df[df.year <= 2019], ['risk_post'])

# -------------------------------------------------------------- event study
for y in [2014] + list(range(2016, 2021)):
    df['rk_%d' % y] = df.risk * (df.year == y)
terms = ' + '.join('rk_%d' % y for y in [2014] + list(range(2016, 2021)))
r = fit('lnwage ~ %s | soc + year' % terms, df, ['rk_%d' % y for y in [2014] + list(range(2016, 2021))])
out['event_study'] = {int(k.split('_')[1]): v for k, v in r.items() if k.startswith('rk_')}
out['event_study'][2015] = dict(b=0.0, se=0.0, lo=0.0, hi=0.0, p=None)
out['event_study_n'] = r['n']; out['event_study_nclus'] = r['nclus']

rb = fit('lnwage ~ %s | soc + year' % terms, df[df.soc.isin(bal)],
         ['rk_%d' % y for y in [2014] + list(range(2016, 2021))])
out['event_study_balanced'] = {int(k.split('_')[1]): v for k, v in rb.items() if k.startswith('rk_')}
out['event_study_balanced'][2015] = dict(b=0.0, se=0.0, lo=0.0, hi=0.0, p=None)

# --------------------------------------------------------------- trend/break
out['trend_break'] = {
    'y2014_2020_trend_only': fit('lnwage ~ risk_trend | soc + year', df, ['risk_trend']),
    'y2014_2020': fit('lnwage ~ risk_trend + risk_post | soc + year', df, ['risk_trend', 'risk_post']),
    'y2014_2019_trend_only': fit('lnwage ~ risk_trend | soc + year', df[df.year <= 2019], ['risk_trend']),
    'y2014_2019': fit('lnwage ~ risk_trend + risk_post | soc + year', df[df.year <= 2019],
                      ['risk_trend', 'risk_post']),
}

# ------------------------------------------------------- NLW exposure, 2015
NLW = 7.20
p15 = gross[gross.year == 2015].set_index('soc')
pcols = ['p%d' % p for p in PCT]


def share_below(row, thr=NLW):
    xs, ys = [], []
    for p in PCT:
        v = row.get('p%d' % p, np.nan)
        if pd.notna(v):
            xs.append(float(v)); ys.append(float(p))
    med = row.get('median', np.nan)
    if pd.notna(med):
        xs.append(float(med)); ys.append(50.0)
    if len(xs) < 3:
        return np.nan
    o = np.argsort(xs); xs = np.array(xs)[o]; ys = np.array(ys)[o]
    if thr <= xs[0]:
        # extrapolate below the lowest published percentile with the slope of
        # the lowest available segment, and clamp at zero
        slope = (ys[1] - ys[0]) / (xs[1] - xs[0]) if xs[1] > xs[0] else 0.0
        return float(max(0.0, ys[0] - slope * (xs[0] - thr)))
    if thr >= xs[-1]:
        return float(ys[-1])
    return float(np.interp(thr, xs, ys))


p15 = p15.assign(nlw_share=p15.apply(share_below, axis=1) / 100.0)
p15['kaitz'] = NLW / p15['median']
expo = p15[['nlw_share', 'kaitz', 'jobs', 'mean', 'median']].rename(
    columns={'jobs': 'jobs15', 'mean': 'mean15', 'median': 'median15'})
d2 = df[df.year >= 2016].merge(expo, left_on='soc', right_index=True, how='inner')
# predetermined 2015 exposure; estimation uses 2016 onward plus the 2015 base year
d2 = df.merge(expo, left_on='soc', right_index=True, how='inner')
d2 = d2[d2.nlw_share.notna()]
d2['nlw_c'] = d2.nlw_share - d2.nlw_share.mean()
d2['post_nlw'] = d2.post * d2.nlw_c
d2['rp_nlw'] = d2.risk_post * d2.nlw_c
d2['kaitz_c'] = d2.kaitz - d2.kaitz.mean()
d2['post_kaitz'] = d2.post * d2.kaitz_c
d2['rp_kaitz'] = d2.risk_post * d2.kaitz_c

occ2 = d2[['soc', 'risk', 'nlw_share', 'kaitz', 'mean15']].drop_duplicates()
out['nlw_exposure'] = {
    'threshold': NLW,
    'n_occ': int(len(occ2)),
    'share_mean': float(occ2.nlw_share.mean()), 'share_sd': float(occ2.nlw_share.std()),
    'share_p10': float(occ2.nlw_share.quantile(.1)), 'share_p90': float(occ2.nlw_share.quantile(.9)),
    'corr_share_risk': float(occ2.nlw_share.corr(occ2.risk)),
    'corr_share_lnmean15': float(occ2.nlw_share.corr(np.log(occ2.mean15))),
    'corr_kaitz_risk': float(occ2.kaitz.corr(occ2.risk)),
    'n_occ_share_gt_10pct': int((occ2.nlw_share > 0.10).sum()),
    'risk_mean_share_gt_10pct': float(occ2.loc[occ2.nlw_share > 0.10, 'risk'].mean()),
    'risk_mean_share_le_10pct': float(occ2.loc[occ2.nlw_share <= 0.10, 'risk'].mean()),
}
out['nlw_models'] = {
    'risk_only': fit('lnwage ~ risk_post | soc + year', d2, ['risk_post']),
    'plus_nlw': fit('lnwage ~ risk_post + post_nlw | soc + year', d2, ['risk_post', 'post_nlw']),
    'triple': fit('lnwage ~ risk_post + post_nlw + rp_nlw | soc + year', d2,
                  ['risk_post', 'post_nlw', 'rp_nlw']),
    'plus_kaitz': fit('lnwage ~ risk_post + post_kaitz | soc + year', d2, ['risk_post', 'post_kaitz']),
    'triple_kaitz': fit('lnwage ~ risk_post + post_kaitz + rp_kaitz | soc + year', d2,
                        ['risk_post', 'post_kaitz', 'rp_kaitz']),
}
# event study with NLW exposure controlled
for y in [2014] + list(range(2016, 2021)):
    d2['rk_%d' % y] = d2.risk * (d2.year == y)
    d2['nl_%d' % y] = d2.nlw_c * (d2.year == y)
t2 = ' + '.join(['rk_%d' % y for y in [2014] + list(range(2016, 2021))] +
                ['nl_%d' % y for y in [2014] + list(range(2016, 2021))])
r = fit('lnwage ~ %s | soc + year' % t2, d2,
        ['rk_%d' % y for y in [2014] + list(range(2016, 2021))])
out['event_study_nlw_controlled'] = {int(k.split('_')[1]): v for k, v in r.items() if k.startswith('rk_')}
out['event_study_nlw_controlled'][2015] = dict(b=0.0, se=0.0, lo=0.0, hi=0.0, p=None)
out['event_study_nlw_controlled_n'] = r['n']

# --------------------------------------------------------- employment weights
dw = df.merge(expo[['jobs15']], left_on='soc', right_index=True, how='inner')
dw = dw[dw.jobs15.notna() & (dw.jobs15 > 0)]
out['weights'] = {
    'n_occ_with_jobs15': int(dw.soc.nunique()),
    'unweighted_same_sample': fit('lnwage ~ risk_post | soc + year', dw, ['risk_post']),
    'weighted': fit('lnwage ~ risk_post | soc + year', dw, ['risk_post'], weights='jobs15'),
}
for y in [2014] + list(range(2016, 2021)):
    dw['rk_%d' % y] = dw.risk * (dw.year == y)
r = fit('lnwage ~ %s | soc + year' % terms, dw,
        ['rk_%d' % y for y in [2014] + list(range(2016, 2021))], weights='jobs15')
out['event_study_weighted'] = {int(k.split('_')[1]): v for k, v in r.items() if k.startswith('rk_')}
out['event_study_weighted'][2015] = dict(b=0.0, se=0.0, lo=0.0, hi=0.0, p=None)

# -------------------------------------------------------- alternative outcomes
alt = {}
med = gross[gross['median'].notna()].merge(risk, on='soc')
med['y'] = np.log(med['median']); med['post'] = (med.year >= 2016).astype(int)
med['risk_post'] = med.risk * med.post; med['trend'] = med.year - 2015
med['risk_trend'] = med.risk * med.trend
alt['median_pay'] = fit('y ~ risk_post | soc + year', med, ['risk_post'])
alt['median_pay_trend'] = fit('y ~ risk_trend + risk_post | soc + year', med, ['risk_trend', 'risk_post'])

ex = exovt[exovt['mean'].notna()].merge(risk, on='soc')
ex['y'] = np.log(ex['mean']); ex['post'] = (ex.year >= 2016).astype(int)
ex['risk_post'] = ex.risk * ex.post
alt['hourly_excl_overtime'] = fit('y ~ risk_post | soc + year', ex, ['risk_post'])

jb = gross[gross['jobs'].notna() & (gross['jobs'] > 0)].merge(risk, on='soc')
jb['y'] = np.log(jb['jobs']); jb['post'] = (jb.year >= 2016).astype(int)
jb['risk_post'] = jb.risk * jb.post; jb['trend'] = jb.year - 2015
jb['risk_trend'] = jb.risk * jb.trend
alt['log_jobs'] = fit('y ~ risk_post | soc + year', jb, ['risk_post'])
alt['log_jobs_trend'] = fit('y ~ risk_trend + risk_post | soc + year', jb, ['risk_trend', 'risk_post'])
for y in [2014] + list(range(2016, 2021)):
    jb['rk_%d' % y] = jb.risk * (jb.year == y)
r = fit('y ~ %s | soc + year' % terms, jb, ['rk_%d' % y for y in [2014] + list(range(2016, 2021))])
out['event_study_jobs'] = {int(k.split('_')[1]): v for k, v in r.items() if k.startswith('rk_')}
out['event_study_jobs'][2015] = dict(b=0.0, se=0.0, lo=0.0, hi=0.0, p=None)

hr = hours[hours['mean'].notna()].merge(risk, on='soc')
hr['y'] = np.log(hr['mean']); hr['post'] = (hr.year >= 2016).astype(int)
hr['risk_post'] = hr.risk * hr.post
alt['log_hours'] = fit('y ~ risk_post | soc + year', hr, ['risk_post'])
out['alt_outcomes'] = alt

# ----------------------------------------------------- baseline-pay controls
w14 = df[df.year == 2014].set_index('soc')[['lnwage']].rename(columns={'lnwage': 'lnw14'})
d3 = df[df.year >= 2015].merge(w14, left_on='soc', right_index=True, how='inner')
d3['c'] = d3.lnw14 - d3.lnw14.mean()
d3['post_c'] = d3.post * d3.c; d3['rp_c'] = d3.risk_post * d3.c
out['het_baseline_pay'] = {
    'corr_risk_lnw14': float(d3[['soc', 'risk', 'lnw14']].drop_duplicates()[['risk', 'lnw14']].corr().iloc[0, 1]),
    'risk_only': fit('lnwage ~ risk_post | soc + year', d3, ['risk_post']),
    'plus_pay': fit('lnwage ~ risk_post + post_c | soc + year', d3, ['risk_post', 'post_c']),
    'triple': fit('lnwage ~ risk_post + post_c + rp_c | soc + year', d3, ['risk_post', 'post_c', 'rp_c']),
}
d3['wt'] = pd.qcut(d3.lnw14, 3, labels=[1, 2, 3])
out['pay_terciles'] = {}
for k in [1, 2, 3]:
    dd = d3[d3.wt == k]
    rr = fit('lnwage ~ risk_post | soc + year', dd, ['risk_post'])
    rr['w14_min'] = float(np.exp(dd.lnw14.min())); rr['w14_max'] = float(np.exp(dd.lnw14.max()))
    out['pay_terciles'][int(k)] = rr

out['exclude_low_2015'] = {}
d4 = df.merge(expo[['mean15']], left_on='soc', right_index=True, how='inner')
for cut in [8, 9, 10, 11, 12]:
    sub = d4[d4.mean15 >= cut]
    out['exclude_low_2015'][cut] = fit('lnwage ~ risk_post | soc + year', sub, ['risk_post'])

# ---------------------------------------------------------------- robustness
rob = {}
med_r = occ.risk.median(); df['high'] = (df.risk > med_r).astype(int)
df['high_post'] = df.high * df.post
rob['binary_above_median'] = fit('lnwage ~ high_post | soc + year', df, ['high_post'])
q = occ.risk.quantile([1 / 3, 2 / 3]).values
df['ter'] = np.where(df.risk <= q[0], 1, np.where(df.risk <= q[1], 2, 3))
df['t2_post'] = (df.ter == 2).astype(int) * df.post
df['t3_post'] = (df.ter == 3).astype(int) * df.post
rob['terciles'] = fit('lnwage ~ t2_post + t3_post | soc + year', df, ['t2_post', 't3_post'])
out['tercile_cuts'] = [float(x) for x in q]
rob['major_by_year'] = fit('lnwage ~ risk_post | soc + major^year', df, ['risk_post'])
rob['submajor_by_year'] = fit('lnwage ~ risk_post | soc + submajor^year', df, ['risk_post'])
out['n_major'] = int(df.major.nunique()); out['n_submajor'] = int(df.submajor.nunique())
rob['cutoffs'] = {}
for c in [2017, 2018, 2019, 2020]:
    df['rp'] = df.risk * (df.year >= c)
    rob['cutoffs'][c] = fit('lnwage ~ rp | soc + year', df, ['rp'])
df['rp'] = df.risk * (df.year >= 2018)
rob['placebo_2018_within_2014_19'] = fit('lnwage ~ rp | soc + year', df[df.year <= 2019], ['rp'])
df['rp'] = df.risk * (df.year >= 2017)
rob['placebo_2017_within_2014_19'] = fit('lnwage ~ rp | soc + year', df[df.year <= 2019], ['rp'])
out['robustness'] = rob

# --------------------------------------------------------------- permutation
base_b = out['baseline']['risk_post']['b']
occ_idx = occ.set_index('soc').risk
B = 2000; betas = np.empty(B)
d = df[['soc', 'year', 'lnwage', 'post']].copy()
for b in range(B):
    perm = pd.Series(rng.permutation(occ_idx.values), index=occ_idx.index)
    d['rp'] = d.soc.map(perm) * d.post
    betas[b] = pf.feols('lnwage ~ rp | soc + year', data=d, vcov='iid').coef()['rp']
out['permutation'] = {'B': B, 'p_two_sided': float((np.abs(betas) >= abs(base_b)).mean()),
                      'perm_sd': float(betas.std()), 'perm_max_abs': float(np.abs(betas).max())}

# ----------------------------------------------------- contaminated full panel
gg = pd.read_csv('build/hourly_gross_raw.csv')
gg = gg[gg['mean'].notna()].merge(risk, on='soc')
gg['lnwage'] = np.log(gg['mean']); gg['post'] = (gg.year >= 2016).astype(int)
gg['risk_post'] = gg.risk * gg.post
out['contaminated_full_panel'] = fit('lnwage ~ risk_post | soc + year', gg, ['risk_post'])
for y in [2014] + list(range(2016, 2024)):
    gg['rk_%d' % y] = gg.risk * (gg.year == y)
tt = ' + '.join('rk_%d' % y for y in [2014] + list(range(2016, 2024)))
r = fit('lnwage ~ %s | soc + year' % tt, gg, ['rk_%d' % y for y in [2014] + list(range(2016, 2024))])
out['event_study_contaminated'] = {int(k.split('_')[1]): v for k, v in r.items() if k.startswith('rk_')}
out['event_study_contaminated'][2015] = dict(b=0.0, se=0.0, lo=0.0, hi=0.0, p=None)

# ----------------------------------------------------------- descriptive series
import statsmodels.api as sm
out['gradient_by_year'] = {}
for y in sorted(df.year.unique()):
    s = df[df.year == y]
    o = sm.OLS(s.lnwage, sm.add_constant(s.risk)).fit(cov_type='HC1')
    out['gradient_by_year'][int(y)] = {'slope': float(o.params['risk']), 'se': float(o.bse['risk']),
                                       'n': int(len(s))}
out['trend_series'] = {int(y): {int(h): float(v) for h, v in s.items()}
                       for y, s in df.groupby('year').apply(lambda x: x.groupby('high').lnwage.mean()).iterrows()}

json.dump(out, open('analysis/locked_numbers_v2.json', 'w'), indent=1, default=float)
print('written. baseline', out['baseline']['risk_post'])

# --------------------------------------------- employment conditioned on floor
def _employment_floor():
    j = gross[gross['jobs'].notna() & (gross['jobs'] > 0)].merge(risk, on='soc')
    j['y'] = np.log(j['jobs']); j['post'] = (j.year >= 2016).astype(int)
    j['risk_post'] = j.risk * j.post
    c = j.groupby('soc').size(); b = c[c == 7].index
    j = j[j.soc.isin(b)].merge(expo[['nlw_share']], left_on='soc', right_index=True, how='inner')
    j = j[j.nlw_share.notna()]
    j['nlw_c'] = j.nlw_share - j.nlw_share.mean()
    j['post_nlw'] = j.post * j.nlw_c
    j['rp_nlw'] = j.risk_post * j.nlw_c
    m = {'risk_only': fit('y ~ risk_post | soc + year', j, ['risk_post']),
         'plus_nlw': fit('y ~ risk_post + post_nlw | soc + year', j, ['risk_post', 'post_nlw']),
         'triple': fit('y ~ risk_post + post_nlw + rp_nlw | soc + year', j,
                       ['risk_post', 'post_nlw', 'rp_nlw'])}
    for y in [2014] + list(range(2016, 2021)):
        j['rk_%d' % y] = j.risk * (j.year == y)
        j['nl_%d' % y] = j.nlw_c * (j.year == y)
    tt = ' + '.join(['rk_%d' % y for y in [2014] + list(range(2016, 2021))] +
                    ['nl_%d' % y for y in [2014] + list(range(2016, 2021))])
    r = fit('y ~ %s | soc + year' % tt, j, ['rk_%d' % y for y in [2014] + list(range(2016, 2021))])
    es = {int(k.split('_')[1]): v for k, v in r.items() if k.startswith('rk_')}
    es[2015] = dict(b=0.0, se=0.0, lo=0.0, hi=0.0, p=None)
    return m, es


def _employment_core():
    j = gross[gross['jobs'].notna() & (gross['jobs'] > 0)].merge(risk, on='soc')
    j['y'] = np.log(j['jobs']); j['post'] = (j.year >= 2016).astype(int)
    j['risk_post'] = j.risk * j.post
    c = j.groupby('soc').size(); b = c[c == 7].index
    jb = j[j.soc.isin(b)]
    m = {'balanced': fit('y ~ risk_post | soc + year', jb, ['risk_post']),
         'balanced_2014_19': fit('y ~ risk_post | soc + year', jb[jb.year <= 2019], ['risk_post']),
         'n_occ_balanced': int(len(b)), 'n_occ_any': int(j.soc.nunique())}
    for y in [2014] + list(range(2016, 2021)):
        jb = jb.assign(**{'rk_%d' % y: jb.risk * (jb.year == y)})
    tt = ' + '.join('rk_%d' % y for y in [2014] + list(range(2016, 2021)))
    r = fit('y ~ %s | soc + year' % tt, jb, ['rk_%d' % y for y in [2014] + list(range(2016, 2021))])
    es = {int(k.split('_')[1]): v for k, v in r.items() if k.startswith('rk_')}
    es[2015] = dict(b=0.0, se=0.0, lo=0.0, hi=0.0, p=None)
    m['event_study_balanced'] = es
    tot = jb.groupby('year').jobs.sum()
    m['total_jobs_thousands'] = {int(y): float(v) for y, v in tot.items()}
    med_r = occ.risk.median()
    jb = jb.assign(high=(jb.risk > med_r).astype(int))
    sh = jb.groupby(['year', 'high']).jobs.sum().unstack()
    m['share_jobs_high_risk'] = {int(y): float(sh.loc[y, 1] / (sh.loc[y, 0] + sh.loc[y, 1])) for y in sh.index}
    return m


out['employment'] = _employment_core()
_m, _es = _employment_floor()
out['employment']['nlw_models'] = _m
out['employment']['event_study_nlw_controlled'] = _es
out['employment']['effect_1sd_balanced'] = out['employment']['balanced']['risk_post']['b'] * out['sample']['risk_sd_occ']
out['employment']['effect_1sd_balanced_pct'] = (np.exp(out['employment']['effect_1sd_balanced']) - 1) * 100
out['pay_effect_1sd_pct'] = out['baseline']['effect_1sd_pct']
json.dump(out, open('analysis/locked_numbers_v2.json', 'w'), indent=1, default=float)
print('employment-floor block appended')

# ------------------------------------------------- descriptives for jobs/hours
def _desc_blocks():
    j = gross[gross['jobs'].notna() & (gross['jobs'] > 0)].merge(risk, on='soc')
    h = hours[hours['mean'].notna()].merge(risk, on='soc')
    jd = {'n': int(len(j)), 'n_obs': int(len(j)), 'n_occ': int(j.soc.nunique()),
          'mean_jobs_thousands': float(j['jobs'].mean()),
          'mean': float(j['jobs'].mean()), 'sd': float(j['jobs'].std()),
          'min': float(j['jobs'].min()), 'max': float(j['jobs'].max()),
          'ln_mean': float(np.log(j['jobs']).mean()), 'ln_sd': float(np.log(j['jobs']).std())}
    hd = {'n': int(len(h)), 'n_obs': int(len(h)), 'n_occ': int(h.soc.nunique()),
          'mean_hours': float(h['mean'].mean()),
          'mean': float(h['mean'].mean()), 'sd': float(h['mean'].std()),
          'min': float(h['mean'].min()), 'max': float(h['mean'].max())}
    h = h.copy()
    h['y'] = np.log(h['mean']); h['post'] = (h.year >= 2016).astype(int)
    for y in [2014] + list(range(2016, 2021)):
        h['rk_%d' % y] = h.risk * (h.year == y)
    tt = ' + '.join('rk_%d' % y for y in [2014] + list(range(2016, 2021)))
    r = fit('y ~ %s | soc + year' % tt, h, ['rk_%d' % y for y in [2014] + list(range(2016, 2021))])
    es = {int(k.split('_')[1]): v for k, v in r.items() if k.startswith('rk_')}
    es[2015] = dict(b=0.0, se=0.0, lo=0.0, hi=0.0, p=None)
    return jd, hd, es


out['jobs_desc'], out['hours_desc'], out['event_study_hours'] = _desc_blocks()
json.dump(out, open('analysis/locked_numbers_v2.json', 'w'), indent=1, default=float)
print('descriptive blocks appended')

# ------------------------------------- employment trend/break and weighted
def _employment_extras():
    j = gross[gross['jobs'].notna() & (gross['jobs'] > 0)].merge(risk, on='soc')
    j['y'] = np.log(j['jobs']); j['post'] = (j.year >= 2016).astype(int)
    j['risk_post'] = j.risk * j.post; j['trend'] = j.year - 2015
    j['risk_trend'] = j.risk * j.trend
    c = j.groupby('soc').size(); b = c[c == 7].index
    jb = j[j.soc.isin(b)]
    res = {
        'trend_break_balanced': fit('y ~ risk_trend + risk_post | soc + year', jb,
                                    ['risk_trend', 'risk_post']),
        'trend_break_balanced_2014_19': fit('y ~ risk_trend + risk_post | soc + year',
                                            jb[jb.year <= 2019], ['risk_trend', 'risk_post']),
    }
    jw = jb.merge(expo[['jobs15']], left_on='soc', right_index=True, how='inner')
    jw = jw[jw.jobs15.notna() & (jw.jobs15 > 0)]
    res['weighted_balanced'] = fit('y ~ risk_post | soc + year', jw, ['risk_post'], weights='jobs15')
    res['nlw_controls'] = out['employment']['nlw_models']
    return res


out['employment'].update(_employment_extras())
json.dump(out, open('analysis/locked_numbers_v2.json', 'w'), indent=1, default=float)
print('employment extras appended')

# ------------------------------------------- raw counts behind the employment result
def _raw_counts():
    j = gross[gross['jobs'].notna() & (gross['jobs'] > 0)].merge(risk, on='soc')
    c = j.groupby('soc').size(); b = c[c == 7].index
    jb = j[j.soc.isin(b)].copy()
    q = occ.risk.quantile([1 / 3, 2 / 3]).values
    jb['rt'] = np.where(jb.risk <= q[0], 1, np.where(jb.risk <= q[1], 2, 3))
    g15 = jb[jb.year == 2015].groupby('rt').jobs.sum()
    g19 = jb[jb.year == 2019].groupby('rt').jobs.sum()
    growth = {int(k): float(np.log(g19[k]) - np.log(g15[k])) for k in [1, 2, 3]}
    w = gross[gross['mean'].notna()].merge(risk, on='soc')
    a = w[w.year == 2015].set_index('soc'); bb = w[w.year == 2019].set_index('soc')
    j15 = j[j.year == 2015].set_index('soc'); j19 = j[j.year == 2019].set_index('soc')
    ix = a.index.intersection(bb.index).intersection(j15.index).intersection(j19.index)
    dpay = np.log(bb.loc[ix, 'mean']) - np.log(a.loc[ix, 'mean'])
    djob = np.log(j19.loc[ix, 'jobs']) - np.log(j15.loc[ix, 'jobs'])
    return {'employment_growth_2015_19_by_risk_tercile': growth,
            'n_occ_both_series': int(len(ix)),
            'corr_djobs_risk': float(djob.corr(a.loc[ix, 'risk'])),
            'corr_dpay_risk': float(dpay.corr(a.loc[ix, 'risk'])),
            'corr_dpay_djobs': float(dpay.corr(djob))}


out['raw_counts'] = _raw_counts()
json.dump(out, open('analysis/locked_numbers_v2.json', 'w'), indent=1, default=float)
print('raw counts appended')
