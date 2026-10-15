"""Batch a translation-only glTF mesh hierarchy without changing source normals/UVs."""
import json,struct,numpy as np

def batch_glb(path):
 raw=open(path,'rb').read();jl=struct.unpack_from('<I',raw,12)[0];j=json.loads(raw[20:20+jl]);data=raw[28+jl:];oldviews=j['bufferViews'];oldacc=j['accessors'];out=bytearray();views=[];access=[]
 def read(ai):
  a=oldacc[ai];v=oldviews[a['bufferView']];dt={5126:'<f4',5123:'<u2',5125:'<u4'}[a['componentType']];n={'SCALAR':1,'VEC2':2,'VEC3':3}[a['type']];assert 'byteStride' not in v
  return np.frombuffer(data,dtype=dt,count=a['count']*n,offset=v.get('byteOffset',0)+a.get('byteOffset',0)).reshape(-1,n).copy()
 def put_bytes(b):
  while len(out)%4:out.append(0)
  vi=len(views);views.append({'buffer':0,'byteOffset':len(out),'byteLength':len(b)});out.extend(b);return vi
 def put(a,typ,ct):
  vi=put_bytes(a.tobytes());ac={'bufferView':vi,'componentType':ct,'count':len(a),'type':typ}
  if typ=='VEC3':ac.update(min=a.min(axis=0).tolist(),max=a.max(axis=0).tolist())
  access.append(ac);return len(access)-1
 groups={}
 for node in j['nodes']:
  if 'mesh' not in node:continue
  assert not any(k in node for k in ['rotation','scale','matrix'])
  t=np.array(node.get('translation',[0,0,0]),dtype=np.float32)
  for p in j['meshes'][node['mesh']]['primitives']:
   g=groups.setdefault(p['material'],[]);pos=read(p['attributes']['POSITION']);pos+=t
   g.append((pos,read(p['attributes']['NORMAL']),read(p['attributes']['TEXCOORD_0']),read(p['indices']).ravel()))
 meshes=[]
 for m,g in sorted(groups.items()):
  ix=[];off=0
  for x in g:ix.extend((x[3]+off).tolist());off+=len(x[0])
  attrs={name:put(np.concatenate([x[k] for x in g]).astype('<f4'),typ,5126) for k,name,typ in [(0,'POSITION','VEC3'),(1,'NORMAL','VEC3'),(2,'TEXCOORD_0','VEC2')]}
  ii=put(np.array(ix,dtype='<u4').reshape(-1,1),'SCALAR',5125);meshes.append({'name':'Counter_material_'+str(m),'primitives':[{'attributes':attrs,'indices':ii,'material':m}]})
 for im in j.get('images',[]):
  v=oldviews[im['bufferView']];im['bufferView']=put_bytes(data[v.get('byteOffset',0):v.get('byteOffset',0)+v['byteLength']])
 j['meshes']=meshes;j['nodes']=[{'name':'SHIBUHACHIBOX_counter_bottom_center','children':[1,2]}, {'name':'Oak_counter','mesh':0},{'name':'White_rack','mesh':1}];j['scenes']=[{'nodes':[0]}];j['scene']=0;j['bufferViews']=views;j['accessors']=access;j['buffers']=[{'byteLength':len(out)}]
 jb=json.dumps(j,separators=(',',':')).encode();jb+=b' '*((-len(jb))%4);out+=b'\0'*((-len(out))%4)
 open(path,'wb').write(struct.pack('<4sII',b'glTF',2,28+len(jb)+len(out))+struct.pack('<II',len(jb),0x4e4f534a)+jb+struct.pack('<II',len(out),0x004e4942)+out)
