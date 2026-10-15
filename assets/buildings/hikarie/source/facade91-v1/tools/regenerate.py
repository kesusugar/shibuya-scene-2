#!/usr/bin/env python3
"""Deterministic stdlib-only GLB overlay patch; all paths are package-relative."""
from pathlib import Path
import argparse,hashlib,json,struct
ROOT=Path(__file__).resolve().parents[1]
INPUT_SHA='14cb88b7d3870512c23a750e7b9f701e85dc184cc1d473954725b6c138a0749d'
OUTPUT_SHA='2f4e95126c0d126c8db2d7d8aad4a54d5d0010ba7af0734b357a939077a87721'
def parse(path):
 raw=path.read_bytes();assert struct.unpack_from('<II',raw,0)==(0x46546c67,2);n=struct.unpack_from('<I',raw,12)[0];return raw,json.loads(raw[20:20+n]),raw[28+n:]
def indices(j,b,i):
 a=j['accessors'][i];v=j['bufferViews'][a['bufferView']];fmt,width={5123:('H',2),5125:('I',4)}[a['componentType']];assert a['type']=='SCALAR';off=v.get('byteOffset',0)+a.get('byteOffset',0);stride=v.get('byteStride',width);values=[struct.unpack_from('<'+fmt,b,off+k*stride)[0] for k in range(a['count'])];return [tuple(values[k:k+3]) for k in range(0,len(values),3)]
def generate(target):
 raw,j,b0=parse(ROOT/'baseline/hikarie.glb');assert hashlib.sha256(raw).hexdigest()==INPUT_SHA
 contract=json.loads((ROOT/'source/overlay_contract.json').read_text());assert contract['baseline_sha256']==INPUT_SHA and contract['candidate_sha256']==OUTPUT_SHA
 assert sum(len(m['remove_triangle_indices']) for m in contract['meshes'])==906;assert sum(len(m['retain_source91_triangle_indices']) for m in contract['meshes'])==204
 b=bytearray(b0)
 for entry in contract['meshes']:
  p=j['meshes'][entry['mesh']]['primitives'][entry['primitive']];assert p['material']==entry['material_id'];tri=indices(j,b0,p['indices']);remove=set(entry['remove_triangle_indices']);retain=set(entry['retain_source91_triangle_indices']);assert not remove&retain;assert remove|retain==set(entry['source91_all_triangle_indices']);assert max(remove)<len(tri)
  kept=[v for k,t in enumerate(tri) if k not in remove for v in t]
  b.extend(b'\0'*((-len(b))%4));off=len(b);data=struct.pack('<'+'I'*len(kept),*kept);b.extend(data);vi=len(j['bufferViews']);j['bufferViews'].append({'buffer':0,'byteOffset':off,'byteLength':len(data),'target':34963});ai=len(j['accessors']);j['accessors'].append({'bufferView':vi,'componentType':5125,'count':len(kept),'type':'SCALAR'});p['indices']=ai
 j['buffers'][0]['byteLength']=len(b);jb=json.dumps(j,separators=(',',':')).encode();jb+=b' '*((-len(jb))%4);b+=b'\0'*((-len(b))%4);out=struct.pack('<III',0x46546c67,2,12+8+len(jb)+8+len(b))+struct.pack('<II',len(jb),0x4e4f534a)+jb+struct.pack('<II',len(b),0x004e4942)+b
 digest=hashlib.sha256(out).hexdigest();assert digest==OUTPUT_SHA,(digest,OUTPUT_SHA);target.parent.mkdir(parents=True,exist_ok=True);target.write_bytes(out);print(json.dumps({'output':str(target),'sha256':digest,'bytes':len(out),'stdlib_only':True}))
if __name__=='__main__':
 ap=argparse.ArgumentParser();ap.add_argument('--output',type=Path,default=ROOT/'web/hikarie.glb');args=ap.parse_args();generate(args.output)
