import json,struct,sys,hashlib
from pathlib import Path
p=Path(sys.argv[1]);b=p.read_bytes();magic,version,total=struct.unpack_from('<III',b);assert magic==0x46546c67 and version==2 and total==len(b)
n=struct.unpack_from('<I',b,12)[0];j=json.loads(b[20:20+n]);assert not j.get('images') and not j.get('textures')
assert len(j['meshes'])==1 and len(j['materials'])==3
tris=0;mins=[];maxs=[]
for m in j['meshes']:
 for pr in m['primitives']:
  assert pr.get('mode',4)==4
  tris+=j['accessors'][pr['indices']]['count']//3
  ac=j['accessors'][pr['attributes']['POSITION']];mins.append(ac['min']);maxs.append(ac['max'])
lo=[min(v[i] for v in mins) for i in range(3)];hi=[max(v[i] for v in maxs) for i in range(3)]
assert tris<=2000,(tris,'triangle budget');assert abs(lo[1])<1e-6
assert abs(lo[0]+hi[0])<1e-6 and abs(lo[2]+hi[2])<1e-6
assert abs((hi[0]-lo[0])-3.65)<1e-5 and abs((hi[1]-lo[1])-.18)<1e-5
assert all(m.get('alphaMode','OPAQUE')=='OPAQUE' for m in j['materials'])
print(json.dumps({'sha256':hashlib.sha256(b).hexdigest(),'bytes':len(b),'triangles':tris,'bounds_gltf': [lo,hi],'no_external_images':True,'materials':3,'status':'PASS'},indent=2))
