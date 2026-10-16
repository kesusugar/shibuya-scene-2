"""Minimal actual-buffer GLB checks, using Python's standard library only."""
import hashlib, json, math, struct, sys
from pathlib import Path
p=Path(sys.argv[1]); raw=p.read_bytes(); magic,version,total=struct.unpack_from('<4sII',raw,0)
assert magic==b'glTF' and version==2 and total==len(raw)
n,t=struct.unpack_from('<II',raw,12); assert t==0x4E4F534A
d=json.loads(raw[20:20+n]); off=20+n; size,typ=struct.unpack_from('<II',raw,off); assert typ==0x004E4942
b=raw[off+8:off+8+size]
assert len(d['nodes'])==1 and len(d['meshes'])==1 and len(d['materials'])==3
assert not d.get('images') and not d.get('textures') and not d.get('animations') and not d.get('skins')
assert all('uri' not in buf for buf in d['buffers'])
assert all(mat.get('doubleSided') for mat in d['materials'])
assert not any(k in d['nodes'][0] for k in ('translation','rotation','scale','matrix'))
def acc(i):
 a=d['accessors'][i]; v=d['bufferViews'][a['bufferView']]; types={5126:'f',5125:'I',5123:'H',5121:'B'}; counts={'SCALAR':1,'VEC3':3,'VEC2':2,'VEC4':4}; fmt='<'+types[a['componentType']]*counts[a['type']]; length=struct.calcsize(fmt); start=v.get('byteOffset',0)+a.get('byteOffset',0); stride=v.get('byteStride',length)
 assert start+(a['count']-1)*stride+length<=len(b)
 return [struct.unpack_from(fmt,b,start+j*stride) for j in range(a['count'])]
pts_all=[]; triangles=0; minimum_area=1e20; area_sum=0
for prim in d['meshes'][0]['primitives']:
 assert prim.get('mode',4)==4
 pts=acc(prim['attributes']['POSITION']); ids=[v[0] for v in acc(prim['indices'])]; assert len(ids)%3==0
 assert all(math.isfinite(v) for pt in pts for v in pt)
 for j in range(0,len(ids),3):
  a,c,e=[pts[k] for k in ids[j:j+3]]; u=[c[k]-a[k] for k in range(3)]; v=[e[k]-a[k] for k in range(3)]; cross=(u[1]*v[2]-u[2]*v[1],u[2]*v[0]-u[0]*v[2],u[0]*v[1]-u[1]*v[0]); area=math.sqrt(sum(x*x for x in cross))/2
  assert area>1e-10, 'Degenerate triangle'
  minimum_area=min(minimum_area,area); area_sum+=area
 triangles+=len(ids)//3; pts_all.extend(pts)
lo=[min(p[k] for p in pts_all) for k in range(3)]; hi=[max(p[k] for p in pts_all) for k in range(3)]
assert all(abs(a-b)<1e-5 for a,b in zip(lo,[-1.1,0,-.1]))
assert all(abs(a-b)<1e-5 for a,b in zip(hi,[1.1,4.2,.1]))
assert abs(area_sum-(2.2*4.2+.2*4.2))<1e-5, 'Surface area mismatch: possible holes or overlapping bands'
result={'passed':True,'glb_sha256':hashlib.sha256(raw).hexdigest(),'glb_bytes':len(raw),'triangles':triangles,'actual_position_bounds_gltf_m':[lo,hi],'surface_area_m2':area_sum,'minimum_triangle_area_m2':minimum_area,'mesh_objects':1,'materials':3,'double_sided':True,'image_textures':0,'external_uris':0,'unapplied_node_transforms':0,'checks':['GLB container and buffers','actual finite position arrays','index bounds and nonzero triangle areas','nominal envelope and ground contact','front + return total surface area','single asset node; no studio export','no image texture/external URI/animation/skin','double-sided open shell']}
print(json.dumps(result,indent=2))
