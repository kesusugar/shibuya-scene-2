"""Append-only source235 localized cap cluster. All accepted bytes/meshes remain exact.
Dark framed10x3 opaque panel and two short glazed ribbons. No holes or function claim.
"""
from pathlib import Path
import json,struct,hashlib
import numpy as np
ROOT=Path(__file__).resolve().parents[2]
BASE=ROOT/'source/baseline/mark-city-before-west-cap.glb'
SHA='9e795e55da8983bb34d8b32ce3e8bf4e32acee2bd78ae3182de01de805728292'
SOURCE_SHA='ac0b62994521aed4ae7156cee2d609c7beaa2f6a3509743a197a123429e4368b'
SCOPE_SHA='420aafd348689a0ac0e4d0643382f3bedf32b033a7a7611862b1cd75cb436c67'
def sha(path):return hashlib.sha256(Path(path).read_bytes()).hexdigest()
def read(path):
 raw=Path(path).read_bytes();assert struct.unpack_from('<II',raw)==(0x46546c67,2)
 n=struct.unpack_from('<I',raw,12)[0];return json.loads(raw[20:20+n]),bytearray(raw[28+n:])
def accessor(j,b,i):
 a=j['accessors'][i];v=j['bufferViews'][a['bufferView']];dt={5126:'<f4',5125:'<u4',5123:'<u2',5121:'u1'}[a['componentType']];nc={'SCALAR':1,'VEC2':2,'VEC3':3,'VEC4':4}[a['type']]
 assert not a.get('sparse') and not v.get('byteStride')
 return np.frombuffer(b,dtype=dt,count=a['count']*nc,offset=v.get('byteOffset',0)+a.get('byteOffset',0)).reshape(-1,nc).copy()
def to_source(v):return np.stack((v[:,0],-v[:,2],v[:,1]),axis=1)
def to_gltf(v):return np.stack((v[:,0],v[:,2],-v[:,1]),axis=1)
def build(output):
 assert sha(BASE)==SHA and sha(ROOT/'source/data/plateau.json')==SOURCE_SHA
 assert sha(ROOT/'source/data/west-cap-cluster-scope.json')==SCOPE_SHA
 scope=json.loads((ROOT/'source/data/west-cap-cluster-scope.json').read_text());params=json.loads((ROOT/'source/data/west-cap-parameters.json').read_text());src=json.loads((ROOT/'source/data/plateau.json').read_text())
 assert scope['accepted_glb_sha256']==SHA and scope['source_index']==params['source_face']==235
 assert src['surfaces'][235]['ring']==scope['source_geometry']['ring'] and scope['empty_removal_selector']
 geom=scope['source_geometry'];a=np.array(geom['a']);t=np.array(geom['t']);n=np.array(geom['outward']);j,b=read(BASE)
 assert len(j['meshes'])==25 and len(j['nodes'])==25 and len(j['materials'])==22
 def append(arr,typ,ct):
  while len(b)%4:b.extend(b'\0')
  arr=np.asarray(arr,dtype='<f4' if ct==5126 else '<u4');off=len(b);data=arr.tobytes();b.extend(data);vi=len(j['bufferViews']);j['bufferViews'].append({'buffer':0,'byteOffset':off,'byteLength':len(data)})
  ai=len(j['accessors']);aa={'bufferView':vi,'componentType':ct,'count':len(arr),'type':typ}
  if typ=='VEC3':aa.update(min=arr.min(0).tolist(),max=arr.max(0).tolist())
  j['accessors'].append(aa);return ai
 groups={k:{'v':[],'n':[],'i':[]} for k in ['dark_opaque','glass','frame']};records=[]
 def rect(kind,u0,u1,z0,z1,depth):
  assert u0<u1 and z0<z1
  vs=to_gltf(np.array([a+t*u0+n*depth+[0,0,z0],a+t*u0+n*depth+[0,0,z1],a+t*u1+n*depth+[0,0,z1],a+t*u1+n*depth+[0,0,z0]])).astype('<f4');g=groups[kind];start=len(g['v']);g['v'].extend(vs)
  nn=np.cross(vs[1].astype(float)-vs[0],vs[2].astype(float)-vs[0]);nn/=np.linalg.norm(nn);g['n'].extend([nn]*4);g['i'].extend([[start,start+1,start+2],[start,start+2,start+3]])
 u0,u1=params['u_range'];fw=params['vertical_frame_width_m'];fh=params['horizontal_frame_height_m'];depth=params['surface_outward_m'];fd=params['frame_outward_m']
 assert [u0,u1]==scope['layout_inferred_not_surveyed']['dark_opaque_screen_proxy']['u']==[7.6,37.4]
 def framed_region(z0,z1,cols,rows,fill_kind):
  # Horizontal bars span the entire rectangle; vertical segments stop between bars.
  # This avoids coplanar frame-strip intersections and keeps every frame INSIDE bounds.
  us=np.linspace(u0,u1,cols+1);zs=np.linspace(z0,z1,rows+1)
  for z in zs:rect('frame',u0,u1,max(z0,z-fh/2),min(z1,z+fh/2),fd)
  for lo,hi in zip(zs[:-1],zs[1:]):
   for u in us:rect('frame',max(u0,u-fw/2),min(u1,u+fw/2),lo+fh/2,hi-fh/2,fd)
  if fill_kind=='dark_opaque':
   for lo,hi in zip(zs[:-1],zs[1:]):
    for l,r in zip(us[:-1],us[1:]):rect(fill_kind,l+fw/2,r-fw/2,lo+fh/2,hi-fh/2,depth)
  else:rect(fill_kind,u0,u1,z0,z1,depth)
  records.append({'kind':fill_kind,'u_range':[u0,u1],'z_range':[z0,z1],'bays':cols,'tiers':rows,'surface_outward_m':depth,'frame_outward_m':fd,'outer_frames_contained':True})
 framed_region(*params['dark_z_range'],params['dark_bays'],params['dark_tiers'],'dark_opaque')
 for zr in params['glass_z_ranges']:framed_region(*zr,params['glass_bays_inferred'],1,'glass')
 dark_mat=len(j['materials']);j['materials'].append({'name':'west_cap_panel_opaque','doubleSided':False,'alphaMode':'OPAQUE','pbrMetallicRoughness':{'baseColorFactor':[.055,.068,.071,1],'metallicFactor':0,'roughnessFactor':.9}})
 frame_mat=len(j['materials']);j['materials'].append({'name':'west_cap_frame','doubleSided':False,'alphaMode':'OPAQUE','pbrMetallicRoughness':{'baseColorFactor':[.54,.56,.55,1],'metallicFactor':.5,'roughnessFactor':.45}})
 for kind,g in groups.items():
  name='mark-city_west_cap_'+kind;mi=len(j['meshes']);node=len(j['nodes']);p={'attributes':{'POSITION':append(g['v'],'VEC3',5126),'NORMAL':append(g['n'],'VEC3',5126)},'indices':append(np.array(g['i']).reshape(-1,1),'SCALAR',5125),'material':20 if kind=='glass' else (dark_mat if kind=='dark_opaque' else frame_mat),'mode':4}
  j['meshes'].append({'name':name,'primitives':[p]});j['nodes'].append({'name':name,'mesh':mi});j['scenes'][j.get('scene',0)]['nodes'].append(node)
 j['buffers'][0]['byteLength']=len(b);js=json.dumps(j,separators=(',',':')).encode();js+=b' '*((-len(js))%4);b+=b'\0'*((-len(b))%4)
 out=struct.pack('<III',0x46546c67,2,28+len(js)+len(b))+struct.pack('<II',len(js),0x4e4f534a)+js+struct.pack('<II',len(b),0x004e4942)+b
 output=Path(output);output.parent.mkdir(parents=True,exist_ok=True);output.write_bytes(out)
 report=json.loads((ROOT/'source/baseline/before-west-cap.east-stats.json').read_text());report.update(west_cap_correction={'source_face':235,'removed_triangles':0,'retained_accepted_triangles':25122,'retained_inward_cap_overlay_triangles':1254,'features':records,'parameters':params,'added_triangles':sum(len(g['i']) for g in groups.values()),'preservation':'Entire accepted binary payload, all meshes, attributes, materials and nodes unchanged. Three meshes/nodes and two safe-named wall materials appended; scene root membership extended. No235 shell/hidden-overlay,279/return,240/299,roof or EAST edits.'},prior_stage_glb_sha256=SHA,triangles=sum(j['accessors'][p['indices']]['count']//3 for m in j['meshes'] for p in m['primitives']),primitives=sum(len(m['primitives']) for m in j['meshes']),bytes=len(out),sha256=hashlib.sha256(out).hexdigest())
 return report
