import json,struct,math,sys
from pathlib import Path
p=Path(sys.argv[1] if len(sys.argv)>1 else 'output/shibu_hachi_box.glb')
b=p.read_bytes();magic,version,size=struct.unpack_from('<III',b);assert magic==0x46546c67 and version==2 and size==len(b)
n,t=struct.unpack_from('<II',b,12);j=json.loads(b[20:20+n]);offset=20+n;bn,bt=struct.unpack_from('<II',b,offset);binary=b[offset+8:offset+8+bn]
assert len(j['materials'])==5;assert len(j['meshes'])==5;assert not j.get('images');assert not j.get('textures');assert not j.get('cameras');assert not j.get('animations')
assert all(not x.get('uri') for x in j.get('buffers',[]));tri=0;bounds=[[],[],[]]
for mesh in j['meshes']:
 for pr in mesh['primitives']:
  assert pr.get('mode',4)==4;ac=j['accessors'][pr['attributes']['POSITION']];assert ac['componentType']==5126
  bv=j['bufferViews'][ac['bufferView']];start=bv.get('byteOffset',0)+ac.get('byteOffset',0);stride=bv.get('byteStride',12)
  for i in range(ac['count']):
   xyz=struct.unpack_from('<fff',binary,start+i*stride);assert all(math.isfinite(v) for v in xyz)
   for k,v in enumerate(xyz):bounds[k].append(v)
  ind=j['accessors'][pr['indices']];tri+=ind['count']//3
assert tri<20000
bb=[[min(x),max(x)] for x in bounds];assert abs(bb[1][0])<1e-6;assert bb[0][1]-bb[0][0]<13.1;assert bb[1][1]<3.5
assert any(m.get('alphaMode')=='BLEND' for m in j['materials'])
print(json.dumps({'pass':True,'bytes':len(b),'triangles':tri,'meshes':len(j['meshes']),'materials':len(j['materials']),'gltf_bounds':bb,'external_resources':0},indent=2))
