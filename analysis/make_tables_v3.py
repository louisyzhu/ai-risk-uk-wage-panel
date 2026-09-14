import json, numpy as np, os, csv
o = json.load(open('analysis/locked_numbers_v2.json'))
os.makedirs('paper/tables', exist_ok=True)


def f(x, d=3): return f"{x:.{d}f}"
def cell(r): return f(r['b']), f"({f(r['se'])})"
def ci(r): return f"[{f(r['lo'])}, {f(r['hi'])}]"
def head(sz='footnotesize', pad='4pt'):
    return r"\begin{threeparttable}\%s\setlength{\tabcolsep}{%s}" % (sz, pad)


SE = r"Standard errors clustered by occupation are reported in parentheses."
FE = r"All columns include occupation and release fixed effects."
SRC = r"\item \emph{Source:} ASHE Table 14, 2014--2020 releases, revised editions; ONS (2019) probability of automation."
T = {}
s = o['sample']; YRS = [2014, 2015, 2016, 2017, 2018, 2019, 2020]
ES = YRS

# ------------------------------------------------------------------ Table 1
rows = []
for y in YRS:
    g = o['gradient_by_year'][str(y)]; t = o['trend_series'][str(y)]
    j = o['employment']['share_jobs_high_risk'][str(y)]
    rows.append(f"{y} & {s['n_by_year'][str(y)]} & {t['0']:.3f} & {t['1']:.3f} & {g['slope']:.3f} & ({g['se']:.3f}) & {100*j:.1f} \\\\")
T['sample'] = r"""\begin{table}[!ht]\centering
\caption{The occupation-year panel by release, 2014--2020}\label{tab:sample}
""" + head('footnotesize', '3pt') + r"""
\begin{tabular}{lcccccc}\toprule
 & & \multicolumn{2}{c}{Mean log hourly pay} & \multicolumn{2}{c}{Cross-section gradient} & Share of jobs in \\
\cmidrule(lr){3-4}\cmidrule(lr){5-6}
Release & Occupations & Below-median & Above-median & Slope & (s.e.) & above-median risk (\%) \\ \midrule
""" + "\n".join(rows) + r"""
\bottomrule\end{tabular}
\begin{tablenotes}\footnotesize
\item \emph{Notes:} Each row describes the occupations with a published mean gross hourly pay in that ASHE release on the SOC 2010 basis, of the 366 occupations in the panel. Log pay is the log of nominal mean gross hourly pay. The median automation probability across the 366 occupations is """ + f"{s['risk_median_occ']:.3f}" + r""". The gradient is the slope from a cross-sectional regression of log pay on the automation probability in that release, with heteroskedasticity-consistent standard errors in parentheses. The final column is the share of employee jobs in above-median-risk occupations among the """ + f"{o['employment']['n_occ_balanced']}" + r""" occupations with a published jobs count in all seven releases.
""" + SRC + r"""
\end{tablenotes}\end{threeparttable}\end{table}"""

# ------------------------------------------------------------------ Table 2
nx = o['nlw_exposure']; jd = o['jobs_desc']; hd = o['hours_desc']
T['desc'] = r"""\begin{table}[!ht]\centering
\caption{Descriptive statistics}\label{tab:desc}
""" + head('footnotesize', '3pt') + r"""
\begin{tabular}{lccccc}\toprule
Variable & N & Mean & S.D. & Min & Max \\ \midrule
\multicolumn{6}{l}{\emph{Panel A. Occupation-year cells, 2014--2020}} \\
Log mean gross hourly pay & """ + f"{s['n_obs']:,} & {s['lnw_mean']:.3f} & {s['lnw_sd']:.3f} & {np.log(s['wage_min']):.3f} & {np.log(s['wage_max']):.3f}" + r""" \\
Mean gross hourly pay (\pounds) & """ + f"{s['n_obs']:,} & {s['wage_mean']:.2f} & -- & {s['wage_min']:.2f} & {s['wage_max']:.2f}" + r""" \\
Employee jobs (thousands) & """ + f"{jd['n']:,} & {jd['mean_jobs_thousands']:.1f} & -- & {jd['min']:.0f} & {jd['max']:.0f}" + r""" \\
Mean paid hours per week & """ + f"{hd['n']:,} & {hd['mean_hours']:.1f} & -- & -- & --" + r""" \\
\addlinespace
\multicolumn{6}{l}{\emph{Panel B. Occupation-level attributes, fixed over time}} \\
Automation probability & """ + f"{s['n_occ']} & {s['risk_mean_occ']:.3f} & {s['risk_sd_occ']:.3f} & {s['risk_min']:.3f} & {s['risk_max']:.3f}" + r""" \\
Share of jobs below \pounds 7.20 in 2015 & """ + f"{nx['n_occ']} & {nx['share_mean']:.3f} & {nx['share_sd']:.3f} & 0.000 & --" + r""" \\
\bottomrule\end{tabular}
\begin{tablenotes}\footnotesize
\item \emph{Notes:} Pay is nominal. Jobs and hours are the published occupation totals and means from ASHE Tables 14.5a and 14.9a; the jobs count is published for fewer cells because the ONS suppresses small counts. The automation probability is defined on the SOC 2010 four-digit classification. The share of jobs below \pounds 7.20, the National Living Wage rate of April 2016, is interpolated from the published percentiles of the 2015 release by equation (B1); its tenth and ninetieth percentiles across occupations are """ + f"{nx['share_p10']:.3f} and {nx['share_p90']:.3f}" + r""", and it correlates """ + f"{nx['corr_share_risk']:.2f}" + r""" with the automation probability.
""" + SRC + r"""
\end{tablenotes}\end{threeparttable}\end{table}"""

# ------------------------------------------------------------------ Table 3
b = o['baseline']; bal = o['balanced']; p19 = o['pre_covid_2014_19']
wu = o['weights']['unweighted_same_sample']; ww = o['weights']['weighted']
md = o['alt_outcomes']['median_pay']; ex = o['alt_outcomes']['hourly_excl_overtime']
cols = [('Mean pay', b), ('Balanced', bal), ('2014--19', p19), ('Weighted', ww), ('Median pay', md), ('Excl.\\ overtime', ex)]
T['pay'] = r"""\begin{table}[!ht]\centering
\caption{Post-2016 change in the automation-risk gradient of log hourly pay}\label{tab:pay}
""" + head('scriptsize', '2.5pt') + r"""
\begin{tabular}{l""" + "c" * len(cols) + r"""}\toprule
 & (1) & (2) & (3) & (4) & (5) & (6) \\
 & """ + " & ".join(c[0] for c in cols) + r""" \\ \midrule
Risk $\times$ post-2016 & """ + " & ".join(cell(c[1]['risk_post'])[0] for c in cols) + r""" \\
 & """ + " & ".join(cell(c[1]['risk_post'])[1] for c in cols) + r""" \\
95\% confidence interval & """ + " & ".join(ci(c[1]['risk_post']) for c in cols) + r""" \\ \addlinespace
Occupation-years & """ + " & ".join(f"{c[1]['n']:,}" for c in cols) + r""" \\
Occupations & """ + " & ".join(f"{c[1]['nclus']}" for c in cols) + r""" \\
Within $R^{2}$ & """ + " & ".join(f"{c[1]['r2_within']:.3f}" for c in cols) + r""" \\
\bottomrule\end{tabular}
\begin{tablenotes}\footnotesize
\item \emph{Notes:} The dependent variable is the log of the stated pay measure and the specification is equation (1). """ + FE + r""" """ + SE + r""" Column 2 keeps the """ + f"{bal['n_occ_balanced']}" + r""" occupations with a published mean in all seven releases. Column 4 weights each cell by the occupation's employee jobs in the 2015 release, on the """ + f"{o['weights']['n_occ_with_jobs15']}" + r""" occupations with a published count; the unweighted estimate on that same sample is """ + f"{wu['risk_post']['b']:.3f} ({wu['risk_post']['se']:.3f})" + r""". Column 5 uses the published median of Table 14.5a and column 6 the mean of Table 14.6a. All other columns weight each occupation-year equally.
""" + SRC + r"""
\end{tablenotes}\end{threeparttable}\end{table}"""

# ------------------------------------------------------------------ Table 4
def esc(d, y):
    r = d[str(y)]
    if r['se'] == 0: return '0 (ref.)', ''
    return f(r['b']), f"({f(r['se'])})"
rows = []
for y in ES:
    a = esc(o['event_study'], y); w = esc(o['event_study_weighted'], y); n = esc(o['event_study_nlw_controlled'], y)
    rows.append(f"{y} & {a[0]} & {a[1]} & {w[0]} & {w[1]} & {n[0]} & {n[1]} \\\\")
T['espay'] = r"""\begin{table}[!ht]\centering
\caption{Event-study estimates for log mean hourly pay, relative to 2015}\label{tab:espay}
""" + head('footnotesize', '3pt') + r"""
\begin{tabular}{lcccccc}\toprule
 & \multicolumn{2}{c}{(1) Unweighted} & \multicolumn{2}{c}{(2) Employment-weighted} & \multicolumn{2}{c}{(3) Floor exposure controlled} \\
\cmidrule(lr){2-3}\cmidrule(lr){4-5}\cmidrule(lr){6-7}
Release & $\hat{\beta}_{s}$ & (s.e.) & $\hat{\beta}_{s}$ & (s.e.) & $\hat{\beta}_{s}$ & (s.e.) \\ \midrule
""" + "\n".join(rows) + r"""
\addlinespace
Occupation-years & \multicolumn{2}{c}{""" + f"{o['event_study_n']:,}" + r"""} & \multicolumn{2}{c}{""" + f"{o['weights']['weighted']['n']:,}" + r"""} & \multicolumn{2}{c}{""" + f"{o['event_study_nlw_controlled_n']:,}" + r"""} \\
Occupations & \multicolumn{2}{c}{""" + f"{o['event_study_nclus']}" + r"""} & \multicolumn{2}{c}{""" + f"{o['weights']['n_occ_with_jobs15']}" + r"""} & \multicolumn{2}{c}{""" + f"{o['nlw_exposure']['n_occ']}" + r"""} \\
\bottomrule\end{tabular}
\begin{tablenotes}\footnotesize
\item \emph{Notes:} Estimates of $\beta_{s}$ in equation (2), the interaction between the automation probability and a release indicator, with 2015 omitted. Column 2 weights by 2015 employee jobs. Column 3 adds the interaction between the 2015 share of jobs paid below \pounds 7.20 and each release indicator, so the reported coefficients are net of a floor-exposure path that is free to differ by release. A positive coefficient means the cross-occupation slope of log pay on the probability was less negative in that release than in 2015. """ + FE + r""" """ + SE + r"""
""" + SRC + r"""
\end{tablenotes}\end{threeparttable}\end{table}"""

# ------------------------------------------------------------------ Table 5
tb = o['trend_break']; ej = o['employment']
def tc(d, k): return cell(d[k]) if k in d else ('--', '')
specs = [('Pay', '2014--19', tb['y2014_2019_trend_only']), ('Pay', '2014--19', tb['y2014_2019']),
         ('Pay', '2014--20', tb['y2014_2020_trend_only']), ('Pay', '2014--20', tb['y2014_2020']),
         ('Jobs', '2014--19', ej['trend_break_balanced_2014_19']), ('Jobs', '2014--20', ej['trend_break_balanced'])]
T['trend'] = r"""\begin{table}[!ht]\centering
\caption{Linear trend or break at 2016 in the automation-risk gradient}\label{tab:trend}
""" + head('footnotesize', '3pt') + r"""
\begin{tabular}{lcccccc}\toprule
 & (1) & (2) & (3) & (4) & (5) & (6) \\
Dependent variable & """ + " & ".join(x[0] for x in specs) + r""" \\
Releases & """ + " & ".join(x[1] for x in specs) + r""" \\ \midrule
Risk $\times$ (year $-$ 2015) & """ + " & ".join(tc(x[2], 'risk_trend')[0] for x in specs) + r""" \\
 & """ + " & ".join(tc(x[2], 'risk_trend')[1] for x in specs) + r""" \\
Risk $\times$ post-2016 & """ + " & ".join(tc(x[2], 'risk_post')[0] for x in specs) + r""" \\
 & """ + " & ".join(tc(x[2], 'risk_post')[1] for x in specs) + r""" \\ \addlinespace
Occupation-years & """ + " & ".join(f"{x[2]['n']:,}" for x in specs) + r""" \\
Occupations & """ + " & ".join(f"{x[2]['nclus']}" for x in specs) + r""" \\
\bottomrule\end{tabular}
\begin{tablenotes}\footnotesize
\item \emph{Notes:} Estimates of equation (3). The trend term lets the risk gradient move linearly in calendar time and the break term adds a level shift from 2016. Pay is log mean gross hourly pay on the full panel; jobs is log employee jobs on the balanced panel of """ + f"{ej['n_occ_balanced']}" + r""" occupations with a published count in every release. """ + FE + r""" """ + SE + r"""
""" + SRC + r"""
\end{tablenotes}\end{threeparttable}\end{table}"""

# ------------------------------------------------------------------ Table 6
nm = o['nlw_models']
cols = [('risk_only', ['risk_post']), ('plus_nlw', ['risk_post', 'post_nlw']), ('triple', ['risk_post', 'post_nlw', 'rp_nlw']),
        ('plus_kaitz', ['risk_post', 'post_kaitz']), ('triple_kaitz', ['risk_post', 'post_kaitz', 'rp_kaitz'])]
def hc(k, name):
    d = nm[k[0]]; return cell(d[name]) if name in k[1] else ('', '')
T['nlw'] = r"""\begin{table}[!ht]\centering
\caption{The post-2016 pay gradient conditional on exposure to the National Living Wage}\label{tab:nlw}
""" + head() + r"""
\begin{tabular}{lccccc}\toprule
 & (1) & (2) & (3) & (4) & (5) \\
Exposure measure & None & Share below floor & Share below floor & Kaitz index & Kaitz index \\ \midrule
Risk $\times$ post & """ + " & ".join(hc(c, 'risk_post')[0] for c in cols) + r""" \\
 & """ + " & ".join(hc(c, 'risk_post')[1] for c in cols) + r""" \\
Exposure $\times$ post & """ + " & ".join((hc(c, 'post_nlw')[0] or hc(c, 'post_kaitz')[0]) for c in cols) + r""" \\
 & """ + " & ".join((hc(c, 'post_nlw')[1] or hc(c, 'post_kaitz')[1]) for c in cols) + r""" \\
Risk $\times$ exposure $\times$ post & """ + " & ".join((hc(c, 'rp_nlw')[0] or hc(c, 'rp_kaitz')[0]) for c in cols) + r""" \\
 & """ + " & ".join((hc(c, 'rp_nlw')[1] or hc(c, 'rp_kaitz')[1]) for c in cols) + r""" \\ \addlinespace
Occupation-years & """ + " & ".join(f"{nm[c[0]]['n']:,}" for c in cols) + r""" \\
Occupations & """ + " & ".join(f"{nm[c[0]]['nclus']}" for c in cols) + r""" \\
\bottomrule\end{tabular}
\begin{tablenotes}\footnotesize
\item \emph{Notes:} Estimates of equation (4) on the """ + f"{nm['risk_only']['nclus']}" + r""" occupations for which the 2015 percentiles allow the exposure share to be computed. The dependent variable is log mean gross hourly pay. The share below the floor is the interpolated share of the occupation's employee jobs paid below \pounds 7.20 in the 2015 release; the Kaitz index is \pounds 7.20 divided by the occupation's 2015 median hourly pay. Both are demeaned across occupations, so the coefficient on risk in columns 3 and 5 is evaluated at mean exposure. The exposure share correlates """ + f"{o['nlw_exposure']['corr_share_risk']:.2f}" + r""" and the Kaitz index """ + f"{o['nlw_exposure']['corr_kaitz_risk']:.2f}" + r""" with the automation probability. """ + FE + r""" """ + SE + r"""
""" + SRC + r"""
\end{tablenotes}\end{threeparttable}\end{table}"""

# ------------------------------------------------------------------ Table 7
al = o['alt_outcomes']; nc = ej['nlw_controls']
cols = [('Jobs, all', al['log_jobs']), ('Balanced', ej['balanced']), ('Bal., 2014--19', ej['balanced_2014_19']),
        ('Bal., weighted', ej['weighted_balanced']), ('Bal., floor', nc['plus_nlw']), ('Hours', al['log_hours'])]
T['jobs'] = r"""\begin{table}[!ht]\centering
\caption{Post-2016 change in the automation-risk gradient of log employment and log hours}\label{tab:jobs}
""" + head('scriptsize', '2pt') + r"""
\begin{tabular}{l""" + "c" * len(cols) + r"""}\toprule
 & (1) & (2) & (3) & (4) & (5) & (6) \\
 & """ + " & ".join(c[0] for c in cols) + r""" \\ \midrule
Risk $\times$ post-2016 & """ + " & ".join(cell(c[1]['risk_post'])[0] for c in cols) + r""" \\
 & """ + " & ".join(cell(c[1]['risk_post'])[1] for c in cols) + r""" \\
95\% confidence interval & """ + " & ".join(ci(c[1]['risk_post']) for c in cols) + r""" \\
Floor share $\times$ post-2016 & & & & & """ + cell(nc['plus_nlw']['post_nlw'])[0] + r""" & \\
 & & & & & """ + cell(nc['plus_nlw']['post_nlw'])[1] + r""" & \\ \addlinespace
Occupation-years & """ + " & ".join(f"{c[1]['n']:,}" for c in cols) + r""" \\
Occupations & """ + " & ".join(f"{c[1]['nclus']}" for c in cols) + r""" \\
\bottomrule\end{tabular}
\begin{tablenotes}\footnotesize
\item \emph{Notes:} Estimates of equation (1) with log employee jobs (columns 1 to 5) or log mean paid hours per week (column 6) as the dependent variable. Columns 2 to 5 keep the """ + f"{ej['n_occ_balanced']}" + r""" occupations with a published jobs count in all seven releases. Column 4 weights by 2015 jobs. Column 5 adds the interaction between the 2015 share of jobs below \pounds 7.20 and the post-2016 indicator. """ + FE + r""" """ + SE + r"""
""" + SRC + r"""
\end{tablenotes}\end{threeparttable}\end{table}"""

# ------------------------------------------------------------------ Table 8
rows = []
for y in ES:
    a = esc(ej['event_study_balanced'], y); n = esc(ej['event_study_nlw_controlled'], y); h = esc(o['event_study_hours'], y)
    rows.append(f"{y} & {a[0]} & {a[1]} & {n[0]} & {n[1]} & {h[0]} & {h[1]} \\\\")
T['esjobs'] = r"""\begin{table}[!ht]\centering
\caption{Event-study estimates for log employment and log hours, relative to 2015}\label{tab:esjobs}
""" + head() + r"""
\begin{tabular}{lcccccc}\toprule
 & \multicolumn{2}{c}{(1) Jobs, balanced} & \multicolumn{2}{c}{(2) Jobs, floor controlled} & \multicolumn{2}{c}{(3) Hours} \\
\cmidrule(lr){2-3}\cmidrule(lr){4-5}\cmidrule(lr){6-7}
Release & $\hat{\beta}_{s}$ & (s.e.) & $\hat{\beta}_{s}$ & (s.e.) & $\hat{\beta}_{s}$ & (s.e.) \\ \midrule
""" + "\n".join(rows) + r"""
\addlinespace
Occupation-years & \multicolumn{2}{c}{""" + f"{ej['balanced']['n']:,}" + r"""} & \multicolumn{2}{c}{""" + f"{nc['plus_nlw']['n']:,}" + r"""} & \multicolumn{2}{c}{""" + f"{al['log_hours']['n']:,}" + r"""} \\
Occupations & \multicolumn{2}{c}{""" + f"{ej['n_occ_balanced']}" + r"""} & \multicolumn{2}{c}{""" + f"{nc['plus_nlw']['nclus']}" + r"""} & \multicolumn{2}{c}{""" + f"{al['log_hours']['nclus']}" + r"""} \\
\bottomrule\end{tabular}
\begin{tablenotes}\footnotesize
\item \emph{Notes:} Estimates of $\beta_{s}$ in equation (2) with the stated dependent variable and 2015 omitted. Column 2 adds the interaction between the 2015 floor-exposure share and each release indicator. A negative coefficient means employment in more automatable occupations was lower in that release, relative to 2015, than in less automatable ones. """ + FE + r""" """ + SE + r"""
""" + SRC + r"""
\end{tablenotes}\end{threeparttable}\end{table}"""

# ------------------------------------------------------------------ Table 9
rb = o['robustness']; pm = o['permutation']
rows = [f"Above-median risk $\\times$ post-2016 & {cell(rb['binary_above_median']['high_post'])[0]} & {cell(rb['binary_above_median']['high_post'])[1]} & {ci(rb['binary_above_median']['high_post'])} \\\\",
        f"Middle risk tercile $\\times$ post-2016 & {cell(rb['terciles']['t2_post'])[0]} & {cell(rb['terciles']['t2_post'])[1]} & {ci(rb['terciles']['t2_post'])} \\\\",
        f"Top risk tercile $\\times$ post-2016 & {cell(rb['terciles']['t3_post'])[0]} & {cell(rb['terciles']['t3_post'])[1]} & {ci(rb['terciles']['t3_post'])} \\\\",
        r"\addlinespace",
        f"Risk $\\times$ post-2016, major group $\\times$ release effects & {cell(rb['major_by_year']['risk_post'])[0]} & {cell(rb['major_by_year']['risk_post'])[1]} & {ci(rb['major_by_year']['risk_post'])} \\\\",
        f"Risk $\\times$ post-2016, sub-major group $\\times$ release effects & {cell(rb['submajor_by_year']['risk_post'])[0]} & {cell(rb['submajor_by_year']['risk_post'])[1]} & {ci(rb['submajor_by_year']['risk_post'])} \\\\",
        r"\addlinespace"]
for c in ['2017', '2018', '2019', '2020']:
    r = rb['cutoffs'][c]['rp']; rows.append(f"Risk $\\times$ post-{c} & {cell(r)[0]} & {cell(r)[1]} & {ci(r)} \\\\")
rows.append(r"\addlinespace")
rows.append(f"Risk $\\times$ post-2017, 2014--2019 releases only & {cell(rb['placebo_2017_within_2014_19']['rp'])[0]} & {cell(rb['placebo_2017_within_2014_19']['rp'])[1]} & {ci(rb['placebo_2017_within_2014_19']['rp'])} \\\\")
rows.append(f"Risk $\\times$ post-2018, 2014--2019 releases only & {cell(rb['placebo_2018_within_2014_19']['rp'])[0]} & {cell(rb['placebo_2018_within_2014_19']['rp'])[1]} & {ci(rb['placebo_2018_within_2014_19']['rp'])} \\\\")
T['rob'] = r"""\begin{table}[!ht]\centering
\caption{Alternative treatment definitions, time controls and cut-offs for log hourly pay}\label{tab:rob}
""" + head() + r"""
\begin{tabular}{lccc}\toprule
Specification & Estimate & (s.e.) & 95\% confidence interval \\ \midrule
\multicolumn{4}{l}{\emph{Panel A. Discrete treatment}} \\
""" + "\n".join(rows[:3]) + r"""
\addlinespace
\multicolumn{4}{l}{\emph{Panel B. Finer time controls}} \\
""" + "\n".join(rows[4:6]) + r"""
\addlinespace
\multicolumn{4}{l}{\emph{Panel C. Alternative and placebo cut-offs}} \\
""" + "\n".join(rows[7:]) + r"""
\bottomrule\end{tabular}
\begin{tablenotes}\footnotesize
\item \emph{Notes:} Each row is a separate regression of log mean gross hourly pay on the stated interaction, estimated on the panel of """ + f"{s['n_obs']:,}" + r""" occupation-years unless the row restricts the releases. """ + FE + r""" unless the row names a finer time control. Risk terciles use cuts at """ + f"{o['tercile_cuts'][0]:.3f} and {o['tercile_cuts'][1]:.3f}" + r""" with the bottom tercile as the reference. Major groups are the nine one-digit SOC 2010 groups and sub-major groups the """ + f"{o['n_submajor']}" + r""" two-digit groups. """ + SE + r"""
A permutation test that reassigns the automation probabilities at random across the 366 occupations """ + f"{pm['B']:,}" + r""" times, holding the panel fixed, produces a largest placebo interaction of """ + f"{pm['perm_max_abs']:.3f}" + r""" in absolute value, against the estimate of """ + f"{o['baseline']['risk_post']['b']:.3f}" + r""" in Table~\ref{tab:pay}, with a permutation standard deviation of """ + f"{pm['perm_sd']:.3f}" + r""".
""" + SRC + r"""
\end{tablenotes}\end{threeparttable}\end{table}"""

# ------------------------------------------------------------------ Appendix C
hb = o['het_baseline_pay']; pt = o['pay_terciles']; ex_ = o['exclude_low_2015']
rows = []
for k in ['1', '2', '3']:
    lab = {'1': 'Bottom third', '2': 'Middle third', '3': 'Top third'}[k]; r = pt[k]
    rows.append(f"{lab} of 2014 pay (\\pounds{r['w14_min']:.2f}--{r['w14_max']:.2f}) & {cell(r['risk_post'])[0]} & {cell(r['risk_post'])[1]} & {r['n']:,} & {r['nclus']} \\\\")
rows2 = [f"2015 mean pay of \\pounds{k} or more & {cell(ex_[k]['risk_post'])[0]} & {cell(ex_[k]['risk_post'])[1]} & {ex_[k]['n']:,} & {ex_[k]['nclus']} \\\\" for k in ['8', '9', '10', '11', '12']]
T['paylevel'] = r"""\begin{table}[!ht]\centering
\caption{The post-2016 pay gradient by level of 2014 pay}\label{tab:paylevel}
""" + head() + r"""
\begin{tabular}{lcccc}\toprule
Sample or specification & Risk $\times$ post & (s.e.) & Occ.-years & Occupations \\ \midrule
\multicolumn{5}{l}{\emph{Panel A. Conditioning on demeaned log 2014 pay, releases 2015--2020}} \\
Risk $\times$ post alone & """ + f"{cell(hb['risk_only']['risk_post'])[0]} & {cell(hb['risk_only']['risk_post'])[1]} & {hb['risk_only']['n']:,} & {hb['risk_only']['nclus']}" + r""" \\
Adding log 2014 pay $\times$ post & """ + f"{cell(hb['plus_pay']['risk_post'])[0]} & {cell(hb['plus_pay']['risk_post'])[1]} & {hb['plus_pay']['n']:,} & {hb['plus_pay']['nclus']}" + r""" \\
\quad coefficient on log 2014 pay $\times$ post & """ + f"{cell(hb['plus_pay']['post_c'])[0]} & {cell(hb['plus_pay']['post_c'])[1]} & &" + r""" \\
\addlinespace
\multicolumn{5}{l}{\emph{Panel B. Within terciles of 2014 mean hourly pay, releases 2015--2020}} \\
""" + "\n".join(rows) + r"""
\addlinespace
\multicolumn{5}{l}{\emph{Panel C. Dropping low-paid occupations, releases 2014--2020}} \\
""" + "\n".join(rows2) + r"""
\bottomrule\end{tabular}
\begin{tablenotes}\footnotesize
\item \emph{Notes:} The dependent variable is log mean gross hourly pay. Panel A demeans the occupation's log mean pay in the 2014 release across occupations and excludes that release from estimation, so the conditioning variable is predetermined. The occupation-level correlation between the automation probability and log 2014 pay is """ + f"{hb['corr_risk_lnw14']:.2f}" + r""". """ + FE + r""" """ + SE + r"""
""" + SRC + r"""
\end{tablenotes}\end{threeparttable}\end{table}"""

# ------------------------------------------------------------------ Appendix D
cb = o['classification_break']
rows = [f"{e['soc']} & {e['soc10_2020']} & {e['soc20_2021']} \\\\" for e in cb['examples']]
T['soc'] = r"""\begin{table}[!ht]\centering
\caption{Four-digit codes denoting different occupations under SOC 2010 and SOC 2020}\label{tab:soc}
""" + head() + r"""
\begin{tabular}{lp{0.40\textwidth}p{0.40\textwidth}}\toprule
Code & SOC 2010 title, 2020 release & SOC 2020 title, 2021 release \\ \midrule
""" + "\n".join(rows) + r"""
\bottomrule\end{tabular}
\begin{tablenotes}\footnotesize
\item \emph{Notes:} The 2020 release publishes """ + f"{cb['n_soc10_2020']}" + r""" four-digit SOC 2010 unit groups and the 2021 release """ + f"{cb['n_soc20_2021']}" + r""" SOC 2020 unit groups. """ + f"{cb['n_codes_in_both']}" + r""" numeric codes appear in both, of which """ + f"{cb['n_same_description']}" + r""" carry the same occupation title and """ + f"{cb['n_different_description']}" + r""" a different one. """ + f"{cb['n_soc20_codes_new']}" + r""" SOC 2020 codes have no SOC 2010 counterpart and """ + f"{cb['n_soc10_codes_gone']}" + r""" SOC 2010 codes have no SOC 2020 counterpart. The rows are the first six mismatches in code order.
""" + SRC + r"""
\end{tablenotes}\end{threeparttable}\end{table}"""

cf = o['contaminated_full_panel']; ecs = o['event_study_contaminated']
rows = []
for y in [2014, 2015, 2016, 2017, 2018, 2019, 2020, 2021, 2022, 2023]:
    a = esc(ecs, y)
    c = esc(o['event_study'], y) if str(y) in o['event_study'] else ('--', '')
    rows.append(f"{y} & {c[0]} & {c[1]} & {a[0]} & {a[1]} \\\\")
T['contam'] = r"""\begin{table}[!ht]\centering
\caption{Pay event study with and without the mismatched 2021--2023 releases}\label{tab:contam}
""" + head() + r"""
\begin{tabular}{lcccc}\toprule
 & \multicolumn{2}{c}{SOC 2010 releases only} & \multicolumn{2}{c}{SOC 2020 releases joined by code} \\
\cmidrule(lr){2-3}\cmidrule(lr){4-5}
Release & $\hat{\beta}_{s}$ & (s.e.) & $\hat{\beta}_{s}$ & (s.e.) \\ \midrule
""" + "\n".join(rows) + r"""
\addlinespace
Risk $\times$ post-2016 & """ + f"{cell(o['baseline']['risk_post'])[0]} & {cell(o['baseline']['risk_post'])[1]} & {cell(cf['risk_post'])[0]} & {cell(cf['risk_post'])[1]}" + r""" \\
Occupation-years & \multicolumn{2}{c}{""" + f"{o['baseline']['n']:,}" + r"""} & \multicolumn{2}{c}{""" + f"{cf['n']:,}" + r"""} \\
\bottomrule\end{tabular}
\begin{tablenotes}\footnotesize
\item \emph{Notes:} The dependent variable is log mean gross hourly pay. The right-hand columns reproduce the design of the earlier version of this paper, in which the 2021 to 2023 releases, published on SOC 2020, were joined to SOC 2010 automation probabilities by numeric code. """ + FE + r""" """ + SE + r"""
""" + SRC + r"""
\end{tablenotes}\end{threeparttable}\end{table}"""

# ------------------------------------------------------------------ Appendix B
prov = list(csv.DictReader(open('build/hourly_gross_provenance.csv')))
rows = [f"{p['year']} & {p['basis']} & {p['n_four_digit']} & {p['n_mean']} & {p['n_median']} & {p['n_jobs']} \\\\" for p in prov]
T['prov'] = r"""\begin{table}[!ht]\centering
\caption{Workbook provenance and published cell counts, ASHE Table 14.5a}\label{tab:prov}
""" + head() + r"""
\begin{tabular}{lccccc}\toprule
Release & Classification & Four-digit rows & Mean published & Median published & Jobs published \\ \midrule
""" + "\n".join(rows) + r"""
\bottomrule\end{tabular}
\begin{tablenotes}\footnotesize
\item \emph{Notes:} Each release is the revised edition downloaded from the ONS dataset page for ASHE Table 14 on the SOC 2010 basis. Counts are four-digit unit-group rows on the All sheet of Table 14.5a carrying a value that is not suppressed in the stated column. The 2021 to 2023 workbooks are titled for SOC 2020 and enter the analysis only in Appendix D.
""" + SRC + r"""
\end{tablenotes}\end{threeparttable}\end{table}"""

for k, v in T.items():
    open(f'paper/tables/{k}.tex', 'w').write(v)
print('ok', list(T))
