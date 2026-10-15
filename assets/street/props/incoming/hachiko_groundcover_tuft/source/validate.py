import json,struct,math,hashlib
from pathlib import Path
r=Path(__file__).resolve().parents[1];b=(r/'output/groundcover.glb').read_bytes();n=struct.unpack_from('<I',b,12)[0];d=json.loads(b[20:20+n]);bb=b[28+n:]
assert struct.unpack_from('<I',b,8)[0]==len(b)
assert len(d['meshes'])==1 and len(d['materials'])==2
assert not d.get('images') and not d.get('textures') and not d.get('animations') and not d.get('skins')
assert all(m.get('alphaMode','OPAQUE')=='OPAQUE' and m.get('doubleSided') for m in d['materials'])
def acc(i):
 a=d['accessors'][i];v=d['bufferViews'][a['bufferView']];k={'SCALAR':1,'VEC3':3}[a['type']];fmt={5126:'f',5123:'H',5125:'I'}[a['componentType']];sz=struct.calcsize('<'+fmt*k);st=v.get('byteStride',sz);off=v.get('byteOffset',0)+a.get('byteOffset',0)
 return [struct.unpack_from('<'+fmt*k,bb,off+j*st) for j in range(a['count'])]
pts=[];tri=0;minarea=1
for p in d['meshes'][0]['primitives']:
 pos=acc(p['attributes']['POSITION']);norm=acc(p['attributes']['NORMAL']);ind=[x[0] for x in acc(p['indices'])];pts+=pos;tri+=len(ind)//3
 assert all(math.isfinite(x) for row in pos+norm for x in row)
 for j in range(0,len(ind),3):
  a,bp,c=[pos[k] for k in ind[j:j+3]];u=[bp[k]-a[k] for k in range(3)];v=[c[k]-a[k] for k in range(3)];cr=[u[1]*v[2]-u[2]*v[1],u[2]*v[0]-u[0]*v[2],u[0]*v[1]-u[1]*v[0]];area=math.sqrt(sum(x*x for x in cr))/2;minarea=min(minarea,area);assert area>1e-10
lo=[min(p[k] for p in pts) for k in range(3)];hi=[max(p[k] for p in pts) for k in range(3)]
assert abs(lo[1])<1e-6 and abs(lo[0]+hi[0])<1e-6 and abs(lo[2]+hi[2])<1e-6
assert tri==936 and tri<=1200 and .12<hi[1]<.25
result={'passed':True,'triangles':tri,'minimum_triangle_area_m2':minarea,'materials':2,'alpha':'OPAQUE','external_resources':0,'gltf_bounds_y_up':[lo,hi],'bytes':len(b),'sha256':hashlib.sha256(b).hexdigest(),'scope':'standalone asset; runtime integration and FPS not tested'}
(r/'evidence/validation.json').write_text(json.dumps(result,indent=2)+'\n');print(result)
