import os,sys,subprocess,json,shutil,hashlib
from pathlib import Path
B=Path(__file__).resolve().parent;S=B/'snapshot';sys.path.insert(0,str(S));import mutation_test as mt
env=dict(os.environ,BENCHPRESS_PATH=r'C:\Users\User\Desktop\benchpress_test',PYTHONUTF8='1',PYTHONDONTWRITEBYTECODE='1')
out=[]
def run(case,args,cwd=S,environ=env):
    p=subprocess.run(args,cwd=cwd,env=environ,capture_output=True,text=True,encoding='utf8');t=p.stdout+p.stderr;(B/(case+'.log')).write_text(t,encoding='utf8');r=dict(case=case,exit=p.returncode,state=mt.classify(p.returncode,t));out.append(r);(B/'environment_results.json').write_text(json.dumps(out,indent=2));print(json.dumps(r),flush=True);return t
run('pdf_powershell_environment',[sys.executable,'pdf_binding.py'])
run('pdf_gitbash_environment',[r'C:\Program Files\Git\bin\bash.exe','-lc','"'+sys.executable.replace('\\','/')+'" pdf_binding.py'])
run('pdf_empty_path',[sys.executable,'pdf_binding.py'],environ=dict(env,PATH=''))
code="import pdf_binding as p,builtins; p.find_pdftotext=lambda:None; old=builtins.__import__; builtins.__import__=lambda name,*a,**k: (_ for _ in ()).throw(ImportError('controlled missing PDF library')) if name=='fitz' else old(name,*a,**k); p.main()"
run('pdf_no_extractor',[sys.executable,'-c',code])
# Baseline PDF placement/numeric reference for API-level near variants, without rebuilding science.
code="import pdf_binding as p,json; t=p.pdf_text(); s=open('PAPER.md',encoding='utf8').read(); print(json.dumps({'extractor':p.find_pdftotext(),'baseline_problems':p.check(t,s,echo=lambda *x:None)}))"
run('pdf_reference',[sys.executable,'-c',code])
for ending in ['LF','CRLF']:
    old=Path(r'C:\Users\User\AppData\Local\Temp\astra-v4-4531d97-36c0767c')/('benchpress_five_'+ending)
    run('pin_no_git_'+ending,[sys.executable,'pin_check.py'],environ=dict(env,BENCHPRESS_PATH=str(old)))
run('pin_git_control',[sys.executable,'pin_check.py'])
# A matching checkout from an unexpected revision is not equivalent to a valid pin.
bp=B/'bp_empty_git';bp.mkdir();subprocess.run(['git','init','--quiet',str(bp)],check=True)
for rel in json.loads((S/'results/raw/benchpress_pin_canonical.json').read_text())['benchpress_module_canonical_sha256']:
    dst=bp/rel;dst.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(Path(r'C:\Users\User\Desktop\benchpress_test')/rel,dst)
run('pin_unborn_git',[sys.executable,'pin_check.py'],environ=dict(env,BENCHPRESS_PATH=str(bp)))
history=B/'history_change';subprocess.run(['git','clone','--quiet','--shared',str(S),str(history)],check=True)
p=history/'results/raw/prereg/multiplier_n45_heavy-hex_q200.jsonl';rows=[json.loads(l) for l in p.read_text().splitlines()]
next(r for r in rows if r.get('record')=='run')['two_q']+=1;p.write_text('\n'.join(json.dumps(r) for r in rows)+'\n')
run('history_manifest',[sys.executable,'raw_integrity.py','--write'],cwd=history)
run('history_changed',[sys.executable,'v2_anchor.py'],cwd=history)
offline=B/'offline';subprocess.run(['git','clone','--quiet','--depth','1',S.as_uri(),str(offline)],check=True)
run('offline_pristine',[sys.executable,'v2_anchor.py'],cwd=offline)
shutil.copyfile(p,offline/p.relative_to(history));anchor=offline/'results/raw/V2_EVIDENCE_ANCHOR.json';j=json.loads(anchor.read_text());key=p.relative_to(history).as_posix();blob=p.read_bytes().replace(b'\r\n',b'\n');j['files'][key]={'sha256':hashlib.sha256(blob).hexdigest(),'bytes':len(blob)};anchor.write_text(json.dumps(j))
run('offline_changed_transcript',[sys.executable,'v2_anchor.py'],cwd=offline)
run('offline_write_refused',[sys.executable,'v2_anchor.py','--write-anchor'],cwd=offline)
# Exercise actual built-in U fixture on this environment, with its declared reason.
u=B/'builtin_u';u.mkdir();mt.snapshot(str(u));built=mt.mut_U(str(u));t=run('builtin_u',[sys.executable,'pdf_binding.py'],cwd=u);(B/'builtin_u_result.json').write_text(json.dumps({'fixture':built,'declared_reason_found':'appears NOWHERE in PAPER.md' in t}))
