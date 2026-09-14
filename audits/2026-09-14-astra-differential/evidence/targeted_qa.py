import os,sys,json,csv,subprocess,shutil,copy
from pathlib import Path
B=Path(__file__).resolve().parent;S=B/'snapshot';D=B/'targeted';subprocess.run(['git','clone','--quiet','--shared',str(S),str(D)],check=True)
env=dict(os.environ,BENCHPRESS_PATH=r'C:\Users\User\Desktop\benchpress_test',PYTHONUTF8='1',PYTHONDONTWRITEBYTECODE='1')
sys.path.insert(0,str(S));sys.path.insert(0,r'C:\Users\User\AppData\Local\Temp\astra-v3-839ac80-h1_mhdhj\pdfdeps');import fitz,mutation_test as mt
results=[]
def run(case,args):
    p=subprocess.run([sys.executable,*args],cwd=D,env=env,capture_output=True,text=True,encoding='utf8');out=p.stdout+p.stderr;(B/(case+'.log')).write_text(out,encoding='utf8')
    r=dict(case=case,args=args,exit=p.returncode,state=mt.classify(p.returncode,out),traceback='Traceback (most recent call last)' in out);results.append(r);(B/'targeted_results.json').write_text(json.dumps(results,indent=2));print(json.dumps(r),flush=True);return out
csvp=D/'results/summary/prereg_heavy-hex.csv';base=list(csv.DictReader(csvp.open()));header=list(base[0])
for case in ['nan','inf','fractional','bool','duplicate','inverted','outside_interval','derived_flag','blank_required','extra_cell']:
    rows=copy.deepcopy(base);live=next(r for r in rows if r['error_ci_lo'])
    if case=='nan':
        for r in rows:
            if r['error_ci_lo']:r['error_ci_lo']=r['error_ci_hi']='NaN'
    elif case=='inf':live['error_ci_hi']='-Inf'
    elif case=='fractional':live['n_seeds']='200.9';live['k']='3.9'
    elif case=='bool':live['boundary']='not_verified'
    elif case=='duplicate':rows.append(dict(rows[0]))
    elif case=='inverted':live['error_ci_lo'],live['error_ci_hi']=live['error_ci_hi'],live['error_ci_lo']
    elif case=='outside_interval':live['error_rate']='0.999999'
    elif case=='derived_flag':live['error_excludes_zero']='False' if live['error_excludes_zero']=='True' else 'True'
    elif case=='blank_required':live['change_ci_lo_pct']=''
    with csvp.open('w',newline='') as f:w=csv.DictWriter(f,fieldnames=header);w.writeheader();w.writerows(rows)
    if case=='extra_cell':
        ls=csvp.read_text().splitlines();ls[1]+=',unlabelled-extra-cell';csvp.write_text('\n'.join(ls)+'\n')
    run('schema_'+case,['derived_binding.py']+(['--schema'] if case=='extra_cell' else []))
shutil.copyfile(S/'results/summary/prereg_heavy-hex.csv',csvp)
paper=D/'PAPER.md';source=(S/'PAPER.md').read_text(encoding='utf8');lines=source.splitlines();i=next(i for i,l in enumerate(lines) if l.startswith('| risk > 0'));table='\n'.join(lines[i-2:i+3])
for case in ['hidden_original','abstract_original','abstract_words','raw_html','long_html']:
    t=source
    if case=='hidden_original':t=t.replace(table,'<div style="display:none">\n\n'+table+'\n\n</div>\n\nThe primary risk interval excludes zero in zero of the twenty-six eligible circuits.',1)
    elif case=='abstract_original':t=t.replace('## Abstract','## Abstract\n\nThe primary risk interval excludes zero in only 7 / 26 eligible circuits.',1)
    elif case=='abstract_words':t=t.replace('## Abstract','## Abstract\n\nThe primary risk interval excludes zero in only seven of 26 eligible circuits.',1)
    elif case=='raw_html':t=t.replace(table,'<section>\n\n'+table+'\n\n</section>',1)
    elif case=='long_html':t=t.replace(table,'<div data-note="'+'x'*450+'" hidden>\n\n'+table+'\n\n</div'+' '*450+'>',1)
    paper.write_text(t,encoding='utf8');shutil.copyfile(paper,B/(case+'.md'));run(case,['manuscript_binding.py'])
paper.write_text(source,encoding='utf8')
for case in ['pdf_original','pdf_row_swap','pdf_drop']:
    doc=fitz.open(S/'publish/paper.pdf');edits=[]
    for page in doc:
        changes=[]
        pairs=[('10.9','99.9')] if case=='pdf_original' else [('7 / 26','4 / 26'),('4 / 26','7 / 26')] if case=='pdf_row_swap' else [('0.2462','')]
        for old,new in pairs:
            for rect in page.search_for(old):changes.append((rect,new));page.add_redact_annot(rect,fill=(1,1,1));edits.append(old)
        page.apply_redactions()
        for rect,new in changes:
            if new:page.insert_text((rect.x0,rect.y1-2),new,fontsize=10,fontname='tiro')
    assert edits,(case,'no matching PDF text')
    out=B/(case+'.pdf');doc.save(out);doc.close();shutil.copyfile(out,D/'publish/paper.pdf');run(case,['pdf_binding.py'])
shutil.copyfile(S/'publish/paper.pdf',D/'publish/paper.pdf')
faults=[]
for name,code in [('runtime',"raise RuntimeError('unrelated')"),('import',"import module_that_does_not_exist_qa"),('diagnostic_then_runtime',"print('✗ is not finite'); raise RuntimeError('unrelated later failure')")]:
    p=subprocess.run([sys.executable,'-c',code],env=env,capture_output=True,text=True,encoding='utf8');out=p.stdout+p.stderr;(B/('fault_'+name+'.log')).write_text(out,encoding='utf8');state=mt.classify(p.returncode,out);faults.append(dict(case=name,exit=p.returncode,state=state,nan_required_reason_present='is not finite' in out,traceback='Traceback (most recent call last)' in out))
(B/'fault_results.json').write_text(json.dumps(faults,indent=2));print(json.dumps(faults),flush=True)
