"""Read-only structural/budget validation of source GLB and temporary PR38 LOD output.
python3 check_glb.py <source.glb> <imported.glb> <report.json>
"""
import json,struct,sys
from pathlib import Path

def inspect(path):
 data=Path(path).read_bytes()
 magic,version,length=struct.unpack_from('<4sII',data)
 assert magic==b'glTF' and version==2 and length==len(data)
 n,kind=struct.unpack_from('<II',data,12);assert kind==0x4e4f534a
 g=json.loads(data[20:20+n]);tris=0;primitives=0
 for m in g['meshes']:
  for p in m['primitives']:
   assert p.get('mode',4)==4
   tris+=g['accessors'][p['indices']]['count']//3;primitives+=1
 assert not g.get('cameras') and not g.get('textures')
 return {'bytes':len(data),'triangles':tris,'primitives':primitives,'mesh_count':len(g['meshes']),'materials':[m['name'] for m in g['materials']],'nodes':[n.get('name','') for n in g['nodes']]}
src=inspect(sys.argv[1]);out=inspect(sys.argv[2])
assert src['triangles']==2676 and src['mesh_count']==3 and src['primitives']==3
assert out['triangles']==2676+669 and out['mesh_count']==2
assert out['materials']==['prop_furniture_0','prop_furniture_1']
assert set(out['nodes'])=={'hachiko_white_bollard','hachiko_white_bollard_lod1'}
assert src['bytes']<400000 and out['bytes']<400000
report={'status':'PASS','source':src,'temporary_importer_output':out,'limits':{'LOD0_triangles':3000,'LOD1_triangles':750,'validation_bytes_each':400000},'warning':'Temporary imported GLB contains overlapping LOD0 and LOD1; excluded from committed incoming source. Runtime must select one LOD.','npm_suite':'NOT RUN: full repository and dependencies unavailable; no runtime integration or FPS claim.'}
Path(sys.argv[3]).write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n')
print(json.dumps(report,ensure_ascii=False,indent=2))
