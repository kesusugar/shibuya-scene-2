import bpy,json,sys,math
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
report=[]
for p in sorted((ROOT/'web').glob('*.glb')):
 bpy.ops.wm.read_factory_settings(use_empty=True);bpy.ops.import_scene.gltf(filepath=str(p))
 obs=list(bpy.context.scene.objects);ms=[o for o in obs if o.type=='MESH']
 assert ms and not any(o.type in ['CAMERA','LIGHT'] for o in obs)
 coords=[o.matrix_world@v.co for o in ms for v in o.data.vertices]
 assert all(math.isfinite(x) for v in coords for x in v)
 assert all(o.matrix_world.determinant()>0 for o in ms)
 report.append({'file':p.name,'status':'pass','mesh_objects':len(ms),'triangles':sum(len(po.vertices)-2 for o in ms for po in o.data.polygons),'bounds_blender_zup':[[min(v[i] for v in coords) for i in range(3)],[max(v[i] for v in coords) for i in range(3)]],'positive_transforms':True})
(ROOT/'qa'/'blender_reimport.json').write_text(json.dumps({'blender':bpy.app.version_string,'results':report},indent=2));print(report)
