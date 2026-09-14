import subprocess,time
start=time.time()
try:
 p=subprocess.run(['git','archive','HEAD'],stdout=subprocess.DEVNULL,stderr=subprocess.PIPE,timeout=20)
 print(p.returncode,round(time.time()-start,2),p.stderr[:200])
except subprocess.TimeoutExpired:
 print('archive timed out after 20s')
