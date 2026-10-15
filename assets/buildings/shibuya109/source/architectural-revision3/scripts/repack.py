"""Deterministic lossless removal of unreachable mesh/accessor/buffer payload.
No quantization, coordinate conversion, normal recomputation or attribute edits.
"""
import copy,json,struct,hashlib
from pathlib import Path
from glb_helpers import load,acc,sha

def repack(path):
 j,b=load(path);old=copy.deepcopy(j);oldraw=Path(path).read_bytes()
 meshes=sorted({n['mesh'] for n in j['nodes'] if 'mesh'in n});mm={k:i for i,k in enumerate(meshes)};j['meshes']=[j['meshes'][k] for k in meshes]
 for n in j['nodes']:
  if 'mesh'in n:n['mesh']=mm[n['mesh']]
 used=set()
 for m in j['meshes']:
  for p in m['primitives']:
   used.update(p['attributes'].values());used.add(p['indices'])
   for t in p.get('targets',[]):used.update(t.values())
 for s in j.get('skins',[]):
  if 'inverseBindMatrices'in s:used.add(s['inverseBindMatrices'])
 for an in j.get('animations',[]):
  for s in an['samplers']:used.update([s['input'],s['output']])
 aa={k:i for i,k in enumerate(sorted(used))};j['accessors']=[j['accessors'][k] for k in sorted(used)]
 for m in j['meshes']:
  for p in m['primitives']:
   p['attributes']={k:aa[v] for k,v in p['attributes'].items()};p['indices']=aa[p['indices']]
   for t in p.get('targets',[]):
    for k in t:t[k]=aa[t[k]]
 for s in j.get('skins',[]):
  if 'inverseBindMatrices'in s:s['inverseBindMatrices']=aa[s['inverseBindMatrices']]
 for an in j.get('animations',[]):
  for s in an['samplers']:
   for k in ['input','output']:s[k]=aa[s[k]]
 views={a['bufferView'] for a in j['accessors']};views.update(im['bufferView'] for im in j.get('images',[]) if 'bufferView'in im)
 assert all('sparse'not in a for a in j['accessors'])
 vm={k:i for i,k in enumerate(sorted(views))};nb=bytearray();newviews=[];hashes=[]
 for k in sorted(views):
  v=copy.deepcopy(old['bufferViews'][k]);assert v.get('buffer',0)==0
  while len(nb)%4:nb.append(0)
  payload=b[v.get('byteOffset',0):v.get('byteOffset',0)+v['byteLength']];v['byteOffset']=len(nb);v['buffer']=0;nb.extend(payload);newviews.append(v);hashes.append({'old_view':k,'new_view':vm[k],'sha256':sha(payload),'bytes':len(payload)})
 j['bufferViews']=newviews
 for a in j['accessors']:a['bufferView']=vm[a['bufferView']]
 for im in j.get('images',[]):
  if 'bufferView'in im:im['bufferView']=vm[im['bufferView']]
 for oi,ni in aa.items():assert acc(old,b,oi)==acc(j,nb,ni),oi
 j['buffers'][0]['byteLength']=len(nb);jb=json.dumps(j,separators=(',',':')).encode();jb+=b' '*(-len(jb)%4);nb+=b'\0'*(-len(nb)%4);raw=struct.pack('<III',0x46546c67,2,28+len(jb)+len(nb))+struct.pack('<II',len(jb),0x4e4f534a)+jb+struct.pack('<II',len(nb),0x004e4942)+nb
 path=Path(path);path.with_name('pre-repack.glb').write_bytes(oldraw);path.write_bytes(raw)
 report={'before_sha256':sha(oldraw),'after_sha256':sha(raw),'before_bytes':len(oldraw),'after_bytes':len(raw),'mesh_map':mm,'accessor_map':aa,'buffer_view_map':vm,'view_payload_hashes':hashes,'all_active_accessor_values_exact':True,'all_retained_view_bytes_exact':True,'materials_unchanged':j['materials']==old['materials'],'nodes_changed_only_mesh_index':True}
 path.with_name('repack-report.json').write_text(json.dumps(report,indent=2));return report
