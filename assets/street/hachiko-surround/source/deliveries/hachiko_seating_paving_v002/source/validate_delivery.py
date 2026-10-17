#!/usr/bin/env python3
"""Independent GLB structure/material checks; does not import or execute model code."""
from pathlib import Path
import json,struct,math,hashlib,sys
ROOT=Path(__file__).resolve().parents[1]
results=[]
for path in sorted((ROOT/'web').glob('*.glb')):
 data=path.read_bytes();magic,version,length=struct.unpack_from('<III',data,0)
 assert magic==0x46546c67 and version==2 and length==len(data)
 n,kind=struct.unpack_from('<II',data,12);g=json.loads(data[20:20+n]);issues=[]
 assert not g.get('cameras') and not g.get('animations') and not g.get('skins')
 assert 'KHR_lights_punctual' not in g.get('extensions',{})
 for node in g.get('nodes',[]):
  assert not any(k in node for k in ['camera','skin']);assert all(math.isfinite(x) for k in ['matrix','translation','rotation','scale'] for x in node.get(k,[]))
 for img in g.get('images',[]): assert 'bufferView' in img and 'uri' not in img
 for acc in g['accessors']:
  for k in ['min','max']:assert all(math.isfinite(v) for v in acc.get(k,[]))
 for m in g.get('materials',[]):
  if 'granite' in m['name'] or 'paving' in m['name']:
   assert 'baseColorTexture' in m['pbrMetallicRoughness'];assert 'normalTexture' in m
   assert m['pbrMetallicRoughness']['baseColorTexture']['index']!=m['normalTexture']['index']
  assert 'emissiveFactor' not in m or not any(m['emissiveFactor'])
 # Texture and geometry references are all in bounds.
 for tx in g.get('textures',[]):assert 0<=tx['source']<len(g['images'])
 for mesh in g['meshes']:
  for pr in mesh['primitives']:
   assert pr.get('mode',4)==4
   for ai in pr['attributes'].values():assert ai<len(g['accessors'])
 results.append({'file':str(path.relative_to(ROOT)),'bytes':len(data),'sha256':hashlib.sha256(data).hexdigest(),'meshes':len(g['meshes']),'primitives':sum(len(m['primitives']) for m in g['meshes']),'embedded_images':len(g.get('images',[])),'no_cameras_lights_animation':True,'independent_basecolor_normal_maps':True,'status':'pass'})
(ROOT/'qa'/'structure_validation.json').write_text(json.dumps(results,indent=2));print(json.dumps(results,indent=2))
