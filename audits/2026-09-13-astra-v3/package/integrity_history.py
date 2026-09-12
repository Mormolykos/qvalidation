"""Read-only Git identity audit plus disposable autocrlf checkouts."""
import subprocess,json,hashlib
from pathlib import Path
B=Path(__file__).resolve().parent;R=B/'snapshot'
def git(*args,root=R):return subprocess.check_output(['git','-C',str(root),*args])
sha=lambda b:hashlib.sha256(b).hexdigest()
manifest=json.loads((R/'results/raw/RAW_MANIFEST.json').read_text())['files'];out={'hashes':[]}
for name,rec in manifest.items():
    p='results/raw/prereg/'+name
    now=git('show','HEAD:'+p);old=git('show','17e08f3:'+p);work=(R/p).read_bytes()
    out['hashes'].append(dict(path=p,manifest=rec['sha256'],head=sha(now),v2=sha(old),checkout=sha(work),match=sha(now)==sha(old)==sha(work)==rec['sha256']))
out['all_raw_changed_paths']=git('diff','--name-only','17e08f3','HEAD','--','results/raw').decode().splitlines()
out['jsonl_changed_paths']=git('diff','--name-only','17e08f3','HEAD','--','results/raw/**/*.jsonl','results/raw/*.jsonl').decode().splitlines()
out['tracked_pdfs']=git('ls-files','*.pdf').decode().splitlines()
out['autocrlf']=[]
for value in ['true','false']:
    dest=B/('autocrlf_'+value)
    subprocess.run(['git','clone','--quiet','--shared','--no-checkout',str(R),str(dest)],check=True)
    subprocess.run(['git','-C',str(dest),'config','core.autocrlf',value],check=True)
    subprocess.run(['git','-C',str(dest),'checkout','--quiet','--detach','HEAD'],check=True)
    good=sum(sha((dest/r['path']).read_bytes())==r['manifest'] for r in out['hashes'])
    out['autocrlf'].append(dict(value=value,matches=good,total=len(manifest)))
paths=['PREREGISTRATION.md','prereg_analysis.py','_selected.txt','results/raw/prereg','results/raw','crossmachine','replication','followup.py','followup3.py','PAPER.md','V3_CORRECTION_LEDGER.md']
out['history']={p:git('log','--reverse','--format=%h %aI %cI %s','--',p).decode().splitlines() for p in paths}
out['status']=git('status','--porcelain','--untracked-files=no').decode()
(B/'integrity_history.json').write_text(json.dumps(out,indent=2));print(json.dumps({k:v for k,v in out.items() if k not in ['hashes','history']},indent=2));print('v2/head/manifest/checkout equal:',sum(r['match'] for r in out['hashes']))
