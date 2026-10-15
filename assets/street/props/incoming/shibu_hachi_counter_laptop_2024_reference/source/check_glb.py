"""stdlib-only GLB structural/numeric audit. Run: python source/check_glb.py DIR"""
import json,struct,math,sys,hashlib
from pathlib import Path
O=Path(sys.argv[1]);p=O/'shibu_hachi_counter_laptop.glb';data=p.read_bytes()
magic,version,length=struct.unpack_from('<III',data);assert magic==0x46546c67 and version==2 and length==len(data)
pos=12;parts={}
while pos<len(data):
 n,t=struct.unpack_from('<II',data,pos);pos+=8;parts[t]=data[pos:pos+n];pos+=n
assert pos==len(data)
doc=json.loads(parts[0x4e4f534a]);binary=parts[0x004e4942]
assert len(doc['buffers'])==1 and 'uri' not in doc['buffers'][0]
assert not doc.get('images') and not doc.get('textures') and not doc.get('cameras') and not doc.get('animations')
assert not doc.get('extensionsRequired')
formats={5120:'b',5121:'B',5122:'h',5123:'H',5125:'I',5126:'f'};sizes={'SCALAR':1,'VEC2':2,'VEC3':3,'VEC4':4,'MAT4':16}
def acc(i):
 a=doc['accessors'][i];v=doc['bufferViews'][a['bufferView']];f='<'+formats[a['componentType']]*sizes[a['type']];n=struct.calcsize(f);stride=v.get('byteStride',n);off=v.get('byteOffset',0)+a.get('byteOffset',0);end=off+(a['count']-1)*stride+n
 assert end<=v.get('byteOffset',0)+v['byteLength']<=len(binary)
 return [struct.unpack_from(f,binary,off+k*stride) for k in range(a['count'])]
triangles=0;zero=0;pts=[];prims=0
for mesh in doc['meshes']:
 for pr in mesh['primitives']:
  prims+=1;assert pr.get('mode',4)==4
  xyz=acc(pr['attributes']['POSITION']);norm=acc(pr['attributes']['NORMAL']);idx=[r[0] for r in acc(pr['indices'])]
  assert len(idx)%3==0 and min(idx)>=0 and max(idx)<len(xyz);triangles+=len(idx)//3;pts+=xyz
  assert all(math.isfinite(c) for p in xyz for c in p)
  assert all(abs(sum(c*c for c in n)-1)<.005 for n in norm)
  for k in range(0,len(idx),3):
   a,b,c=[xyz[i] for i in idx[k:k+3]];u=[b[i]-a[i] for i in range(3)];v=[c[i]-a[i] for i in range(3)];cross=[u[1]*v[2]-u[2]*v[1],u[2]*v[0]-u[0]*v[2],u[0]*v[1]-u[1]*v[0]]
   zero+=int(sum(x*x for x in cross)<1e-24)
assert len(doc['meshes'])==3 and prims==3 and len(doc['materials'])==3 and zero==0
mn=[min(p[i] for p in pts) for i in range(3)];mx=[max(p[i] for p in pts) for i in range(3)]
assert abs(mn[1])<1e-6 and abs(mn[0]+mx[0])<1e-6 and abs(mn[2]+mx[2])<1e-6
for m in doc['materials']:assert m.get('alphaMode','OPAQUE')=='OPAQUE' and not any(m.get('emissiveFactor',[0,0,0]))
res={'status':'pass','sha256':hashlib.sha256(data).hexdigest(),'bytes':len(data),'glTF_version':doc['asset']['version'],'meshes':len(doc['meshes']),'primitives':prims,'materials':len(doc['materials']),'triangles':triangles,'zero_area_triangles':zero,'finite_positions':True,'unit_normals':True,'bounds_gltf_y_up_m':[mn,mx],'bottom_centre':True,'embedded_binary_buffer':True,'external_uris':[],'textures':0,'cameras':0,'lights':0,'extensions_required':[]}
json.dump(res,open(O/'qa'/'glb_structure.json','w'),indent=2);print(json.dumps(res,indent=2))
