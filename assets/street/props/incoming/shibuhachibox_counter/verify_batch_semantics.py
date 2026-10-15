import json,struct,collections,os,sys
import numpy as np
D=os.path.dirname(os.path.abspath(__file__))
def sig(path):
 b=open(path,'rb').read();n=struct.unpack_from('<I',b,12)[0];j=json.loads(b[20:20+n]);data=b[28+n:]
 def read(i):
  a=j['accessors'][i];v=j['bufferViews'][a['bufferView']];return np.frombuffer(data,dtype={5126:'<f4',5123:'<u2',5125:'<u4'}[a['componentType']],count=a['count']*{'SCALAR':1,'VEC2':2,'VEC3':3}[a['type']],offset=v.get('byteOffset',0)+a.get('byteOffset',0)).reshape(a['count'],-1).copy()
 out=collections.Counter()
 for node in j['nodes']:
  if 'mesh' not in node:continue
  assert not any(k in node for k in ['rotation','scale','matrix'])
  for p in j['meshes'][node['mesh']]['primitives']:
   pos=read(p['attributes']['POSITION']);pos+=np.array(node.get('translation',[0,0,0]),np.float32)
   norm=read(p['attributes']['NORMAL']);uv=read(p['attributes']['TEXCOORD_0']);inds=read(p['indices']).reshape(-1,3)
   for tri in inds:
    out[(p['material'],tuple(tuple(np.concatenate((pos[i],norm[i],uv[i])).tolist()) for i in tri))]+=1
 return out
old=sig(sys.argv[1] if len(sys.argv)>1 else '/tmp/counter_before_batch.glb');new=sig(os.path.join(D,'shibuhachibox_counter.glb'))
r={'world_triangle_positions_float32_exact':old==new,'normals_exact':old==new,'uvs_exact':old==new,'triangle_order_winding_material_exact':old==new,'triangles':sum(new.values())};assert old==new,r
open(os.path.join(D,'batch_identity.json'),'w').write(json.dumps(r,indent=2));print(r)
