"""Lossless split of pinned combined geometry into building and optional January sign.
Python 3 stdlib. Copies accessor buffer-view bytes without numeric re-encoding.
No viewer registration: the existing loader automatically enables every registered layer.
"""
from pathlib import Path
import json,struct,hashlib,copy
R=Path(__file__).resolve().parent;A=R.parents[1]
def sha(b):return hashlib.sha256(b).hexdigest()
def read(p):
 b=p.read_bytes();assert b[:4]==b'glTF' and struct.unpack_from('<II',b,4)==(2,len(b));n=struct.unpack_from('<I',b,12)[0];assert b[16:20]==b'JSON';assert b[24+n:28+n]==b'BIN\0';return json.loads(b[20:20+n]),b[28+n:]
def write(p,j,b):
 j['buffers']=[{'byteLength':len(b)}];s=json.dumps(j,separators=(',',':')).encode();s+=b' '*(-len(s)%4);b+=b'\0'*(-len(b)%4);p.parent.mkdir(parents=True,exist_ok=True);p.write_bytes(struct.pack('<III',0x46546c67,2,28+len(s)+len(b))+struct.pack('<I4s',len(s),b'JSON')+s+struct.pack('<I4s',len(b),b'BIN\0')+b)
def split(j,b,ids):
 out={'asset':copy.deepcopy(j['asset']),'scene':0,'scenes':[{'name':'Scene','nodes':list(range(len(ids)))}],'nodes':[],'meshes':[],'materials':[],'accessors':[],'bufferViews':[]};binary=bytearray();maps={k:{} for k in ['materials','accessors','bufferViews']}
 def remap(kind,i):
  if i in maps[kind]:return maps[kind][i]
  v=copy.deepcopy(j[kind][i]);idx=len(out[kind]);maps[kind][i]=idx;out[kind].append(v)
  if kind=='accessors':
   assert 'sparse' not in v;v['bufferView']=remap('bufferViews',v['bufferView'])
  if kind=='bufferViews':
   assert v['buffer']==0;binary.extend(b'\0'*(-len(binary)%4));start=v.get('byteOffset',0);chunk=b[start:start+v['byteLength']];assert len(chunk)==v['byteLength'];v['byteOffset']=len(binary);binary.extend(chunk)
  return idx
 for ni in ids:
  n=copy.deepcopy(j['nodes'][ni]);assert not set(n)&{'children','skin'};m=copy.deepcopy(j['meshes'][n['mesh']]);n['mesh']=len(out['meshes']);out['nodes'].append(n);out['meshes'].append(m)
  for p in m['primitives']:
   assert set(p)<=set(['attributes','indices','material','mode']);p['material']=remap('materials',p['material']);p['indices']=remap('accessors',p['indices']);p['attributes']={k:remap('accessors',v) for k,v in p['attributes'].items()}
 return out,bytes(binary)
def main():
 p=R/'asset/web/takagi.glb';assert sha(p.read_bytes())=='94d893287d20d7155e626a4198a2509719aa66342e1b9620b002e21ba6d4b9fd';j,b=read(p)
 assert set(j)==set(['asset','scene','scenes','nodes','materials','meshes','accessors','bufferViews','buffers'])
 sign=[];base=[]
 for i,n in enumerate(j['nodes']):
  flags=[j['materials'][p['material']]['name'].startswith('takagi_billboard_') for p in j['meshes'][n['mesh']]['primitives']];assert all(flags) or not any(flags);(sign if all(flags) else base).append(i)
 assert len(sign)==4 and len(base)==11
 result={}
 for name,ids in [('takagi',base),('signs-2025-01',sign)]:
  k,c=split(j,b,ids);p=A/'web'/(name+'.glb');write(p,k,c);result[name]={'sha256':sha(p.read_bytes()),'bytes':p.stat().st_size,'triangles':sum(k['accessors'][p['indices']]['count']//3 for m in k['meshes'] for p in m['primitives']),'primitives':sum(len(m['primitives']) for m in k['meshes'])}
 assert result['takagi']['triangles']==4750 and result['signs-2025-01']['triangles']==169
 s=json.loads((R/'asset/source/data/stats.json').read_text());s.update({k:result['takagi'][k] for k in ['triangles','primitives','bytes']});s['status']='Cumulative facade/roof repair; January IKEA split into unregistered optional dated layer';s['statistics_scope']='Runtime architecture only; other inherited fields retain original provenance. Combined original package has 4919 triangles.';s['optional_sign_layer']=result['signs-2025-01'];(A/'source/data/stats.json').write_text(json.dumps(s,ensure_ascii=False,indent=2)+'\n')
 result['visibility']={'default':'architecture only','january_sign':'unregistered, not auto-loaded','reason':'main loader enables every viewer.layers entry; no date selector exists in this scope'}
 (R/'runtime-split.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result,indent=2))
if __name__=='__main__':
 main()
 try:import bpy
 except ImportError:bpy=None
 if bpy is not None:
  assert bpy.app.version[:3]==(4,2,3)
  bpy.ops.wm.read_factory_settings(use_empty=True)
  bpy.ops.import_scene.gltf(filepath=str(A/'web/takagi.glb'))
  bpy.ops.wm.save_as_mainfile(filepath=str(A/'source/blender/takagi.blend'))

