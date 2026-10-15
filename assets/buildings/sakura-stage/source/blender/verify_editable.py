"""Read-only editable scene closure and exact GLB import equivalence; Blender 4.2.3."""
import bpy,json,hashlib,collections
from pathlib import Path
A=Path(__file__).resolve().parents[2]
assert bpy.app.version==(4,2,3)
def geometry():
 result={}
 for o in bpy.data.objects:
  if o.type!='MESH':continue
  o.data.calc_loop_triangles()
  tris=collections.Counter()
  for t in o.data.loop_triangles:
   pts=tuple(sorted(tuple(round(float(x),6) for x in (o.matrix_world@o.data.vertices[i].co)) for i in t.vertices))
   mat=o.data.materials[t.material_index].name if o.data.materials else None
   tris[(mat,pts)]+=1
  result[o.name]=tris
 return result
p=A/'source/blender/sakura-stage.blend';h=hashlib.sha256(p.read_bytes()).hexdigest();bpy.ops.wm.open_mainfile(filepath=str(p));assert not bpy.data.libraries;assert not [x for x in bpy.data.images if x.source=='FILE'];assert bpy.context.scene.unit_settings.scale_length==1
actual=geometry();bpy.ops.wm.read_factory_settings(use_empty=True);bpy.ops.import_scene.gltf(filepath=str(A/'web/sakura-stage.glb'));assert actual==geometry();assert hashlib.sha256(p.read_bytes()).hexdigest()==h
print(json.dumps({'status':'PASS','blender':bpy.app.version_string,'mesh_count':len(actual),'triangle_count':sum(sum(v.values()) for v in actual.values()),'external_libraries':0,'external_images':0,'editable_vs_final_glb':'exact world-space triangles and material assignments at 1e-6m','blend_sha256':h}))
