"""Independent supplementary calculations against pinned raw observations only."""
import json,csv,subprocess,hashlib
from pathlib import Path
import numpy as np
from scipy.stats import mannwhitneyu
from scipy.signal import fftconvolve
from independent import load,sums,call
B=Path(__file__).resolve().parent;R=B/'snapshot';out={}
def records(p):return [json.loads(l) for l in p.read_text().splitlines() if l.strip()]
def runs(p):return [r for r in records(p) if r.get('record')=='run']
def values(p):return np.array([r['two_q'] for r in sorted(runs(p),key=lambda r:r['seed'])],dtype=np.int64)
sel=set((R/'_selected.txt').read_text().split());rows=json.loads((B/'independent.json').read_text())['rows']
cen={}
for r in runs(R/'results/raw/bp_large_heavy-hex_q202.jsonl'):cen.setdefault(r['circuit'],[]).append(r)
rule={c for c,v in cen.items() if len(v)==12 and sum(r['seconds'] for r in v)<=10 and c!='bv_n140'}
out['selection_rule_difference']=sorted(rule^sel);out['selection']=[]
for old in [False,True]:
    s=sel|({'bv_n140'} if old else set());g=[[],[]]
    for c,rs in cen.items():
        v=[r['two_q'] for r in rs]
        if len(v)>=12:g[int(c not in s)].append((max(v)-min(v))/min(v))
    out['selection'].append(dict(old=old,n=list(map(len,g)),medians=list(map(float,map(np.median,g))),p=float(mannwhitneyu(*g).pvalue)))
fit={'additive':0,'multiplicative':0,'tie':0}
for c in sel:
    a=load(R,c,'143')[1].astype(float);b=load(R,c,'200')[1].astype(float);m=(a@b)/(a@a);d=(b-a).mean();rm=sum((b-m*a)**2);ra=sum((b-a-d)**2)
    fit['tie' if abs(rm-ra)<1e-9 else 'additive' if ra<rm else 'multiplicative']+=1
out['fits']=fit
out['crossmachine']=[]
for v in ['143','200','202']:
    pa=R/f'crossmachine/desktop_q{v}.jsonl';pb=R/f'crossmachine/laptop_q{v}.jsonl'
    a={(r['circuit'],r['seed']):r['two_q'] for r in runs(pa)};b={(r['circuit'],r['seed']):r['two_q'] for r in runs(pb)}
    out['crossmachine'].append(dict(version=v,n=len(a),equal=a==b,environment=[records(pa)[0],records(pb)[0]]))
out['issue']=[]
for c in ['bv_n140','bv_n280','knn_341']:
    a,b=[np.array([r['two_q'] for r in runs(R/f'results/raw/bp_large_linear_q{v}.jsonl') if r['circuit']==c]) for v in ['143','200']]
    out['issue'].append(dict(circuit=c,n=[len(a),len(b)],theta_pct=float(100*(b.mean()/a.mean()-1))))
def pmf(v,k):
    h=np.bincount(v-v.min())/len(v);z=np.array([1.])
    for _ in range(k):z=fftconvolve(z,h)
    assert z.min()>-1e-13 and abs(z.sum()-1)<1e-10
    z[z<0]=0;return np.arange(len(z))+k*v.min(),z
a,b=[np.concatenate([values(R/f'results/raw/{p}_bv_n140_heavy-hex_q{v}.jsonl') for p in ['deep','scatter']]) for v in ['143','200']]
out['k_sweep']={}
for k in [1,3,5,8,10,20]:
    av,ap=pmf(a,k);bv,bp=pmf(b,k);p=ap@(1-np.r_[0,np.cumsum(bp)][np.searchsorted(10*bv,11*av)])
    out['k_sweep'][k]=float(100*p)
out['bands']=[]
for row in rows:
    if row['verdict']=='UNRESOLVED' or row['constant']:continue
    c=row['circuit'];a=load(R,c,'143')[1];b=load(R,c,'200')[1];av,ac=sums(a);bv,bc=sums(b);bcum=np.r_[0,np.cumsum(bc)];den=float(ac.sum())*bc.sum();mr=np.mean(b/a);ma=a.mean();mb=b.mean();C=(mb/ma)/mr
    def prob(r,model):
        if model=='floor':return call(a,(r*b/mr).astype(np.int64))[0]
        if model=='addfloor':return call(a,(b+r*ma-mb).astype(np.int64))[0]
        cut=1.1*av*mr/r if model=='mult' else 1.1*av-3*(r*ma-mb)
        ix=np.searchsorted(bv,cut,side='left');return float(ac@(bc.sum()-bcum[ix]))/den
    def solve(target,model):
        lo,hi=.5,3.
        for _ in range(45):
            mid=(lo+hi)/2
            if prob(mid,model)>=target:hi=mid
            else:lo=mid
        return (lo+hi)/2
    bands={}
    for model in ['mult','add','floor','addfloor']:
        l,h=solve(.05,model),solve(.95,model);bands[model]=[100*(l-1),100*(h-1),100*(h-l)]
    out['bands'].append(dict(circuit=c,C=float(C),bands=bands,true_width=bands['mult'][2]*C))
out['band_quantiles']={m:np.percentile([r['bands'][m][2] for r in out['bands']],[50,75,100]).tolist() for m in ['mult','add','floor','addfloor']}
out['band_true_median']=float(np.median([r['true_width'] for r in out['bands']]))
out['counterexamples']={'near_stable':call(np.array([100]),np.array([109]))[0],'far_unstable':call(np.array([100]*10),np.array([200]*3+[29]*7))[0],'missing_tail_probability':.99**200,'population_risk':.99**3}
(B/'supplementary.json').write_text(json.dumps(out,indent=2));print(json.dumps({k:v for k,v in out.items() if k not in ['bands','crossmachine']},indent=2))
