import bpy,json,sys
from pathlib import Path
from mathutils import Vector
R=Path(__file__).resolve().parents[1]
report={}
for file in ['surround_before.glb','hachiko_surround_v002.glb','hachiko_low_shrubs_only_v002.glb']:
 bpy.ops.wm.read_factory_settings(use_empty=True);bpy.ops.import_scene.gltf(filepath=str(R/'models'/file))
 meshes=[o for o in bpy.context.scene.objects if o.type=='MESH'];points=[o.matrix_world@Vector(c) for o in meshes for c in o.bound_box]
 lo=[min(p[i] for p in points) for i in range(3)];hi=[max(p[i] for p in points) for i in range(3)]
 report[file]={'mesh_names':[o.name for o in meshes],'vertices':sum(len(o.data.vertices) for o in meshes),'triangles':sum(len(p.vertices)-2 for o in meshes for p in o.data.polygons),'world_bbox_blender_z_up_m':{'min':lo,'max':hi,'extent':[hi[i]-lo[i] for i in range(3)]},'images':[{'name':i.name,'size':list(i.size),'alpha_mode':i.alpha_mode,'packed':bool(i.packed_file)} for i in bpy.data.images if i.size[0]>0]}
 assert len(meshes)>0
(R/'validation/roundtrip.json').write_text(json.dumps(report,indent=2)+'\n')
print(json.dumps(report,indent=2))
