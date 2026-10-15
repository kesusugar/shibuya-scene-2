from clip import *
import copy
base,bb=parse((R/'web/clipped-base.glb').read_bytes());add,ab=parse((R/'web/addition.glb').read_bytes());off=len(bb);bb+=ab
vo=len(base['bufferViews']);ao=len(base['accessors']);mo=len(base['materials']);meo=len(base['meshes']);no=len(base['nodes'])
for v in add['bufferViews']:v['byteOffset']=v.get('byteOffset',0)+off
base['bufferViews']+=add['bufferViews']
for a in add['accessors']:a['bufferView']+=vo
base['accessors']+=add['accessors'];base['materials']+=add['materials']
for me in add['meshes']:
 for p in me['primitives']:
  p['material']+=mo;p['indices']+=ao;p['attributes']={k:v+ao for k,v in p['attributes'].items()}
base['meshes']+=add['meshes']
for n in add['nodes']:
 if 'mesh' in n:n['mesh']+=meo
 if 'children' in n:n['children']=[v+no for v in n['children']]
base['nodes']+=add['nodes'];base['scenes'][base.get('scene',0)]['nodes'] +=[v+no for v in add['scenes'][add.get('scene',0)]['nodes']]
for field in ['extensionsUsed','extensionsRequired']:
 if field in add:base[field]=list(dict.fromkeys(base.get(field,[])+add[field]))
save(base,bb,R/'web/ekimae.glb')
print('Candidate',sha((R/'web/ekimae.glb').read_bytes()))
