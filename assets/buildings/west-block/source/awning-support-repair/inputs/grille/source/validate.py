import json,struct,math,hashlib,sys
from pathlib import Path
from build_grille import read,sha
root=Path(sys.argv[1]) if len(sys.argv)>1 else Path(__file__).resolve().parents[1]
a,ab=read(root/'inputs/web/west-block.glb');b,bb=read(root/'web/west-block.glb')
assert ab==bb[:len(ab)]
for key in a:
 if key in ['buffers','scenes']:continue
 assert (b[key][:len(a[key])] if isinstance(a[key],list) else b[key])==a[key],key
expected=json.loads(json.dumps(a['scenes']));expected[a.get('scene',0)]['nodes'].append(len(a['nodes']));assert b['scenes']==expected
assert b['nodes'][-1]=={'name':'west_six_cell_grille_apron','mesh':len(a['meshes'])}
def acc(i):
 q=b['accessors'][i];v=b['bufferViews'][q['bufferView']];width={'SCALAR':1,'VEC3':3}[q['type']];fmt={5126:'f',5123:'H'}[q['componentType']];step=struct.calcsize(fmt)*width;offset=v.get('byteOffset',0)+q.get('byteOffset',0)
 assert offset+step*q['count']<=len(bb)
 return [struct.unpack_from('<'+fmt*width,bb,offset+k*step) for k in range(q['count'])]
lo=[1e9]*3;hi=[-1e9]*3;count=0
for p in b['meshes'][-1]['primitives']:
 vs=acc(p['attributes']['POSITION']);ns=acc(p['attributes']['NORMAL']);ix=[x[0] for x in acc(p['indices'])];assert max(ix)<len(vs)
 for v in vs:
  assert all(math.isfinite(x) for x in v)
  # raw glTF x,z,-y back to local u,d,z
  dx=v[0]+49;dy=-v[2]-23.326344151;vlocal=(dx*.993768268+dy*.111465822,dx*.111465822-dy*.993768268,v[1])
  for k,x in enumerate(vlocal):lo[k]=min(lo[k],x);hi[k]=max(hi[k],x)
 for n in ns:assert abs(sum(x*x for x in n)-1)<1e-5
 for i in range(0,len(ix),3):
  x,y,z=[vs[k] for k in ix[i:i+3]];e=[y[k]-x[k] for k in range(3)];f=[z[k]-x[k] for k in range(3)];cross=[e[1]*f[2]-e[2]*f[1],e[2]*f[0]-e[0]*f[2],e[0]*f[1]-e[1]*f[0]];assert sum(cross[k]*ns[ix[i]][k] for k in range(3))>1e-8;count+=1
assert lo[0]>=-1.41501 and hi[0]<=1.41501 and lo[1]>=.23999 and hi[1]<=.40001 and lo[2]>=3.27499 and hi[2]<=3.85501
for name in ['signs-2025-01.glb','viewer.json']:assert sha(root/'inputs/web'/name)==sha(root/'web'/name)
result={'original_binary_bytes_preserved':len(ab),'original_meshes_preserved':len(a['meshes']),'original_nodes_preserved':len(a['nodes']),'new_geometry_finite_and_index_valid':True,'triangle_winding_matches_flat_normals':True,'added_triangle_count':count,'local_ud_z_min':lo,'local_ud_z_max':hi,'sign_and_datum_bytes_exact':True,'no_original_source_changes_required':True}
(root/'evidence/strict-validation.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result,indent=2))
