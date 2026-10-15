"""Blender4.2.3: blender -b -P scripts/build.py [-- --phase2]
Pinned predecessor bytes retained. All removals refer to ORIGINAL triangle indices.
"""
import sys,json,struct,hashlib,copy,collections
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parent))
from glb_helpers import load,acc,to_gltf,sha
import entrance
ROOT=Path(__file__).resolve().parents[1]
def build(phase2=True):
 j,oldb=load(ROOT/'inputs/prior.glb');assert sha((ROOT/'inputs/prior.glb').read_bytes())=='a31e295bf8ce9bbef9ddc0c6164526db84cb7b08a6caf1957352be142854db90';oldj=copy.deepcopy(j);b=bytearray(oldb)
 pins=json.loads((ROOT/'inputs/INPUTS.json').read_text())
 for filename,digest in pins.items():assert sha((ROOT/'inputs'/filename).read_bytes())==digest,filename
 plans=[entrance.build()]
 if phase2:
  import phase2 as p2
  plans.append(p2.build())
 def append(vals,typ,ct=5126):
  while len(b)%4:b.append(0)
  offset=len(b);fmt={5126:'f',5125:'I',5123:'H'}[ct];flat=[v for x in vals for v in (x if isinstance(x,(list,tuple)) else [x])];b.extend(struct.pack('<'+fmt*len(flat),*flat));vi=len(j['bufferViews']);j['bufferViews'].append({'buffer':0,'byteOffset':offset,'byteLength':len(b)-offset});a={'bufferView':vi,'componentType':ct,'count':len(vals),'type':typ}
  if typ=='VEC3':a.update(min=[min(x[k] for x in vals) for k in range(3)],max=[max(x[k] for x in vals) for k in range(3)])
  ai=len(j['accessors']);j['accessors'].append(a);return ai
 masks=collections.defaultdict(set)
 for plan in plans:
  for k,v in plan['remove'].items():masks[int(k)].update(v)
 for mi,rm in masks.items():
  assert len(j['meshes'][mi]['primitives'])==1
  p=j['meshes'][mi]['primitives'][0];ii=[x[0] for x in acc(oldj,oldb,p['indices'])];assert max(rm)<len(ii)//3
  keep=[i for t in range(len(ii)//3) if t not in rm for i in ii[t*3:t*3+3]]
  if keep:p['indices']=append(keep,'SCALAR',5125)
  else:
   # Keep original mesh data but remove its scene node, preserving all unrelated node transforms.
   for ni,n in enumerate(j['nodes']):
    if n.get('mesh')==mi:
     n.pop('mesh')
     for scene in j['scenes']:
      if ni in scene['nodes']:scene['nodes'].remove(ni)
 additions=[a for plan in plans for a in plan['additions']]
 grouped={}
 for a in additions:
  key=('existing',a['existing_material']) if 'existing_material' in a else ('new',json.dumps(a['material'],sort_keys=True))
  if key not in grouped:grouped[key]=copy.deepcopy(a)
  else:
   g=grouped[key];n=len(g['vertices']);g['vertices'].extend(a['vertices']);g['normals'].extend(a['normals']);g['triangles'].extend([[i+n for i in t] for t in a['triangles']]);gc=g.get('colors');ac=a.get('colors')
   if gc or ac:g['colors']=(gc or [[1,1,1,1]]*n)+(ac or [[1,1,1,1]]*len(a['vertices']))
   else:g.pop('colors',None)
 record=[]
 for a in grouped.values():
  vs,ns,cs,ii=[],[],[],[];lookup={};cols=a.get('colors');hascols=cols is not None and len(cols)>0 and any(any(abs(x-1)>1e-9 for x in c) for c in cols)
  if hascols:assert len(cols)==len(a['vertices']),(a['name'],len(cols),len(a['vertices']))
  for tri in a['triangles']:
   for vi in tri:
    v=to_gltf(a['vertices'][vi]);n=to_gltf(a['normals'][vi]);c=cols[vi] if hascols else None
    # Exactfloat32 key compacts duplicate attributes without welding hard normals.
    key=struct.pack('<'+'f'*(10 if hascols else 6),*(list(v)+list(n)+(list(c) if c else[])))
    if key not in lookup:
     lookup[key]=len(vs);vs.append(v);ns.append(n)
     if hascols:cs.append(c)
    ii.append(lookup[key])
  if 'existing_material' in a:matid=a['existing_material']
  else:matid=len(j['materials']);j['materials'].append(a['material'])
  attrs={'POSITION':append(vs,'VEC3'),'NORMAL':append(ns,'VEC3')}
  if hascols:attrs['COLOR_0']=append(cs,'VEC4')
  p={'attributes':attrs,'indices':append(ii,'SCALAR',5123 if len(vs)<65536 else 5125),'material':matid,'mode':4};mi=len(j['meshes']);j['meshes'].append({'name':a['name'],'primitives':[p]});ni=len(j['nodes']);j['nodes'].append({'name':a['name'],'mesh':mi});j['scenes'][j.get('scene',0)]['nodes'].append(ni);record.append({'mesh':mi,'name':a['name'],'triangles':len(ii)//3,'vertices':len(vs),'material':matid})
 assert bytes(b[:len(oldb)])==oldb
 for mi,m in enumerate(oldj['meshes']):
  if mi not in masks:assert j['meshes'][mi]==m
 j['buffers'][0]['byteLength']=len(b);jb=json.dumps(j,separators=(',',':')).encode();jb+=b' '*(-len(jb)%4);b+=b'\0'*(-len(b)%4);raw=struct.pack('<III',0x46546c67,2,28+len(jb)+len(b))+struct.pack('<II',len(jb),0x4e4f534a)+jb+struct.pack('<II',len(b),0x004e4942)+b
 out=ROOT/'output'/('combined' if phase2 else'entrance');out.mkdir(exist_ok=True,parents=True);(out/'shibuya109.glb').write_bytes(raw)
 active=[j['nodes'][ni]['mesh'] for ni in j['scenes'][0]['nodes'] if 'mesh'in j['nodes'][ni]]
 report={'predecessor_sha256':sha((ROOT/'inputs/prior.glb').read_bytes()),'sha256':sha(raw),'pre_repack_binary_prefix_preserved':True,'removed_original_triangle_indices':{str(k):sorted(v) for k,v in masks.items()},'additions':record,'triangles':sum(j['accessors'][p['indices']]['count']//3 for m in active for p in j['meshes'][m]['primitives']),'active_primitives':sum(len(j['meshes'][m]['primitives']) for m in active),'bytes':len(raw),'phase_reports':[p.get('report',{}) for p in plans]}
 (out/'report.json').write_text(json.dumps(report,indent=2));print('BUILT',out,report['triangles'],report['active_primitives'],len(raw),flush=True)
 from repack import repack
 compact=repack(out/'shibuya109.glb');report['sha256']=compact['after_sha256'];report['bytes']=compact['after_bytes'];report['repack']='Lossless active bufferView content identity; dead historical payload removed';(out/'report.json').write_text(json.dumps(report,indent=2));print('COMPACT',report['bytes'],flush=True)
 import bpy
 assert bpy.app.version==(4,2,3);bpy.ops.wm.read_factory_settings(use_empty=True);bpy.ops.import_scene.gltf(filepath=str(out/'shibuya109.glb'));bpy.ops.file.pack_all();bpy.ops.wm.save_as_mainfile(filepath=str(out/'shibuya109.blend'),compress=True)
 return out
if __name__=='__main__':build('--entrance-only' not in sys.argv)
