"""Disposable v3 mutation runner. Does not modify snapshot or original repository.
Usage python mutations.py ID [--full]; IDs A B C D E F G H I J.
Each clone retains the target HEAD so the supplied git-archive self-test can run.
"""
import sys,os,json,csv,subprocess,time
from pathlib import Path
BASE=Path(__file__).resolve().parent
case=sys.argv[1]; dst=BASE/('mut'+case)
if dst.exists():
    assert case=='K' and not subprocess.check_output(['git','-C',str(dst),'status','--porcelain']), 'Existing case: refusing overwrite'
else:subprocess.run(['git','clone','--quiet','--shared',str(BASE/'snapshot'),str(dst)],check=True)
arm=dst/'results/raw/prereg/knn_n67_heavy-hex_q200.jsonl'
summary=dst/'results/summary/prereg_heavy-hex.csv'
rows=list(csv.DictReader(summary.open())); fields=list(rows[0]); before={}
def writecsv():
    with summary.open('w',newline='',encoding='utf-8') as f:
        w=csv.DictWriter(f,fieldnames=fields);w.writeheader();w.writerows(rows)
def editraw(mode):
    records=[json.loads(l) for l in arm.read_text().splitlines()];done=False
    for r in records:
        if r.get('record')!='run':continue
        if mode=='scale':r['two_q']=round(r['two_q']*1.09)
        elif not done:
            before.update(r)
            r['two_q']=10000000 if mode=='large' else r['two_q']+(3000 if mode=='boundary' else 1)
            done=True
    arm.write_text('\n'.join(json.dumps(r) for r in records)+'\n',encoding='utf-8')
if case=='A':editraw('large')
elif case=='B':editraw('small')
elif case=='C':editraw('scale')
elif case=='C2':editraw('boundary')
elif case=='D':rows[0]['error_rate']='0.999999';writecsv()
elif case=='E':
    p=dst/'PAPER.md';t=p.read_text(encoding='utf-8');s=t.replace('| risk ≥ 5% | 7 / 26 |','| risk ≥ 5% | 9 / 26 |',1);assert t!=s;p.write_text(s,encoding='utf-8')
elif case in ('F','G'):
    # Select largest baseline mean to test tolerance-sized raw changes for F.
    if case=='F':
        candidates=[]
        for p in (dst/'results/raw/prereg').glob('*_q143.jsonl'):
            rr=[json.loads(l) for l in p.read_text().splitlines()]; a=[r['two_q'] for r in rr if r.get('record')=='run'];candidates.append((sum(a)/len(a),p))
        _,p=max(candidates);arm=p.with_name(p.name.replace('_q143','_q200'))
    editraw('small')
elif case=='H':
    for r in rows:
        if r['error_ci_lo']!='':r['error_ci_lo']='0.900000';r['error_ci_hi']='0.999999'
    writecsv()
elif case=='I':
    p=dst/'PAPER.md';t=p.read_text(encoding='utf-8');s=t.replace('+44.060%','+94.060%');assert t!=s;p.write_text(s,encoding='utf-8')
elif case=='J':arm.write_bytes(arm.read_bytes().replace(b'\r\n',b'\n').replace(b'\n',b'\r\n'))
elif case=='K':
    p=dst/'PAPER.md';t=p.read_text(encoding='utf-8')
    table='\n'.join(l for l in t.splitlines() if l.startswith('| risk ') and '/ 26' in l)
    assert '12 / 26' in table and '7 / 26' in table and '4 / 26' in table
    changed=table.replace('12 / 26','0 / 26').replace('7 / 26','0 / 26').replace('4 / 26','0 / 26')
    assert table in t
    p.write_text('<!-- Preserved previous table for editorial reference\n'+table+'\n-->\n\n'+t.replace(table,changed),encoding='utf-8')
else:raise SystemExit('bad case')
env=dict(os.environ,PYTHONUTF8='1',PYTHONDONTWRITEBYTECODE='1',PYTHONUNBUFFERED='1',BENCHPRESS_PATH=r'C:\Users\User\Desktop\benchpress_test')
def run(label,args):
    start=time.time()
    with (BASE/f'mut{case}_{label}.log').open('w',encoding='utf-8') as f:
        p=subprocess.run([sys.executable,*args],cwd=dst,env=env,stdout=f,stderr=subprocess.STDOUT)
    return dict(stage=label,returncode=p.returncode,seconds=time.time()-start)
results=[]
if case=='G':
    # Regenerate the changed circuit with the project's own complete original analysis.
    command="import csv,numpy as np;from prereg_analysis import analyse;p='results/summary/prereg_heavy-hex.csv';rs=list(csv.DictReader(open(p)));fields=list(rs[0]);r=analyse('knn_n67',.1,3,np.random.default_rng(20260906));rs=[r if q['circuit']=='knn_n67' else q for q in rs];f=open(p,'w',newline='');w=csv.DictWriter(f,fieldnames=fields);w.writeheader();w.writerows(rs);f.close()"
    results.append(run('regenerate',['-c',command]))
if case in ('F','G'):results.append(run('manifest',['raw_integrity.py','--write']))
if '--full' in sys.argv:results.append(run('full',['verify.py']))
else:
    for label,args in [('science',['raw_endpoint.py','--json',str(BASE/f'mut{case}_raw.json')]),('integrity',['raw_integrity.py']),('paper',['paper_check.py'])]:results.append(run(label,args))
(BASE/f'mut{case}_result.json').write_text(json.dumps(dict(case=case,arm=str(arm.relative_to(dst)),before=before,results=results),indent=2))
print(case,results,flush=True)
