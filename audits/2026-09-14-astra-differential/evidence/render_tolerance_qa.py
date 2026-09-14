import os,sys,subprocess,json,shutil,collections
from pathlib import Path
import numpy as np
B=Path(__file__).resolve().parent;S=B/'snapshot';D=B/'rendered';subprocess.run(['git','clone','--quiet','--shared',str(S),str(D)],check=True)
env=dict(os.environ,BENCHPRESS_PATH=r'C:\Users\User\Desktop\benchpress_test',PYTHONUTF8='1',PYTHONDONTWRITEBYTECODE='1')
sys.path.insert(0,r'C:\Users\User\AppData\Local\Temp\astra-v3-839ac80-h1_mhdhj\pdfdeps');sys.path.insert(0,str(S));import fitz,prereg_analysis as pa
out=[]
def cmd(name,args):
    p=subprocess.run(args,cwd=D,env=env,capture_output=True,text=True,encoding='utf8');(B/(name+'.log')).write_text(p.stdout+p.stderr,encoding='utf8');out.append({'case':name,'exit':p.returncode});return p.returncode
for case in ['abstract_original','long_html']:
    shutil.copyfile(B/(case+'.md'),D/'PAPER.md');assert cmd(case+'_build',[r'C:\Program Files\Git\bin\bash.exe','publish/build_paper.sh','publish/paper.pdf'])==0
    cmd(case+'_pdf_check',[sys.executable,'pdf_binding.py']);shutil.copyfile(D/'publish/paper.pdf',B/(case+'_rendered.pdf'))
    d=fitz.open(D/'publish/paper.pdf');texts=[p.get_text() for p in d]
    if case=='abstract_original':page=d[0]
    else:page=next(p for p in d if '4.2 Magnitude' in p.get_text())
    page.get_pixmap(matrix=fitz.Matrix(1.25,1.25)).save(B/(case+'_render.png'))
css=D/'publish/paper_style.css';hidden=D/'publish/style_temporarily_renamed.css';css.rename(hidden)
try:cmd('missing_stylesheet',[r'C:\Program Files\Git\bin\bash.exe','publish/build_paper.sh','publish/paper.pdf'])
finally:hidden.rename(css)
baseline=fitz.open(S/'publish/paper.pdf');baseline[0].get_pixmap(matrix=fitz.Matrix(1.25,1.25)).save(B/'styled_baseline.png')
sizes=collections.Counter(round(s['size'],2) for p in baseline for b in p.get_text('dict')['blocks'] if 'lines' in b for l in b['lines'] for s in l['spans'])
style={'pages':len(baseline),'page_size_pt':list(baseline[0].rect),'most_common_font_sizes':sizes.most_common(5),'first_page_fonts':sorted({f[3] for f in baseline[0].get_fonts()})}
tests=[]
for a,b in [(100,110),(10_000_000_000,11_000_000_001),(100_000,110_001)]:
    seeds=np.arange(200,dtype=np.int64)
    pa.load_seeded=lambda c,v,topo='heavy-hex':(seeds,np.full(200,a if v=='143' else b,dtype=np.int64),v)
    r=pa.analyse('constant',.1,3,np.random.default_rng(20260906));tests.append({'A':a,'B':b,'verdict':r['verdict'],'tie_epsilon':pa.TIE_EPS})
(B/'render_tolerance_results.json').write_text(json.dumps({'commands':out,'styling':style,'threshold':tests},indent=2));print(json.dumps({'commands':out,'styling':style,'threshold':tests},indent=2))
