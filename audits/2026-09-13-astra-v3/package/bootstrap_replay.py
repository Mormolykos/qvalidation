"""Fresh exact replay of original MC bootstrap stream, independently from raw.
Constants have analytical [0,0]; other circuits use all 400*400000 trials.
"""
import json,csv,numpy as np
from pathlib import Path
from independent import load,call
BASE=Path(__file__).resolve().parent; ROOT=BASE/'snapshot'
rows=json.loads((BASE/'independent.json').read_text())['rows'];out=[]
saved={r['circuit']:r for r in csv.DictReader((ROOT/'results/summary/prereg_heavy-hex.csv').open())}
for row in rows:
    if row['verdict']=='UNRESOLVED':continue
    c=row['circuit'];a=load(ROOT,c,'143')[1];b=load(ROOT,c,'200')[1]
    exact=[];mc=[];rng=np.random.default_rng(20260905)
    if row['constant']:exact=mc=[0.]*400
    else:
        for i in range(400):
            j=rng.integers(0,200,200);aa=a[j];bb=b[j];pc=call(aa,bb)[0];exact.append(1-pc if row['verdict']=='REGRESSION' else pc)
            sa=aa[rng.integers(0,200,(400000,3))].sum(1);sb=bb[rng.integers(0,200,(400000,3))].sum(1)
            v=float(np.mean(10*sb>=11*sa));mc.append(1-v if row['verdict']=='REGRESSION' else v)
    cm=np.percentile(mc,[2.5,97.5]);ce=np.percentile(exact,[2.5,97.5]);want=np.array([float(saved[c]['error_ci_lo']),float(saved[c]['error_ci_hi'])])
    rec=dict(circuit=c,mc_ci=cm.tolist(),exact_same_stream_ci=ce.tolist(),saved_ci=want.tolist(),max_error=float(max(abs(cm-want))))
    out.append(rec);print(json.dumps(rec),flush=True)
    (BASE/'bootstrap_replay.json').write_text(json.dumps(out,indent=2))
assert len(out)==36 and max(r['max_error'] for r in out)<=.00000051
