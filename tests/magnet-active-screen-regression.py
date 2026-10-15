"""Run from repository root with Python 3; standard library only."""
from pathlib import Path
import importlib.util,tempfile,hashlib,json
root=Path(__file__).resolve().parents[1]
a=root/'assets/buildings/magnet';p=a/'source/active-screen-v1'
s=importlib.util.spec_from_file_location('correct_screen',p/'source/correct_screen.py');m=importlib.util.module_from_spec(s);s.loader.exec_module(m)
with tempfile.TemporaryDirectory() as d:
 out=Path(d);r=m.repair(p/'inputs',out)
 assert (out/'magnet_signs_2025.glb').read_bytes()==(a/'web/magnet_signs_2025.glb').read_bytes()
 assert (out/'signage_2025.json').read_bytes()==(a/'source/data/signage_2025.json').read_bytes()
 assert r['all_triangles']==16092 and r['all_meshes']==31 and r['all_materials']==19
 assert r['changed_binary_bytes']==24 and r['changed_position_components']==8
 assert abs(r['runtime_offset_m']+0.093)<1e-10
 manifest=json.loads((a/'manifest.json').read_text())
 for f in ['web/magnet_signs_2025.glb','source/data/signage_2025.json']:
  b=(a/f).read_bytes();assert manifest['files'][f]=={'bytes':len(b),'sha256':hashlib.sha256(b).hexdigest()}
 print('PASS: exact regeneration, scope, materials, nodes, parent hierarchy, images, datum and canonical hashes')
