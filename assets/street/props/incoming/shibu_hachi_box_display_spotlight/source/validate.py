import struct,json,sys,hashlib,math
from pathlib import Path
p=Path(sys.argv[1]);data=p.read_bytes();magic,version,length=struct.unpack_from('<III',data);assert magic==0x46546c67 and version==2 and length==len(data)
n,t=struct.unpack_from('<II',data,12);assert t==0x4e4f534a;g=json.loads(data[20:20+n]);assert len(g['meshes'])==1 and len(g['materials'])==3;assert 'images' not in g and 'textures' not in g
assert not any(k=='KHR_lights_punctual' for k in g.get('extensionsUsed',[]));assert not g.get('cameras')
tris=sum(g['accessors'][p['indices']]['count']//3 for m in g['meshes'] for p in m['primitives']);assert tris==652
mins=[1e9]*3;maxs=[-1e9]*3
for m in g['meshes']:
 for p in m['primitives']:
  a=g['accessors'][p['attributes']['POSITION']]
  for i in range(3):mins[i]=min(mins[i],a['min'][i]);maxs[i]=max(maxs[i],a['max'][i])
assert abs(mins[1])<1e-6 and abs(mins[0]+maxs[0])<1e-6 and abs(mins[2]+maxs[2])<1e-6
assert all(math.isfinite(v) for v in mins+maxs)
print(json.dumps({'status':'PASS','triangles':tris,'materials':len(g['materials']),'bytes':len(data),'sha256':hashlib.sha256(data).hexdigest(),'gltf_bounds_min':mins,'gltf_bounds_max':maxs,'no_external_images':True,'no_runtime_lights':True},indent=2))
