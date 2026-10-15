"""Reproduce the full completed chain in a temporary copy, then sync current runtime. Python 3."""
from pathlib import Path
import subprocess,sys,shutil,tempfile,argparse,hashlib
A=Path(__file__).resolve().parents[2]
p=argparse.ArgumentParser();p.add_argument('--blender',required=True);args=p.parse_args();B=str(Path(args.blender).resolve())
def same(a,b):assert a.read_bytes()==b.read_bytes(),str(a)+' does not exactly match pinned input'
with tempfile.TemporaryDirectory(prefix='parco-rebuild-') as tmp:
 W=Path(tmp)/'parco';shutil.copytree(A,W)
 def blend(p,*extra):subprocess.run([B,'-b','-t','2','--python-exit-code','1','-P',str(p),*extra],check=True)
 blend(W/'source/blender/build_podium.py');same(W/'web/parco.glb',A/'source/roof-repair-v1/prior.glb')
 blend(W/'source/roof-repair-v1/repair.py');same(W/'web/parco.glb',A/'source/terrace-v1/inputs/roof22-corrected-base.glb')
 T=W/'source/terrace-v1';subprocess.run([sys.executable,str(T/'scripts/rebuild.py'),'--blender',B],check=True)
 same(T/'parco_terrace_candidate.glb',A/'source/terrace-v1/parco_terrace_candidate.glb')
 shutil.copy2(T/'parco_terrace_candidate.glb',A/'web/parco.glb')
print('FULL_CHAIN_PASS',hashlib.sha256((A/'web/parco.glb').read_bytes()).hexdigest())
