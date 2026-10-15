import sys,json,struct,hashlib,argparse,math,copy
from pathlib import Path
HERE=Path(__file__).resolve().parent;ASSET=HERE.parent.parent
sha=lambda b:hashlib.sha256(b).hexdigest()

def load(path):
 raw=Path(path).read_bytes();n=struct.unpack_from('<I',raw,12)[0]
 return json.loads(raw[20:20+n]),raw[28+n:]
def acc(j,b,i):
 a=j['accessors'][i];v=j['bufferViews'][a['bufferView']];n={'SCALAR':1,'VEC2':2,'VEC3':3,'VEC4':4}[a['type']];f={5126:'f',5125:'I',5123:'H',5121:'B'}[a['componentType']];sz=struct.calcsize(f)*n
 return [struct.unpack_from('<'+f*n,b,v.get('byteOffset',0)+a.get('byteOffset',0)+k*v.get('byteStride',sz)) for k in range(a['count'])]
def sub(a,b):return tuple(x-y for x,y in zip(a,b))
def dot(a,b):return sum(x*y for x,y in zip(a,b))
def cross(a,b):return (a[1]*b[2]-a[2]*b[1],a[2]*b[0]-a[0]*b[2],a[0]*b[1]-a[1]*b[0])
def norm(a):return math.sqrt(dot(a,a))
def lerp(a,b,f):return tuple(x+(y-x)*f for x,y in zip(a,b))
def to_blender(p):return (p[0],-p[2],p[1])
def to_gltf(p):return (p[0],p[2],-p[1])
