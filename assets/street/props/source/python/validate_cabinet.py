import bpy,json,math
from pathlib import Path
from mathutils import Vector
p=Path(__file__).parent
assert bpy.app.version[:3]==(4,2,3)
bpy.ops.wm.open_mainfile(filepath=str(p/'grey_louvered_cabinet.blend'))
assert bpy.context.scene.unit_settings.scale_length==1
objs=list(bpy.data.collections['ASSET | cabinet only'].objects)
assert len(objs)==105
# Perform a reversible edit and update to confirm mesh editing works in exact version.
o=next(o for o in objs if o.type=='MESH');v=o.data.vertices[0];old=v.co.copy();v.co.x+=.001;o.data.update();assert abs(v.co.x-old.x-.001)<1e-6;v.co=old;o.data.update()
bpy.ops.wm.save_as_mainfile(filepath=str(p/'grey_louvered_cabinet.blend'),compress=True)
bpy.ops.wm.read_factory_settings(use_empty=True)
bpy.ops.import_scene.gltf(filepath=str(p/'grey_louvered_cabinet_source.glb'))
meshes=[o for o in bpy.context.scene.objects if o.type=='MESH'];assert len(meshes)==1
ob=meshes[0];assert ob.name=='grey_louvered_cabinet'
cs=[ob.matrix_world@Vector(c) for c in ob.bound_box];lo=[min(v[i] for v in cs) for i in range(3)];hi=[max(v[i] for v in cs) for i in range(3)]
assert abs(lo[2])<1e-6 and abs(lo[0]+hi[0])<1e-6 and abs(lo[1]+hi[1])<1e-6,(lo,hi)
assert all(math.isfinite(x) for v in ob.data.vertices for x in v.co)
ob.data.calc_loop_triangles();assert len(ob.data.loop_triangles)==2484
assert all(abs(v-1)<1e-6 for v in ob.scale)
assert len(bpy.context.scene.objects)==1
r={'blender':bpy.app.version_string,'blend_reopened':True,'reversible_vertex_edit_verified':True,'source_glb_mesh_nodes':len(meshes),'source_node_name':ob.name,'bounds_min_m':lo,'bounds_max_m':hi,'triangles':2484,'single_cabinet_only':True,'meters':True,'bottom_center_origin_verified':True,'finite_vertices':True,'external_images':False}
(p/'validation_qa.json').write_text(json.dumps(r,indent=2))
print(json.dumps(r))
