import json,hashlib,subprocess
from pathlib import Path
import numpy as np
B=Path(__file__).resolve().parent;R=B/'snapshot';BP=Path(r'C:\Users\User\Desktop\benchpress_test')
pin=json.loads((R/'results/raw/benchpress_pin.json').read_text());out={}
out['corpus_matches']=sum(hashlib.sha256((BP/v['relpath']).read_bytes()).hexdigest()==v['sha256'] for v in pin['circuits'].values());out['corpus_total']=len(pin['circuits'])
out['module_matches']=sum(hashlib.sha256((BP/k).read_bytes()).hexdigest()==v for k,v in pin['benchpress_module_sha256'].items())
out['module_canonicalization']=[]
for k,v in pin['benchpress_module_sha256'].items():
    work=(BP/k).read_bytes();blob=subprocess.check_output(['git','-C',str(BP),'show','HEAD:'+k]);lf=work.replace(b'\r\n',b'\n')
    out['module_canonicalization'].append(dict(path=k,recorded=v,checkout_sha=hashlib.sha256(work).hexdigest(),git_blob_sha=hashlib.sha256(blob).hexdigest(),lf_sha=hashlib.sha256(lf).hexdigest(),lf_equals_git_blob=lf==blob,lf_passes_verifier_hash=hashlib.sha256(lf).hexdigest()==v))
expected=sorted(set(np.random.default_rng(20260904).integers(7,2**31-1,400).tolist()))[:200];out['primary_metadata']=[]
for p in sorted((R/'results/raw/prereg').glob('*.jsonl')):
    rs=[json.loads(l) for l in p.read_text().splitlines()];runs=[r for r in rs if r.get('record')=='run'];env=[r for r in rs if r.get('record')=='env']
    out['primary_metadata'].append(dict(file=p.name,n=len(runs),seeds_match=sorted(r['seed'] for r in runs)==expected,processes=len(set(r['pid'] for r in runs)),env_records=len(env),hashseeds=sorted(set(r.get('hashseed') for r in env)),gates=sorted(set(r.get('two_q_gate') for r in runs)),topologies=sorted(set(r['topology'] for r in runs))))
out['original_head']=subprocess.check_output(['git','-C',r'C:\Users\User\Desktop\research\qvalidation','rev-parse','HEAD']).decode().strip()
out['original_tracked_status']=subprocess.check_output(['git','-C',r'C:\Users\User\Desktop\research\qvalidation','status','--porcelain','--untracked-files=no']).decode()
(B/'metadata_checks.json').write_text(json.dumps(out,indent=2));print({k:v for k,v in out.items() if k!='primary_metadata'});print('all seeds',all(r['seeds_match'] for r in out['primary_metadata']),'process counts',sorted(set(r['processes'] for r in out['primary_metadata'])))
