"""Inspect user-identified staged publication; writes only to audit scratch directory."""
import sys,json,hashlib,zipfile,subprocess,re,difflib,io,tarfile
from pathlib import Path
B=Path(__file__).resolve().parent;sys.path.insert(0,str(B/'pdfdeps'));import fitz
STAGE=Path(r'C:\Users\User\AppData\Local\Temp\claude\c--Users-User-Desktop-web\7bd3eeda-6b86-4eb7-b123-ca645ad18633\scratchpad\v3_upload')
doc=fitz.open(STAGE/'paper.pdf');texts=[p.get_text() for p in doc];text=''.join(texts)
(B/'staged_pdf_text.txt').write_text(text,encoding='utf-8')
phrases=['largely induced','unresolvable','41%','44.060','cannot resolve','monotone','0.661','before the second machine','one seed_transpiler','0.18.1','0 of 24','10.9','12 / 26','7 / 26','4 / 26','under a minute']
out={'pdf_bytes':(STAGE/'paper.pdf').stat().st_size,'pdf_sha256':hashlib.sha256((STAGE/'paper.pdf').read_bytes()).hexdigest(),'pages':len(doc),'text_characters':len(text),'phrases':{s:[i+1 for i,t in enumerate(texts) if s in t] for s in phrases},'metadata':doc.metadata}
for i,p in enumerate(doc):p.get_pixmap(matrix=fitz.Matrix(1,1)).save(str(B/f'pdf_page_{i+1:02d}.png'))
if (B/'rebuilt.pdf').exists():
    rebuilt=fitz.open(B/'rebuilt.pdf');rt=''.join(p.get_text() for p in rebuilt);(B/'rebuilt_pdf_text.txt').write_text(rt,encoding='utf-8')
    norm=lambda t:re.sub(r'\s+','',t).replace('\u00ad','')
    out['rebuilt']={'pages':len(rebuilt),'whitespace_normalized_text_equal':norm(rt)==norm(text),'sha256':hashlib.sha256((B/'rebuilt.pdf').read_bytes()).hexdigest()}
    diff=list(difflib.unified_diff(text.splitlines(),rt.splitlines(),fromfile='staged',tofile='rebuilt'))
    (B/'pdf_text_diff.txt').write_text('\n'.join(diff),encoding='utf-8')
out['stage_files']={p.name:hashlib.sha256(p.read_bytes()).hexdigest() for p in STAGE.iterdir() if p.is_file() and p.name in ['paper.pdf','qvalidation-code-and-data.zip','COMMIT_TIMESTAMPS.txt']}
z=STAGE/'qvalidation-code-and-data.zip'
if z.exists():
    with zipfile.ZipFile(z) as f:
        names=f.namelist();out['archive']={'entries':len(names),'paper_paths':[x for x in names if x.endswith('PAPER.md')],'css_paths':[x for x in names if x.endswith('.css')]}
        target=(B/'snapshot/PAPER.md').read_text(encoding='utf-8')
        out['archive']['paper_matches']={n:f.read(n).decode('utf-8').replace('\r\n','\n')==target for n in names if n.endswith('PAPER.md')}
        archived=subprocess.check_output(['git','-C',str(B/'snapshot'),'archive','HEAD'])
        with tarfile.open(fileobj=io.BytesIO(archived)) as tar:
            expected={r.name:hashlib.sha256(tar.extractfile(r).read()).hexdigest() for r in tar if r.isfile()}
        actual={n.removeprefix('qvalidation/'):hashlib.sha256(f.read(n)).hexdigest() for n in names if not n.endswith('/')}
        out['archive']['mismatches']=[n for n in expected if actual.get(n)!=expected[n]]
        out['archive']['extra_paths']=sorted(set(actual)-set(expected))
        out['archive']['tracked_files']=len(expected)
(B/'pdf_audit.json').write_text(json.dumps(out,indent=2));print(json.dumps(out,indent=2))
