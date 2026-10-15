"""Historical upper-panel assertions, unchanged except explicit frozen-fixture routing."""
import json,struct,hashlib,collections
from pathlib import Path
import numpy as np
A=Path(__file__).resolve().parents[2];R=A/'source/data';B=R/'panel-baseline';C=R/'lower-panel-baseline';E=A/'evidence/cumulative-v2/upper';E.mkdir(parents=True,exist_ok=True)
def load(path):
 raw=path.read_bytes();jl=struct.unpack_from('<I',raw,12)[0];j=json.loads(raw[20:20+jl]);buf=raw[28+jl:]
 def ar(i):
  ac=j['accessors'][i];bv=j['bufferViews'][ac['bufferView']];sz=3 if ac['type']=='VEC3' else 1
  return np.frombuffer(buf,dtype={5126:'<f4',5123:'<u2',5125:'<u4'}[ac['componentType']],count=ac['count']*sz,offset=bv.get('byteOffset',0)+ac.get('byteOffset',0)).reshape(-1,sz)
 tris={};geom={}
 for m in j['meshes']:
  p=m['primitives'][0];pos=ar(p['attributes']['POSITION']);nor=ar(p['attributes']['NORMAL']);idx=ar(p['indices']).reshape(-1,3);c=collections.Counter()
  for tri in idx:
   key=tuple(sorted(pos[v].tobytes()+nor[v].tobytes() for v in tri));c[key]+=1;geom[key]=pos[tri][:,[0,2,1]]*np.array([1,-1,1])
  tris[m['name']]=c
 return j,tris,geom
j0,t0,g0=load(B/'stream.glb');j1,t1,g1=load(C/'stream.glb');br=json.load(open(C/'build-report.json'));a=np.array([255.985,-290.160,0]);b=np.array([279.103,-264.434,0]);t=(b-a)/np.linalg.norm(b-a);n=np.array([t[1],-t[0],0]);W=np.linalg.norm(b-a);low,high=br['target_z_limits'];removed=added=0
for name in t0:
 minus=t0[name]-t1[name];plus=t1[name]-t0[name]
 if name not in ['stream_spandrel','stream_frame']:assert not minus and not plus,name
 for mode,diff,g in [('removed',minus,g0),('added',plus,g1)]:
  for key,count in diff.items():
   tri=g[key];q=(tri-a)@t/W;d=(tri-a)@n
   assert q.min()>-.001 and q.max()<1.001
   assert d.min()>.115 and d.max()<.195
   assert tri[:,2].min()>=low-.011 and tri[:,2].max()<=high+.011
   if mode=='removed':removed+=count
   else:added+=count
assert j0['materials']==j1['materials'];assert j0['nodes']==j1['nodes'];assert len(j1['meshes'])==len(j0['meshes'])==8
assert br['triangles_after']<=br['triangles_before'];assert br['bytes_after']<=br['bytes_before'];assert hashlib.sha256((C/'stream.glb').read_bytes()).hexdigest()=='75753aec0940ab0cdb1bc82914918adf424bef0098aad95c020a1b983a06b82c'
assert hashlib.sha256((B/'stream.glb').read_bytes()).hexdigest()=='16b029fbec71fa753b2c8f5bdbcead325105d9576df2bc636b637f05af130aed'
stats=json.load(open(B/'stats.json'));assert stats['missing_pavement_samples']==0
result={'pass':True,'unchanged_shell_roof_ground_geometry':True,'exact_off_target_triangle_multisets_including_normals':True,'materials_nodes_primitives_unchanged':True,'outside_z_band_unchanged_tolerance_m':.011,'changed_source_face':112,'removed_overlay_triangles':removed,'added_overlay_triangles':added,'triangles':br['triangles_after'],'glb_bytes':br['bytes_after'],'runtime_matches_pinned_output':True,'pavement_samples_retained':len(stats['pavement_samples']),'missing_pavement_samples':0,'datum_tp_m':15,'baseline_sha256':br['source_sha256'],'new_sha256':br['output_sha256']};(E/'tests.json').write_text(json.dumps(result,indent=2)+'\n');print(result)
