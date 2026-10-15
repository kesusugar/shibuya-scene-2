"""Pinned cumulative delivery contract. Run with Blender4.2.3 -b -P this file."""
from pathlib import Path
import json,struct,hashlib,importlib.util,tempfile
import numpy as np
A=Path(__file__).resolve().parents[1]/'assets/buildings/mark-city';P=A/'source/west-cap-v1'
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def read(p):
 b=p.read_bytes();n=struct.unpack_from('<I',b,12)[0];return json.loads(b[20:20+n]),b[28+n:]
def accessor(j,b,i):
 a=j['accessors'][i];v=j['bufferViews'][a['bufferView']];dt={5126:'<f4',5125:'<u4',5123:'<u2',5121:'u1'}[a['componentType']];nc={'SCALAR':1,'VEC2':2,'VEC3':3,'VEC4':4}[a['type']];return np.frombuffer(b,dtype=dt,count=a['count']*nc,offset=v.get('byteOffset',0)+a.get('byteOffset',0)).reshape(-1,nc)
assert sha(A/'web/mark-city.glb')=='8dc763dcd1e242de07f7846ba7789a40252c6efb0eed88d531faf6d1c3b4cd5d'
x,xb=read(P/'source/baseline/mark-city-before-west-cap.glb');y,yb=read(A/'web/mark-city.glb')
assert yb[:len(xb)]==xb
for key in ['meshes','nodes','materials','accessors','bufferViews']:
 assert y[key][:len(x[key])]==x[key],key
assert y['scenes'][0]['nodes'][:len(x['scenes'][0]['nodes'])]==x['scenes'][0]['nodes']
assert len(y['nodes'])-len(x['nodes'])==3 and len(y['materials'])-len(x['materials'])==2
assert not y.get('images') and not y.get('textures')
tri=sum(y['accessors'][p['indices']]['count']//3 for m in y['meshes'] for p in m['primitives']);assert tri==25312
scope=json.loads((P/'source/data/west-cap-cluster-scope.json').read_text());geom=scope['source_geometry'];a=np.array(geom['a']);t=np.array(geom['t']);n=np.array(geom['outward'])
for mesh in y['meshes'][25:]:
 p=mesh['primitives'][0];pos=accessor(y,yb,p['attributes']['POSITION']);norm=accessor(y,yb,p['attributes']['NORMAL']);idx=accessor(y,yb,p['indices']).reshape(-1,3);v=np.stack((pos[:,0],-pos[:,2],pos[:,1]),axis=1);d=(v-a)@n;u=(v-a)@t
 assert np.isfinite(v).all() and min(u)>7.5999 and max(u)<37.4001
 expected=.085 if mesh['name'].endswith('frame') else .06;assert np.max(np.abs(d-expected))<.0001
 assert min(v[:,2])>=93.6999 and max(v[:,2])<=104.9501
 for ids in idx:
  q=v[ids];cross=np.cross(q[1]-q[0],q[2]-q[0]);assert np.linalg.norm(cross)>1e-7 and cross@n>0
 if mesh['name'].endswith('dark_opaque'):assert len(idx)==60
 if mesh['name'].endswith('glass'):assert len(idx)==4
spec=importlib.util.spec_from_file_location('cap',P/'source/blender/build_west_cap.py');m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)
with tempfile.TemporaryDirectory() as td:
 out=Path(td)/'mark-city.glb';report=m.build(out);assert out.read_bytes()==(A/'web/mark-city.glb').read_bytes();assert report==json.loads((P/'web/mark-city.east-stats.json').read_text())
print('PASS: exact target, whole prior payload and structure preservation, bounded outward nondegenerate cap faces, 30 dark panes, two glass ribbons, portable byte-exact regeneration and stats.')
