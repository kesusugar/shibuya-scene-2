"""Pinned-predecessor preservation, lossless repack and asset geometry contracts."""
from pathlib import Path
import json,sys,math,hashlib
sys.path.insert(0,str(Path(__file__).resolve().parent))
from glb_helpers import load,acc,sha,cross,sub,norm,dot
ROOT=Path(__file__).resolve().parents[1];OUT=ROOT/'output/combined'
a,ab=load(ROOT/'inputs/prior.glb');b,bb=load(OUT/'shibuya109.glb');r=json.loads((OUT/'report.json').read_text());pack=json.loads((OUT/'repack-report.json').read_text());mm={int(k):v for k,v in pack['mesh_map'].items()};removed={int(k):set(v) for k,v in r['removed_original_triangle_indices'].items()}
assert sha((ROOT/'inputs/prior.glb').read_bytes())=='a31e295bf8ce9bbef9ddc0c6164526db84cb7b08a6caf1957352be142854db90'
assert b['materials'][:len(a['materials'])]==a['materials']
protected=[]
for mi,m in enumerate(a['meshes']):
 old=m['primitives'][0];oldids=[x[0] for x in acc(a,ab,old['indices'])];mask=removed.get(mi,set());expected=[v for t in range(len(oldids)//3) if t not in mask for v in oldids[t*3:t*3+3]]
 if not expected:assert mi not in mm;continue
 assert mi in mm,(mi,m['name']);new=b['meshes'][mm[mi]]['primitives'][0]
 assert [v[0] for v in acc(b,bb,new['indices'])]==expected,m['name']
 assert old['material']==new['material']
 for k,oi in old['attributes'].items():assert acc(a,ab,oi)==acc(b,bb,new['attributes'][k]),(mi,k)
 if mi not in removed:protected.append(m['name'])
# Check all active vertex arrays and new faces. Four legacy wall degenerates are not silently repaired.
active={n['mesh'] for n in b['nodes'] if 'mesh'in n};triangles=primitives=0;new_degenerate=new_opposed=0
for mi in active:
 for p in b['meshes'][mi]['primitives']:
  primitives+=1;vs=acc(b,bb,p['attributes']['POSITION']);ns=acc(b,bb,p['attributes']['NORMAL']);ii=[v[0] for v in acc(b,bb,p['indices'])];triangles+=len(ii)//3
  assert all(math.isfinite(x) for v in vs+ns for x in v)
  if mi in [mm[k] for k in range(len(a['meshes'])) if k in mm]:continue
  for i in range(0,len(ii),3):
   ids=ii[i:i+3];v=[vs[k] for k in ids];n=cross(sub(v[1],v[0]),sub(v[2],v[0]));ln=norm(n)
   if ln<1e-10:new_degenerate+=1
   elif any(dot(n,ns[k])<-1e-7 for k in ids):new_opposed+=1
assert not new_degenerate and not new_opposed,(new_degenerate,new_opposed)
assert triangles<=120000 and primitives<=40 and (OUT/'shibuya109.glb').stat().st_size<=3000000
before,beforeb=load(OUT/'pre-repack.glb')
for oi,ni in pack['accessor_map'].items():assert acc(before,beforeb,int(oi))==acc(b,bb,ni)
result={'model_sha256':sha((OUT/'shibuya109.glb').read_bytes()),'protected_untouched_meshes':protected,'all_original_live_attribute_values_exact':True,'retained_indices_match_original_removal_contract':True,'original_material_prefix_exact':True,'repack_active_accessor_equivalence':True,'added_degenerate_triangles':new_degenerate,'added_opposed_normals':new_opposed,'triangles':triangles,'primitives':primitives,'bytes':(OUT/'shibuya109.glb').stat().st_size,'budget_unchanged_pass':True}
(ROOT/'evidence/verification.json').write_text(json.dumps(result,indent=2));print(json.dumps(result,indent=2))
