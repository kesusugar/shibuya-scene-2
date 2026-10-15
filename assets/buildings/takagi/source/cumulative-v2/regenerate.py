"""Rebuild both sequential stages with Blender 4.2.3 from bundled pinned sources."""
import bpy,sys,subprocess,hashlib,shutil
from pathlib import Path
R=Path(__file__).resolve().parent
assert bpy.app.version[:3]==(4,2,3), 'Use Blender 4.2.3'
for rel in ['stages/facade','asset']:
 p=R/rel
 (p/'web').mkdir(parents=True,exist_ok=True)
 subprocess.run([bpy.app.binary_path,'-b','-t','6','--python',str(p/'source/blender/build.py'),'--','--no-render'],check=True)
 expected='d081d33fe9b358769264f0277962248f369f276a04dffd91e22214445f93609f' if rel=='stages/facade' else '94d893287d20d7155e626a4198a2509719aa66342e1b9620b002e21ba6d4b9fd'
 assert hashlib.sha256((p/'web/takagi.glb').read_bytes()).hexdigest()==expected
 if rel=='stages/facade':
  assert (p/'web/takagi.glb').read_bytes()==(R/'asset/source/data/baseline.glb').read_bytes()
assert (R/'stages/facade/source/data/stats.json').read_bytes()==(R/'asset/source/data/facade_stats.json').read_bytes()
assert hashlib.sha256((R/'asset/source/data/stats.json').read_bytes()).hexdigest()=='4063c3c559c57c050c8561dfb40a56f42cd6e9e6855436e3ea863fb2bba36179'
print('PASS: facade and final GLB byte-identical to the pinned stages.')
