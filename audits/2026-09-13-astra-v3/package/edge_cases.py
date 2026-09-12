"""Independent edge/reference tests, plus targeted probe of v3 floating PMF."""
import sys,json,itertools
from fractions import Fraction
from pathlib import Path
import numpy as np
from independent import call,load
B=Path(__file__).resolve().parent;R=B/'snapshot';out={}
cases={'tie':([100],[110]),'stable_no':([100],[109]),'stable_reg':([100],[120]),'multimodal':([100]*10,[200]*3+[29]*7),'near_zero':([1],[1]),'zero_baseline':([0],[1])}
for name,(aa,bb) in cases.items():
    a=np.array(aa);b=np.array(bb)
    if not a.min()>0:out[name]={'excluded':'zero baseline; ratio undefined'};continue
    theta=Fraction(int(b.sum()),len(b))/Fraction(int(a.sum()),len(a))-1
    f=b.mean()/a.mean()-1
    out[name]={'theta_exact':str(theta),'theta_float':float(f),'pcall':call(a,b)[0],'float_constant_verdict':'REGRESSION' if f>.1 else 'NO_REGRESSION' if f<.1 else 'UNRESOLVED','exact_constant_side':'REGRESSION' if theta>Fraction(1,10) else 'NO_REGRESSION' if theta<Fraction(1,10) else 'UNRESOLVED'}
# Integer convolution versus ordered brute force, including ties and mixed supports.
rng=np.random.default_rng(89);maximum=0
for _ in range(150):
    a=rng.integers(1,15,4);b=rng.integers(0,20,4)
    av=[sum(t) for t in itertools.product(a,repeat=3)];bv=[sum(t) for t in itertools.product(b,repeat=3)]
    p=sum(10*y>=11*x for x in av for y in bv)/(len(av)*len(bv));maximum=max(maximum,abs(p-call(a,b)[0]))
out['brute_force']={'cases':150,'max_error':maximum};assert maximum==0
sys.path.insert(0,str(R));from raw_endpoint import exact_call_probability
a=np.full(200,100,dtype=np.int64);b=np.r_[np.full(199,120),121]
out['floating_probability_probe']={'exact':call(a,b)[0],'project':exact_call_probability(a,b,Fraction(1,10),3)}
out['raw_mutations']={}
for name,c in [('A','knn_n67'),('B','knn_n67'),('C','knn_n67'),('F','multiplier_n45'),('G','knn_n67')]:
    rr=[]
    for root in [R,B/('mut'+name)]:
        a=load(root,c,'143')[1];b=load(root,c,'200')[1];theta=float(b.mean()/a.mean()-1)
        rng=np.random.default_rng(20260904);j=rng.integers(0,200,(4000,200));ci=np.percentile(b[j].mean(1)/a[j].mean(1)-1,[2.5,97.5]);v='REGRESSION' if ci[0]>.1 else 'NO_REGRESSION' if ci[1]<.1 else 'UNRESOLVED';p=call(a,b)[0] if name!='A' or root==R else None
        # A has one value 10,000,000: avoid enormous dense convolution; enumerate only its sparse triple sums.
        if p is None:
            from collections import Counter
            def sparse(x):
                h=Counter(map(int,x));z=Counter({0:1})
                for _ in range(3):
                    w=Counter()
                    for u,cu in z.items():
                        for v,cv in h.items():w[u+v]+=cu*cv
                    z=w
                return z
            aa=sparse(a);bb=sparse(b);av=sorted(aa);ac=np.r_[0,np.cumsum([aa[x] for x in av])];p=sum(cu*int(ac[np.searchsorted(av,(10*x)//11,side='right')]) for x,cu in bb.items())/200**6
        rr.append(dict(theta=theta,theta_ci=ci.tolist(),verdict=v,boundary=abs(theta-.1)*100<=3,pcall=p,risk=None if v=='UNRESOLVED' else 1-p if v=='REGRESSION' else p))
    out['raw_mutations'][name]=rr
(B/'edge_cases.json').write_text(json.dumps(out,indent=2));print(json.dumps(out,indent=2))
