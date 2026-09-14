"""Employment supplement: floor-exposure controls, trend/break, hours event study, descriptives.
Appends to analysis/locked_numbers_v2.json written by run3.py."""
import pandas as pd, numpy as np, pyfixest as pf, json, warnings
warnings.filterwarnings('ignore')
o=json.load(open('analysis/locked_numbers_v2.json'))
risk=pd.read_stata('data_work/risk.dta'); risk['soc']=risk.soc.astype(int)
g=pd.read_csv('build/hourly_gross_raw.csv'); g=g[g.year<=2020]
PCT=[10,20,25,30,40,60,70,75,80,90]; NLW=7.20
p15=g[g.year==2015].set_index('soc')
def share_below(row,thr=NLW):
    xs,ys=[],[]
    for p in PCT:
        v=row.get('p%d'%p,np.nan)
        if pd.notna(v): xs.append(float(v)); ys.append(float(p))
    if pd.notna(row.get('median',np.nan)): xs.append(float(row['median'])); ys.append(50.0)
    if len(xs)<3: return np.nan
    o_=np.argsort(xs); xs=np.array(xs)[o_]; ys=np.array(ys)[o_]
    if thr<=xs[0]:
        slope=(ys[1]-ys[0])/(xs[1]-xs[0]) if xs[1]>xs[0] else 0.0
        return float(max(0.0, ys[0]-slope*(xs[0]-thr)))
    if thr>=xs[-1]: return float(ys[-1])
    return float(np.interp(thr,xs,ys))
p15=p15.assign(nlw_share=p15.apply(share_below,axis=1)/100.0); p15['kaitz']=NLW/p15['median']
expo=p15[['nlw_share','kaitz','jobs']].rename(columns={'jobs':'jobs15'})
# worked example rows
o['nlw_worked']={int(s):{'desc':p15.loc[s,'desc'],'median':float(p15.loc[s,'median']),'p40':float(p15.loc[s,'p40']),'p60':float(p15.loc[s,'p60']),'p10':float(p15.loc[s,'p10']),'p20':float(p15.loc[s,'p20']),'share':float(p15.loc[s,'nlw_share'])} for s in [7111,2211]}
jb=g[g['jobs'].notna()&(g['jobs']>0)].merge(risk,on='soc')
jb['y']=np.log(jb['jobs']); jb['post']=(jb.year>=2016).astype(int); jb['risk_post']=jb.risk*jb.post
cnt=jb.groupby('soc').size(); bal=cnt[cnt==7].index
def fit(f,d,names,w=None):
    m=pf.feols(f,data=d,vcov={'CRV1':'soc'},weights=w); t=m.tidy()
    r={k:dict(b=float(t.loc[k,'Estimate']),se=float(t.loc[k,'Std. Error']),lo=float(t.loc[k,'2.5%']),hi=float(t.loc[k,'97.5%']),p=float(t.loc[k,'Pr(>|t|)'])) for k in names}
    r['n']=int(m._N); r['nclus']=int(d.soc.nunique()); return r
ES=[2014]+list(range(2016,2021)); terms=' + '.join(f'rk_{y}' for y in ES)
for y in ES: jb[f'rk_{y}']=jb.risk*(jb.year==y)
e={}
e['balanced']=fit('y ~ risk_post | soc + year', jb[jb.soc.isin(bal)], ['risk_post'])
e['balanced_2014_19']=fit('y ~ risk_post | soc + year', jb[(jb.soc.isin(bal))&(jb.year<=2019)], ['risk_post'])
e['n_occ_balanced']=int(len(bal)); e['n_occ_any']=int(jb.soc.nunique())
r=fit(f'y ~ {terms} | soc + year', jb[jb.soc.isin(bal)], [f'rk_{y}' for y in ES])
e['event_study_balanced']={int(k.split('_')[1]):v for k,v in r.items() if k.startswith('rk_')}; e['event_study_balanced'][2015]=dict(b=0.0,se=0.0,lo=0.0,hi=0.0,p=None)
tot=jb[jb.soc.isin(bal)].groupby('year').jobs.sum(); e['total_jobs_thousands']={int(y):float(v) for y,v in tot.items()}
occ=jb[['soc','risk']].drop_duplicates(); med=occ.risk.median(); jb['high']=(jb.risk>med).astype(int)
sh=jb[jb.soc.isin(bal)].groupby(['year','high']).jobs.sum().unstack()
e['share_jobs_high_risk']={int(y):float(sh.loc[y,1]/(sh.loc[y,0]+sh.loc[y,1])) for y in sh.index}
w=g[g['mean'].notna()].merge(risk,on='soc')
a=w[w.year==2015].set_index('soc'); b=w[w.year==2019].set_index('soc'); j=jb[jb.year==2015].set_index('soc'); k=jb[jb.year==2019].set_index('soc')
ix=a.index.intersection(b.index).intersection(j.index).intersection(k.index)
dpay=np.log(b.loc[ix,'mean'])-np.log(a.loc[ix,'mean']); djob=np.log(k.loc[ix,'jobs'])-np.log(j.loc[ix,'jobs'])
e['changes_2015_2019']={'n_occ':int(len(ix)),'corr_dpay_djobs':float(dpay.corr(djob)),'corr_djobs_risk':float(djob.corr(a.loc[ix,'risk'])),'corr_dpay_risk':float(dpay.corr(a.loc[ix,'risk']))}
jbx=jb.merge(expo,left_on='soc',right_index=True,how='inner'); jbx=jbx[jbx.nlw_share.notna()]
jbx['nlw_c']=jbx.nlw_share-jbx.nlw_share.mean(); jbx['post_nlw']=jbx.post*jbx.nlw_c
jbx['kaitz_c']=jbx.kaitz-jbx.kaitz.mean(); jbx['post_kaitz']=jbx.post*jbx.kaitz_c
cnt2=jbx.groupby('soc').size(); bal2=cnt2[cnt2==7].index; jbb=jbx[jbx.soc.isin(bal2)].copy()
e['nlw_controls']={'risk_only':fit('y ~ risk_post | soc + year', jbb, ['risk_post']),
 'plus_nlw':fit('y ~ risk_post + post_nlw | soc + year', jbb, ['risk_post','post_nlw']),
 'plus_kaitz':fit('y ~ risk_post + post_kaitz | soc + year', jbb, ['risk_post','post_kaitz'])}
for y in ES: jbb[f'nl_{y}']=jbb.nlw_c*(jbb.year==y)
t2=' + '.join([f'rk_{y}' for y in ES]+[f'nl_{y}' for y in ES])
r=fit(f'y ~ {t2} | soc + year', jbb, [f'rk_{y}' for y in ES])
e['event_study_nlw_controlled']={int(k.split('_')[1]):v for k,v in r.items() if k.startswith('rk_')}; e['event_study_nlw_controlled'][2015]=dict(b=0.0,se=0.0,lo=0.0,hi=0.0,p=None)
e['weighted_balanced']=fit('y ~ risk_post | soc + year', jbb, ['risk_post'], w='jobs15')
jbb['trend']=jbb.year-2015; jbb['risk_trend']=jbb.risk*jbb.trend
e['trend_break_balanced']=fit('y ~ risk_trend + risk_post | soc + year', jbb, ['risk_trend','risk_post'])
e['trend_break_balanced_2014_19']=fit('y ~ risk_trend + risk_post | soc + year', jbb[jbb.year<=2019], ['risk_trend','risk_post'])
q=occ.risk.quantile([1/3,2/3]).values; jbb['rt']=np.where(jbb.risk<=q[0],1,np.where(jbb.risk<=q[1],2,3))
gj=jbb.groupby(['rt','year']).jobs.sum().unstack()
e['jobs_growth_2015_2019_by_risk_tercile']={int(k):float(np.log(gj.loc[k,2019])-np.log(gj.loc[k,2015])) for k in [1,2,3]}
e['jobs_growth_2015_2020_by_risk_tercile']={int(k):float(np.log(gj.loc[k,2020])-np.log(gj.loc[k,2015])) for k in [1,2,3]}
h=pd.read_csv('build/hours_total_raw.csv'); h=h[h.year<=2020]; hr=h[h['mean'].notna()].merge(risk,on='soc')
hr['y']=np.log(hr['mean']); hr['post']=(hr.year>=2016).astype(int)
for y in ES: hr[f'rk_{y}']=hr.risk*(hr.year==y)
r=fit(f'y ~ {terms} | soc + year', hr, [f'rk_{y}' for y in ES])
o['event_study_hours']={int(k.split('_')[1]):v for k,v in r.items() if k.startswith('rk_')}; o['event_study_hours'][2015]=dict(b=0.0,se=0.0,lo=0.0,hi=0.0,p=None)
o['hours_desc']={'mean_hours':float(hr['mean'].mean()),'n':int(len(hr)),'nocc':int(hr.soc.nunique())}
o['jobs_desc']={'mean_jobs_thousands':float(jb.jobs.mean()),'median_jobs_thousands':float(jb.jobs.median()),'min':float(jb.jobs.min()),'max':float(jb.jobs.max()),'n':int(len(jb)),'nocc':int(jb.soc.nunique())}
o['employment']=e
json.dump(o,open('analysis/locked_numbers_v2.json','w'),indent=1,default=float)
print('nlw', {k:round(v,3) for k,v in o['nlw_exposure'].items() if isinstance(v,float)})
for k,v in o['nlw_models'].items(): print(' pay',k,{a:f"{v[a]['b']:+.3f}({v[a]['se']:.3f})" for a in v if a in ('risk_post','post_nlw','rp_nlw','post_kaitz','rp_kaitz')},v['n'],v['nclus'])
print('ES pay nlw', {y:f"{o['event_study_nlw_controlled'][y]['b']:+.3f}({o['event_study_nlw_controlled'][y]['se']:.3f})" for y in sorted(o['event_study_nlw_controlled'],key=int)})
for k,v in e['nlw_controls'].items(): print(' jobs',k,{a:f"{v[a]['b']:+.3f}({v[a]['se']:.3f})" for a in v if a in ('risk_post','post_nlw','post_kaitz')},v['n'],v['nclus'])
print('worked', o['nlw_worked'])
