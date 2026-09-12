"""Validate and package audit outputs, excluding disposable repositories/runtimes."""
import json,hashlib,re,zipfile,shutil
from pathlib import Path
B=Path(__file__).resolve().parent
report=(B/'ASTRA_FINAL_HOSTILE_AUDIT.md').read_text(encoding='utf-8')
assert report.rstrip().endswith('CORE SURVIVES MAJOR CORRECTIONS')
verdicts=['PAPER FAILS UNDER ATTACK','CORE SURVIVES MAJOR CORRECTIONS','CORE SURVIVES MINOR CORRECTIONS','READY TO PUBLISH']
assert sum(report.count(v) for v in verdicts)==1
findings=json.loads((B/'findings.json').read_text());assert len(findings)==20
assert all(r['severity'] in ['FATAL','MAJOR','MINOR','NOT ISSUE'] for r in findings)
for name in ['baseline.log','mutH_full.log','mutK_full.log','mutF_full.log']:
    text=(B/name).read_text(encoding='utf-8-sig');assert 'All 9 checks passed' in text,name
for p in re.findall(r'\]\((C:/[^)]+)\)',report):
    p=re.sub(r':\d+$','',p);assert Path(p).is_file(),p
ci=json.loads((B/'bootstrap_replay.json').read_text());assert len(ci)==36 and max(r['max_error'] for r in ci)<=.00000051
pdf=json.loads((B/'pdf_audit.json').read_text());assert pdf['rebuilt']['whitespace_normalized_text_equal'] and not pdf['archive']['mismatches']
shutil.copyfile(r'C:\Users\User\Desktop\bad\paper_style.css',B/'pdf_build_input.css')
files=sorted(p for p in B.iterdir() if p.is_file() and (p.suffix in ['.py','.md','.json','.log','.txt','.css'] or p.name=='pdf_contact_sheet.png') and p.name!='AUDIT_FILES_SHA256.txt')
manifest='\n'.join(hashlib.sha256(p.read_bytes()).hexdigest()+'  '+p.name for p in files)+'\n'
(B/'AUDIT_FILES_SHA256.txt').write_text(manifest,encoding='utf-8');files.append(B/'AUDIT_FILES_SHA256.txt')
with zipfile.ZipFile(B/'ASTRA_FINAL_HOSTILE_AUDIT_PACKAGE.zip','w',zipfile.ZIP_DEFLATED) as z:
    for p in files:z.write(p,p.name)
print('Packaged',len(files),'files;bytes',(B/'ASTRA_FINAL_HOSTILE_AUDIT_PACKAGE.zip').stat().st_size)
print('Severity counts',{s:sum(f['severity']==s for f in findings) for s in sorted(set(f['severity'] for f in findings))})
