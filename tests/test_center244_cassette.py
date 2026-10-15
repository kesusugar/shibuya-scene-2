"""Reconstructed v3 tests; immutable exact source, geometry, era and material scope."""
from pathlib import Path
import unittest,json,hashlib,struct,tempfile,shutil,subprocess,sys,os
A=Path.cwd()/'assets/buildings/center244';P=A/'source/cassette'
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def read(p):
 b=p.read_bytes();n=struct.unpack_from('<I',b,12)[0];return json.loads(b[20:20+n]),b[28+n:]
class CassetteTests(unittest.TestCase):
 def test_exact_pin_and_complete_additive_preservation(self):
  self.assertEqual(sha(P/'inputs/center244.glb'),'4a425ab97e75957cd3093fad9dec51ab9a72bbbdc9d93766b667772a2e59f597');self.assertEqual(sha(A/'web/center244.glb'),'39356586cd70837e24d0d17dd306a994f84f77826e134bb9ec15c214760115a1');j,b=read(P/'inputs/center244.glb');k,c=read(A/'web/center244.glb');self.assertEqual(len(b),523100);self.assertEqual(c[:len(b)],b)
  for key in j:
   if key not in ['buffers','scenes']:self.assertEqual(j[key],k[key][:len(j[key])] if isinstance(j[key],list) else k[key])
  scenes=json.loads(json.dumps(j['scenes']));scenes[j.get('scene',0)]['nodes'].append(len(j['nodes']));self.assertEqual(scenes,k['scenes'])
 def test_companions_and_inactive_era(self):
  pins=json.loads((P/'inputs/PINS.json').read_text())
  for f in ['signs-2025-01.glb','viewer.json','emissive_day.json','emissive_night.json']:self.assertEqual(sha(A/'web'/f),pins[f])
  self.assertNotIn('layers',json.loads((A/'web/viewer.json').read_text()))
 def test_portable_regeneration_geometric_scope_and_gap(self):
  with tempfile.TemporaryDirectory() as t:
   root=Path(t);shutil.copytree(P/'inputs',root/'inputs');shutil.copytree(P/'scripts',root/'scripts');(root/'evidence').mkdir()
   for f in ['add_cassette.py','verify.py']:
    r=subprocess.run([sys.executable,str(root/'scripts'/f)],cwd=t,env={**os.environ,'PYTHONDONTWRITEBYTECODE':'1'},capture_output=True,text=True);self.assertEqual(r.returncode,0,r.stderr)
   self.assertEqual(sha(root/'output/center244.glb'),sha(A/'web/center244.glb'));v=json.loads((root/'evidence/verification.json').read_text());self.assertEqual(v['added_triangles'],48);self.assertAlmostEqual(v['rear_trim_gap_m'],.015,places=5);self.assertFalse(v['physical_wall_contact'])
 def test_current_counts_material_totals_and_nonemission(self):
  total=dict(bytes=0,triangles=0,primitives=0);by={}
  for p in (A/'web').glob('*.glb'):
   j,b=read(p);total['bytes']+=p.stat().st_size
   for node in j['nodes']:
    if 'mesh' in node:
     for x in j['meshes'][node['mesh']]['primitives']:
      n=j['accessors'][x['indices']]['count']//3;total['triangles']+=n;total['primitives']+=1;name=j['materials'][x['material']]['name'].removeprefix('c244_');by[name]=by.get(name,0)+n
   if p.stem=='center244':
    for m in j['materials'][-2:]:self.assertNotIn('emissiveFactor',m);self.assertFalse(any('Texture' in k for k in m['pbrMetallicRoughness']))
  self.assertEqual(total,dict(bytes=1055044,triangles=8471,primitives=19));self.assertEqual(json.loads((A/'manifest.json').read_text())['stats'],total);s=json.loads((A/'source/data/stats.json').read_text());self.assertEqual(s['by_material'],by);self.assertEqual(s['triangles'],8471);self.assertEqual(s['primitives'],19)
if __name__=='__main__':unittest.main()
