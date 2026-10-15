from pathlib import Path
import json,struct,numpy as np
COMP={5120:np.int8,5121:np.uint8,5122:np.int16,5123:np.uint16,5125:np.uint32,5126:np.float32}
NUM={'SCALAR':1,'VEC2':2,'VEC3':3,'VEC4':4,'MAT4':16}
def read(path):
 raw=Path(path).read_bytes();ln=struct.unpack_from('<I',raw,12)[0];doc=json.loads(raw[20:20+ln]);bl=struct.unpack_from('<I',raw,20+ln)[0];return doc,bytearray(raw[28+ln:28+ln+bl])
def acc(d,b,i):
 a=d['accessors'][i];v=d['bufferViews'][a['bufferView']];dt=COMP[a['componentType']];n=NUM[a['type']];offset=v.get('byteOffset',0)+a.get('byteOffset',0);stride=v.get('byteStride',n*np.dtype(dt).itemsize)
 return np.ndarray((a['count'],n),dtype=dt,buffer=b,offset=offset,strides=(stride,np.dtype(dt).itemsize))
def write(path,d,b):
 d['buffers']=[{'byteLength':len(b)}];j=json.dumps(d,separators=(',',':')).encode();j+=b' '*((-len(j))%4);b=bytes(b)+b'\0'*((-len(b))%4)
 Path(path).write_bytes(struct.pack('<III',0x46546c67,2,28+len(j)+len(b))+struct.pack('<II',len(j),0x4e4f534a)+j+struct.pack('<II',len(b),0x004e4942)+b)
def world(p):return np.column_stack((p[:,0],-p[:,2],p[:,1]))
