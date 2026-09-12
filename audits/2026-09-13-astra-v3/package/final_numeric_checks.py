"""Additional raw-only checks: WOR, paired calls, family interval, linear support."""
import json,re,math
from pathlib import Path
import numpy as np
from independent import load,sums,call
B=Path(__file__).resolve().parent;R=B/'snapshot';D=json.loads((B/'independent.json').read_text());out={}
def wor(a):
    av,ac=sums(a);lo=int(a.min());g=0
    for x in a:g=math.gcd(g,int(x)-lo)
    g=max(1,g);pair=(2*a[:,None]+a[None,:]).ravel();trip=3*a
    ac=ac-3*np.bincount((pair-3*lo)//g,minlength=len(ac))+2*np.bincount((trip-3*lo)//g,minlength=len(ac))
    assert ac.min()>=0 and int(ac.sum())==len(a)*(len(a)-1)*(len(a)-2)
    return av,ac
diffs=[];paired=[]
for r in D['rows']:
    if r['verdict']=='UNRESOLVED':continue
    c=r['circuit'];a=load(R,c,'143')[1];b=load(R,c,'200')[1];av,ac=wor(a);bv,bc=wor(b)
    pc=int(np.dot(np.r_[0,np.cumsum(ac)][np.searchsorted(av,(10*bv)//11,side='right')],bc))/int(ac.sum())/int(bc.sum())
    risk=1-pc if r['verdict']=='REGRESSION' else pc;diffs.append(dict(circuit=c,wr=r['risk'],wor=risk,abs_delta=abs(risk-r['risk'])))
    ds,dc=sums(10*b-11*a);p=int(dc[ds>=0].sum())/200**3;paired.append(dict(circuit=c,risk=1-p if r['verdict']=='REGRESSION' else p))
out['replacement']=diffs;out['max_replacement_delta']=max(r['abs_delta'] for r in diffs);out['paired']=paired
fam={}
for r in D['rows']:
    if r['verdict']=='UNRESOLVED' or r['boundary']:continue
    f=re.sub(r'_?n?\d+$','',r['circuit']) or r['circuit'];fam.setdefault(f,[]).append(r['excludes_zero'])
names=sorted(fam);rng=np.random.default_rng(7);pr=[]
for _ in range(20000):
    chosen=[names[i] for i in rng.integers(0,len(names),len(names))];flat=[v for n in chosen for v in fam[n]];pr.append(np.mean(flat))
out['family']={'groups':fam,'ci':np.percentile(pr,[2.5,97.5]).tolist()}
def arm(v):
    rr=[json.loads(l) for l in (R/f'results/raw/deep_bv_n140_q{v}.jsonl').read_text().splitlines()];return np.array([r['two_q'] for r in sorted([r for r in rr if r.get('record')=='run'],key=lambda r:r['seed'])])
a,b=arm('143'),arm('200');av,ac=sums(a);bv,bc=sums(b);den=int(ac.sum())*int(bc.sum());cut=.4614152373646045
percentile=sum(int(cn)*int(ac[av>=v/(1+cut)].sum()) for v,cn in zip(bv,bc))/den
out['linear_bv140']={'n':[len(a),len(b)],'support_pct':[100*(b.min()/a.max()-1),100*(b.max()/a.min()-1)],'issue_percentile':percentile}
(B/'final_numeric_checks.json').write_text(json.dumps(out,indent=2));print('max WR/WOR delta',out['max_replacement_delta']);print('familyCI',out['family']['ci']);print(out['linear_bv140']);print('paired', [r for r in paired if r['circuit'] in ['bv_n280','knn_n67']])
