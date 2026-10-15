"""Direct actual-main versus final signed-winding multiset preservation contract."""
import collections,hashlib,json,struct
from pathlib import Path
import numpy as np
A=Path(__file__).resolve().parents[2];D=A/'source/data';E=A/'evidence/cumulative-v2';E.mkdir(parents=True,exist_ok=True)
def load(p):
 raw=p.read_bytes();n=struct.unpack_from('<I',raw,12)[0];j=json.loads(raw[20:20+n]);buf=raw[28+n:]
 def arr(i):
  a=j['accessors'][i];v=j['bufferViews'][a['bufferView']];w={'VEC3':3,'SCALAR':1}[a['type']]
  return np.frombuffer(buf,dtype={5126:'<f4',5123:'<u2',5125:'<u4'}[a['componentType']],count=a['count']*w,offset=v.get('byteOffset',0)+a.get('byteOffset',0)).reshape(-1,w)
 out={}
 for m in j['meshes']:
  assert len(m['primitives'])==1;p=m['primitives'][0];attrs={k:arr(v) for k,v in p['attributes'].items()};idx=arr(p['indices']).reshape(-1,3);c=collections.Counter();g={}
  for tri in idx:
   v=[b''.join(attrs[k][i].tobytes() for k in sorted(attrs)) for i in tri];key=min(tuple(v),tuple(v[1:]+v[:1]),tuple(v[2:]+v[:2]));c[key]+=1;g[key]=attrs['POSITION'][tri][:,[0,2,1]]*[1,-1,1]
  out[m['name']]=(attrs,idx,c,g)
 return raw,j,out
raw0,j0,m0=load(D/'panel-baseline/stream.glb');raw1,j1,m1=load(A/'web/stream.glb')
blob=lambda b:hashlib.sha1(b'blob '+str(len(b)).encode()+b'\0'+b).hexdigest()
assert blob(raw0)=='981faa7b5ffab3ceffa36367533167f437841f1e'
assert blob(raw1)=='cc801164bff5b6c848e2b87f73f823c8ab716d53'
for k in set(j0)|set(j1):
 if k not in ['meshes','accessors','bufferViews','buffers']:assert j0[k]==j1[k],k
assert set(m0)==set(m1) and len(m0)==8
origin=np.array([255.985,-290.160,0]);end=np.array([279.103,-264.434,0]);width=np.linalg.norm(end-origin);t=(end-origin)/width;n=np.array([t[1],-t[0],0])
counts={}
for name in m0:
 a,idx,c,g=m0[name];b,idx1,d,h=m1[name];minus=c-d;plus=d-c;counts[name]={'removed':sum(minus.values()),'added':sum(plus.values())}
 if name not in ['stream_spandrel','stream_frame']:
  assert not minus and not plus
  assert idx.tobytes()==idx1.tobytes()
  for attr in a:assert a[attr].tobytes()==b[attr].tobytes()
 for changes,geo in [(minus,g),(plus,h)]:
  for key in changes:
   xyz=geo[key];q=(xyz-origin)@t/width;depth=(xyz-origin)@n
   assert q.min()>-.001 and q.max()<1.001
   assert depth.min()>.115 and depth.max()<.195
   assert xyz[:,2].min()>=75.240-.011 and xyz[:,2].max()<=163.436+.011
   if xyz[:,2].min()<90.804-.011: assert q.max()<.551
assert sum(x['removed'] for x in counts.values())==112
assert sum(x['added'] for x in counts.values())==118
assert len(raw1)-len(raw0)==-4
stats=json.loads((D/'stats.json').read_text());old=json.loads((D/'panel-baseline/stats.json').read_text())
for k in ['pavement_samples','datum_tp_m','missing_pavement_samples','roof_translation_m']:assert stats[k]==old[k],k
assert len(stats['pavement_samples'])==144 and stats['datum_tp_m']==15
result={'pass':True,'baseline_git_blob':blob(raw0),'target_git_blob':blob(raw1),'baseline_bytes':len(raw0),'target_bytes':len(raw1),'net_bytes':-4,'net_triangles':6,'changed_source_face':112,'meshes':counts,'all_off_target_positions_normals_winding_exact':True,'scene_nodes_materials_and_transform_exact':True,'ground_samples':144,'datum_tp_m':15,'scope':'upper source112 field and lower-left six rectangles; not full scene validation'}
(E/'main-vs-final.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result,indent=2))
