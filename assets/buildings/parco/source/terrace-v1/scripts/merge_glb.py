from pathlib import Path
import json,hashlib
from glb_io import read,write
ROOT=Path(__file__).resolve().parents[1];G=ROOT/'geometry';a,ab=read(G/'authorized-shell-cut.glb');b,bb=read(G/'additions.glb')
off={k:len(a.get(k,[])) for k in ['bufferViews','accessors','meshes','materials','nodes']};pad=(-len(ab))%4;boff=len(ab)+pad
for v in b.get('bufferViews',[]):v['buffer']=0;v['byteOffset']=v.get('byteOffset',0)+boff
for ac in b.get('accessors',[]):
 if 'bufferView'in ac:ac['bufferView']+=off['bufferViews']
for me in b['meshes']:
 for pr in me['primitives']:
  pr['attributes']={k:v+off['accessors'] for k,v in pr['attributes'].items()}
  if 'indices'in pr:pr['indices']+=off['accessors']
  if 'material'in pr:pr['material']+=off['materials']
for node in b['nodes']:
 if 'mesh'in node:node['mesh']+=off['meshes']
 if 'children'in node:node['children']=[i+off['nodes'] for i in node['children']]
for k in off:a.setdefault(k,[]).extend(b.get(k,[]))
a['scenes'][a.get('scene',0)]['nodes'] += [i+off['nodes'] for i in b['scenes'][b.get('scene',0)]['nodes']]
for k in ['extensionsUsed','extensionsRequired']:
 if k in b:a[k]=sorted(set(a.get(k,[])+b[k]))
a['asset']['generator']='PARCO4F terrace candidate on roof22-corrected base; scoped7walltriangle and8ribbon clips; duplicatecorebase omitted after exactcoverage proof; not runtime accepted'
write(ROOT/'parco_terrace_candidate.glb',a,ab+bytearray(pad)+bb)
print('CANDIDATE_GLB',hashlib.sha256((ROOT/'parco_terrace_candidate.glb').read_bytes()).hexdigest())
