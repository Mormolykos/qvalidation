"""Independent raw-only reconstruction; no project imports. Python 3.10/numpy/scipy.
Usage: python independent.py SNAPSHOT OUTPUT.json
Integer histogram convolution counts ordered with-replacement triples exactly.
The bootstrap uses paired seed resampling and frozen classifications.
"""
import sys,json,csv,math
from pathlib import Path
import numpy as np
from scipy.stats import spearmanr

def load(root,c,v):
    records=[json.loads(l) for l in (root/'results/raw/prereg'/f'{c}_heavy-hex_q{v}.jsonl').read_text().splitlines()]
    runs=sorted((r['seed'],r['two_q']) for r in records if r.get('record')=='run')
    assert len(runs)==200 and len(set(s for s,x in runs))==200
    return np.array([s for s,x in runs]),np.array([x for s,x in runs],dtype=np.int64)

def sums(a,k=3):
    lo=int(a.min()); g=0
    for x in a:g=math.gcd(g,int(x)-lo)
    g=max(1,g); h=np.bincount((a-lo)//g).astype(np.int64); z=h
    for _ in range(k-1):z=np.convolve(z,h)
    assert int(z.sum())==len(a)**k
    return k*lo+g*np.arange(len(z)),z

def call(a,b):
    sa,ca=sums(a); sb,cb=sums(b)
    ix=np.searchsorted(sa,(10*sb)//11,side='right')
    ac=np.r_[0,np.cumsum(ca)]
    numer=int(np.dot(ac[ix],cb)); denom=len(a)**3*len(b)**3
    return numer/denom,numer,denom

def reconstruct(root):
    out=[]
    for c in (root/'_selected.txt').read_text().split():
        s,a=load(root,c,'143'); t,b=load(root,c,'200'); assert np.array_equal(s,t) and (a>0).all()
        theta=b.mean()/a.mean()-1
        rng=np.random.default_rng(20260904); idx=rng.integers(0,200,(4000,200))
        lo,hi=np.percentile(b[idx].mean(1)/a[idx].mean(1)-1,[2.5,97.5])
        verdict='REGRESSION' if lo>.1 else 'NO_REGRESSION' if hi<.1 else 'UNRESOLVED'
        boundary=abs(theta-.1)*100<=3
        r=dict(circuit=c,theta=float(theta),theta_ci=[float(lo),float(hi)],verdict=verdict,boundary=bool(boundary),constant=bool(a.std()==0 and b.std()==0),risk=None)
        if verdict!='UNRESOLVED':
            p,nu,de=call(a,b); risk=1-p if verdict=='REGRESSION' else p
            rng=np.random.default_rng(20260905); errs=[]
            for _ in range(400):
                j=rng.integers(0,200,200); pc=call(a[j],b[j])[0]; errs.append(1-pc if verdict=='REGRESSION' else pc)
            ci=np.percentile(errs,[2.5,97.5]); r.update(risk=risk,call_numerator=nu,call_denominator=de,risk_ci=ci.tolist(),excludes_zero=bool(ci[0]>0))
        r['alternative_estimands']={'mean_ratios':float(np.mean(b/a)-1),'median_ratio':float(np.median(b/a)-1),'ratio_medians':float(np.median(b)/np.median(a)-1),'paired_difference_normalized':float(np.mean(b-a)/a.mean())}
        out.append(r);print(c,verdict,r['risk'],flush=True)
    elig=[r for r in out if r['verdict']!='UNRESOLVED' and not r['boundary']]
    st=[r for r in out if r['verdict']!='UNRESOLVED' and not r['constant']]
    counts=dict(resolved=sum(r['verdict']!='UNRESOLVED' for r in out),unresolved=sum(r['verdict']=='UNRESOLVED' for r in out),boundary=sum(r['boundary'] for r in out),eligible=len(elig),excludes_zero=sum(r['excludes_zero'] for r in elig),ge5=sum(r['risk']>=.05 for r in elig),ge10=sum(r['risk']>=.1 for r in elig))
    # Only after reconstruction, consult summary for discrepancies.
    saved={r['circuit']:r for r in csv.DictReader((root/'results/summary/prereg_heavy-hex.csv').open())}
    differences=[]
    for r in out:
        q=saved[r['circuit']]
        if r['risk'] is not None:
            differences.append(dict(circuit=r['circuit'],point_delta=r['risk']-float(q['error_rate']),exact_boot_ci=r['risk_ci'],saved_ci=[float(q['error_ci_lo']),float(q['error_ci_hi'])]))
        assert abs(r['theta']*100-float(q['est_long_run_change_pct']))<.000051
        assert r['verdict']==q['verdict'] and str(r['boundary'])==q['boundary']
        assert max(abs(r['theta_ci'][i]*100-float(q[k])) for i,k in enumerate(['change_ci_lo_pct','change_ci_hi_pct']))<.000051
    seeds=load(root,out[0]['circuit'],'143')[0]; generated=np.array(sorted(set(np.random.default_rng(20260904).integers(7,2**31-1,400).tolist()))[:200]);assert np.array_equal(seeds,generated)
    return dict(counts=counts,rows=out,comparison=differences,spearman=float(spearmanr([abs(r['theta']-.1) for r in st],[r['risk'] for r in st]).statistic),seed_upper_half=int(sum(seeds>(2**31-1)/2)))

if __name__=='__main__':
    result=reconstruct(Path(sys.argv[1]));Path(sys.argv[2]).write_text(json.dumps(result,indent=2));print(result['counts'])
