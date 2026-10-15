"""Minimal index-only correction of proven inherited concave-wall triangulation.
No position/material/other-face/GLB JSON change. Only target152 normals733/734 flip.
"""
import json,struct,hashlib
REPAIRS={52:([293,296,299],[291,292,295]),272:([298,291,292],[291,295,298]),367:([730,733,734],[721,723,728]),368:([730,734,735],[728,732,733]),370:([726,731,737],[721,728,733]),372:([722,725,736],[721,733,734]),373:([721,723,738],[721,734,738])}
BASELINE_SHA='9fa2046b02ac220b305c67241a19b607ea39d2e0a7beedd953cb0a761d3152e2'
def repair_podium_topology(raw):
 assert hashlib.sha256(raw).hexdigest()==BASELINE_SHA,'Unexpected baseline, refuse patch'
 result=bytearray(raw);jl=struct.unpack_from('<I',raw,12)[0];j=json.loads(raw[20:20+jl]);binstart=20+jl+8
 mesh=j['meshes'][1];assert mesh['name']=='parco_wall';pr=mesh['primitives'][0];assert pr=={'attributes':{'POSITION':3,'NORMAL':4},'indices':5,'material':1}
 ac=j['accessors'][5];assert ac['componentType']==5123 and ac['type']=='SCALAR';bv=j['bufferViews'][ac['bufferView']]
 indexstart=binstart+bv.get('byteOffset',0)+ac.get('byteOffset',0);records=[]
 for triangle,(old,new) in REPAIRS.items():
  start=indexstart+triangle*3*2;assert list(struct.unpack_from('<3H',raw,start))==old
  struct.pack_into('<3H',result,start,*new);records.append({'triangle':triangle,'old':old,'new':new,'glb_byte_offset':start,'byte_length':6})
 # 733/734 occur only in five replaced152 triangles; no unrelated normal is touched.
 nac=j['accessors'][4];nbv=j['bufferViews'][nac['bufferView']];nst=binstart+nbv.get('byteOffset',0)+nac.get('byteOffset',0)
 normals=[]
 for vi in [733,734]:
  start=nst+vi*12;old=list(struct.unpack_from('<3f',raw,start));assert old==[0.050700705498456955,0.0,0.9987139105796814]
  for component in [0,2]:
   offset=start+component*4;word=struct.unpack_from('<I',raw,offset)[0];struct.pack_into('<I',result,offset,word^0x80000000)
  normals.append({'vertex':vi,'glb_byte_offset':start,'byte_length':12,'old':old,'new':[-old[0],old[1],-old[2]],'usage':'only replaced source152 triangles'})
 out=bytes(result);changed=[i for i,(a,b) in enumerate(zip(raw,out)) if a!=b]
 allowed={i for r in records+normals for i in range(r['glb_byte_offset'],r['glb_byte_offset']+r['byte_length'])};assert set(changed)<=allowed
 report={'kind':'source108/152 concave polygon triangulation repair','baseline_sha256':BASELINE_SHA,'corrected_baseline_sha256':hashlib.sha256(out).hexdigest(),'repairs':records,'normal_repairs':normals,'changed_byte_count':len(changed),'allowed_index_bytes':42,'target_normal_vertices_changed':2,'position_attributes_changed':0,'source_ring_changed':False,'source171_changed':False,'source152_changed':True,'basis':'Independent projection/union audit: original108 spill49.062692m2 and overlap358.319806m2. Correct valid0-3 diagonal instead of1-5. Source152 notch spill111.191903m2 also removed. All original source boundary positions unchanged. Runtime regression verifies final exported fill against source polygon.'}
 return out,report
