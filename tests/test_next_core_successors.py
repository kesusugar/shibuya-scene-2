"""Reconstructed v3 bounded successor tests; original lost test bytes are not claimed."""
from pathlib import Path
import unittest,json,hashlib,struct,tempfile,shutil,subprocess,sys,os
A=Path.cwd()/'assets/buildings'
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def read(p):
 b=p.read_bytes();assert b[:4]==b'glTF';assert struct.unpack_from('<I',b,8)[0]==len(b);n=struct.unpack_from('<I',b,12)[0];return json.loads(b[20:20+n]),b,28+n
class NextCoreTests(unittest.TestCase):
 def test_exact_stage_and_final_pins(self):
  pins={'west-block/source/grille-apron-v2/inputs/web/west-block.glb':'ea60ca2848e1ecc981dc2bf42d9de389d52e3b36b97d17357edc621da82ccb16','west-block/source/grille-apron-v2/web/west-block.glb':'884f6a555d59ff3736f610953c2f2151a150d5452aee502008086086e595dd6f','west-block/source/awning-support-repair/inputs/current/west-block.glb':'884f6a555d59ff3736f610953c2f2151a150d5452aee502008086086e595dd6f','west-block/web/west-block.glb':'3e9d4573f2d88d65877583f23442740fac333849d0c4f7877202b6905812026a','ekimae/source/door-envelope-repair/input/ekimae.glb':'6813569028d675817d20e16a68ac50f00962a3a18841b5e3980bacb634d3f92d','ekimae/web/ekimae.glb':'4ecb3412bc946a8aa88ac9ab0ac4d9f415b8d5bcadac819ead9d8d59885b89c8'}
  for p,h in pins.items():self.assertEqual(sha(A/p),h,p)
 def test_grille_preserves_original_binary_and_definitions(self):
  d=A/'west-block/source/grille-apron-v2';j,b,o=read(d/'inputs/web/west-block.glb');k,c,q=read(d/'web/west-block.glb');self.assertEqual(b[o:],c[q:q+len(b)-o])
  for key in j:
   if key not in ['buffers','scenes']:self.assertEqual(j[key],k[key][:len(j[key])] if isinstance(j[key],list) else k[key],key)
  expected=json.loads(json.dumps(j['scenes']));expected[j.get('scene',0)]['nodes'].append(len(j['nodes']));self.assertEqual(expected,k['scenes'])
 def test_support_only_declared_bytes(self):
  d=A/'west-block/source/awning-support-repair';j,b,o=read(d/'inputs/current/west-block.glb');k,c,q=read(A/'west-block/web/west-block.glb');r=json.loads((d/'evidence/validation.json').read_text());self.assertEqual(j,k);self.assertEqual(len(b),len(c));self.assertEqual((r['vertices'],r['triangles']),(48,24));allowed={i for x,y in r['allowed_byte_ranges'] for i in range(x,y)};self.assertTrue(all(x==y or i in allowed for i,(x,y) in enumerate(zip(b,c))))
 def test_ekimae_precise_binary_and_metadata_exception(self):
  d=A/'ekimae/source/door-envelope-repair';j,b,o=read(d/'input/ekimae.glb');k,c,q=read(A/'ekimae/web/ekimae.glb');r=json.loads((d/'evidence/audit.json').read_text());delta=json.loads((d/'evidence/json_delta.json').read_text());self.assertEqual(len(delta),1);self.assertEqual((delta[0]['accessor'],delta[0]['field']),(51,'min'));j['accessors'][51]['min']=delta[0]['after'];self.assertEqual(j,k);allowed={i-o for x,y in r['allowed_position_ranges'] for i in range(x,y)};self.assertEqual(len(b)-o,len(c)-q);self.assertTrue(all(x==y or i in allowed for i,(x,y) in enumerate(zip(b[o:],c[q:]))));self.assertEqual(sum(x['vertices'] for x in r['selection']),168);self.assertEqual(sum(x['triangles'] for x in r['selection']),84)
 def test_unchanged_signs_datum_and_source(self):
  b=A/'west-block'
  for f in ['signs-2025-01.glb','viewer.json']:self.assertEqual(sha(b/'web'/f),sha(b/'source/awning-support-repair/inputs/current'/f))
  b=A/'ekimae';pins=json.loads((b/'source/door-envelope-repair/evidence/accepted_source_pins.json').read_text())
  for f in ['web/signs-2025-11.glb','web/viewer.json','source/blender/build_ekimae.py','source/blender/facade_detail.py']:self.assertEqual(sha(b/f),pins[f])
 def test_regenerate_and_geometric_validators_without_mutating_sources(self):
  for asset,slug,scripts in [('west-block','awning-support-repair',['source/regenerate.py']),('ekimae','door-envelope-repair',['source/repair.py','source/test_repair.py'])]:
   src=A/asset/'source'/slug
   with tempfile.TemporaryDirectory() as t:
    root=Path(t)/'package';shutil.copytree(src,root,ignore=shutil.ignore_patterns('*.blend','*.png','*.jpg','*.log'))
    for f in scripts:
     r=subprocess.run([sys.executable,str(root/f)],cwd=t,env={**os.environ,'PYTHONDONTWRITEBYTECODE':'1'},capture_output=True,text=True);self.assertEqual(r.returncode,0,r.stderr)
    self.assertEqual(sha(root/'web'/f'{asset}.glb'),sha(A/asset/'web'/f'{asset}.glb'))
if __name__=='__main__':unittest.main()
