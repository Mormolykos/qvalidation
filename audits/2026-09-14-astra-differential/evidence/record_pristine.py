import subprocess,runpy,time,json,os
from pathlib import Path
B=Path(__file__).resolve().parent
S=B/'snapshot';os.chdir(S)
original=subprocess.run
counter=0

def recorded(*args,**kw):
 global counter
 counter+=1;i=counter;t=time.time()
 p=original(*args,**kw)
 (B/('stage_%02d.log'%i)).write_text((p.stdout or '')+(p.stderr or ''),encoding='utf8')
 with (B/'stage_results.jsonl').open('a',encoding='utf8') as f:f.write(json.dumps({'stage':i,'args':args[0],'exit':p.returncode,'seconds':time.time()-t})+'\n')
 print('Recorded stage',i,'exit',p.returncode,flush=True)
 return p
subprocess.run=recorded
runpy.run_path(str(S/'verify.py'),run_name='__main__')
