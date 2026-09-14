import sys,time,json
from pathlib import Path
B=Path(__file__).resolve().parent
sys.path.insert(0,str(B/'snapshot'))
import mutation_test as m
r=[]
for i in range(2):
 d=B/('snapshot_probe_'+str(i));d.mkdir(exist_ok=True);t=time.time();m.snapshot(str(d));r.append({'i':i,'seconds':time.time()-t,'files':len(list(d.rglob('*'))),'arm':(d/m.ARM).exists()})
print(json.dumps(r))
