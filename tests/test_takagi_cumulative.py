"""Bounded Takagi cumulative contract. Run from repository root; stdlib only."""
from pathlib import Path
import unittest,json,struct,hashlib,math,importlib.util,tempfile,shutil,subprocess,sys
A=Path('assets/buildings/takagi');P=A/'source/cumulative-v2'
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def read(p):
 b=p.read_bytes();assert struct.unpack_from('<III',b)==(0x46546c67,2,len(b));n=struct.unpack_from('<I',b,12)[0];return json.loads(b[20:20+n]),b[28+n:]
def semantic(p):
 j,b=read(p);out=[]
 for n in j['nodes']:
  assert set(n)<=set(['mesh','name'])
  for prim in j['meshes'][n['mesh']]['primitives']:
   payload=[]
   for key,i in [('indices',prim['indices']),*sorted(prim['attributes'].items())]:
    a=j['accessors'][i];v=j['bufferViews'][a['bufferView']];payload.append((key,json.dumps({k:x for k,x in a.items() if k!='bufferView'},sort_keys=True),json.dumps({k:x for k,x in v.items() if k!='byteOffset'},sort_keys=True),b[v.get('byteOffset',0):v.get('byteOffset',0)+v['byteLength']]))
   out.append((n['name'],json.dumps(j['materials'][prim['material']],sort_keys=True),payload))
 return sorted(out)
class Takagi(unittest.TestCase):
 def test_fixed_input_and_combined_export(self):
  self.assertEqual(sha(P/'review/main-b678e936.glb'),'5fe2ee53947ca18f72460da90ef5de1f849c687968a6b623e0db2e1cb5ce218d')
  self.assertEqual(sha(P/'stages/facade/source/data/baseline.glb'),sha(P/'review/main-b678e936.glb'))
  self.assertEqual(sha(P/'asset/web/takagi.glb'),'94d893287d20d7155e626a4198a2509719aa66342e1b9620b002e21ba6d4b9fd')
 def test_lossless_disjoint_partition(self):
  base=semantic(A/'web/takagi.glb');sign=semantic(A/'web/signs-2025-01.glb');self.assertEqual(sorted(base+sign),semantic(P/'asset/web/takagi.glb'));self.assertEqual(len(base),12);self.assertEqual(len(sign),4)
  self.assertTrue(all('takagi_billboard_' not in m for _,m,_ in base));self.assertTrue(all('takagi_billboard_' in m for _,m,_ in sign))
 def test_unregistered_dated_sign_and_unchanged_anchor(self):
  self.assertEqual((A/'web/viewer.json').read_bytes(),(P/'asset/web/viewer.json').read_bytes());self.assertNotIn('layers',json.loads((A/'web/viewer.json').read_text()))
  for f in ['emissive_day.json','emissive_night.json']:self.assertEqual((A/'web'/f).read_bytes(),(P/'asset/web'/f).read_bytes())
 def test_exact_current_counts_and_finite_positions(self):
  totals={'triangles':0,'primitives':0,'bytes':0};receipt=json.loads((P/'runtime-split.json').read_text())
  for name in ['takagi','signs-2025-01']:
   p=A/'web'/(name+'.glb');j,b=read(p);s={'triangles':0,'primitives':0,'bytes':p.stat().st_size}
   for m in j['meshes']:
    for pr in m['primitives']:
     self.assertEqual(pr.get('mode',4),4);s['primitives']+=1;s['triangles']+=j['accessors'][pr['indices']]['count']//3
     a=j['accessors'][pr['attributes']['POSITION']];v=j['bufferViews'][a['bufferView']];self.assertEqual(a['componentType'],5126);off=v.get('byteOffset',0)+a.get('byteOffset',0)
     for i in range(a['count']):self.assertTrue(all(math.isfinite(x) for x in struct.unpack_from('<3f',b,off+i*v.get('byteStride',12))))
   self.assertEqual({k:receipt[name][k] for k in s},s);self.assertEqual(receipt[name]['sha256'],sha(p))
   for k in totals:totals[k]+=s[k]
  self.assertEqual(totals,{'triangles':4919,'primitives':16,'bytes':398108});self.assertEqual(json.loads((A/'manifest.json').read_text())['stats'],totals)
 def test_roof_material_change_is_exactly_seven_and_source52_only_retriangulated(self):
  source=json.loads((P/'asset/source/data/plateau.json').read_text());ring=source['surfaces'][52]['ring'][:-1];self.assertEqual(len(ring),17)
  def roof(path):
   j,b=read(path);out=[]
   def acc(i):
    a=j['accessors'][i];v=j['bufferViews'][a['bufferView']];fmt={5123:'H',5125:'I',5126:'f'}[a['componentType']];w={'SCALAR':1,'VEC3':3}[a['type']];off=v.get('byteOffset',0)+a.get('byteOffset',0);return [struct.unpack_from('<'+fmt*w,b,off+k*v.get('byteStride',struct.calcsize(fmt)*w)) for k in range(a['count'])]
   for n in j['nodes']:
    if n['name']!='takagi_roof':continue
    for q in j['meshes'][n['mesh']]['primitives']:
     ps=acc(q['attributes']['POSITION']);ix=[x[0] for x in acc(q['indices'])];mat=j['materials'][q['material']]['name']
     for i in range(0,len(ix),3):
      xyz=tuple(tuple(ps[k]) for k in ix[i:i+3]);out.append((mat,xyz))
   return out
  old=roof(P/'review/main-b678e936.glb');new=roof(A/'web/takagi.glb')
  def is52(tr):return all(any(sum((a-b)**2 for a,b in zip((v[0],-v[2],v[1]),r))<1e-8 for r in ring) for v in tr)
  def oriented(tr):return min(tr[i:]+tr[:i] for i in range(3))
  before=[(m,oriented(t)) for m,t in old if not is52(t)];after=[(m,oriented(t)) for m,t in new if not is52(t)]
  recolored=[t for m,t in after if m=='takagi_fitted_crown_rib'];self.assertEqual(len(recolored),7)
  self.assertEqual(sorted(before),sorted(('takagi_roof' if m=='takagi_fitted_crown_rib' else m,t) for m,t in after))
  repaired=[t for m,t in new if is52(t)];self.assertEqual(len(repaired),15)
  old_vertices={v for m,t in old if is52(t) for v in t};new_vertices={v for t in repaired for v in t};self.assertEqual(old_vertices,new_vertices);self.assertEqual(len(new_vertices),17)
 def test_portable_split_regeneration(self):
  with tempfile.TemporaryDirectory() as t:
   a=Path(t)/'takagi';p=a/'source/cumulative-v2';shutil.copytree(P/'asset',p/'asset');shutil.copy2(P/'split_runtime.py',p/'split_runtime.py');(a/'source/data').mkdir(parents=True)
   subprocess.run([sys.executable,str(p/'split_runtime.py')],check=True,capture_output=True)
   for f in ['takagi.glb','signs-2025-01.glb']:self.assertEqual((a/'web'/f).read_bytes(),(A/'web'/f).read_bytes())
if __name__=='__main__':unittest.main()
