"""blender -b -P source/validate.py -- OUTPUT_DIR"""
import bpy,sys,json,hashlib
from pathlib import Path
from mathutils import Vector
root=Path(sys.argv[sys.argv.index('--')+1]).resolve()
bpy.ops.wm.open_mainfile(filepath=str(root/'soffit_dome_fixture.blend'))
objs=[o for o in bpy.context.scene.objects if o.type=='MESH'];assert len(objs)==3
pts=[o.matrix_world@v.co for o in objs for v in o.data.vertices]
mins=[min(p[i] for p in pts) for i in range(3)];maxs=[max(p[i] for p in pts) for i in range(3)]
assert max(abs(mins[i]+.06) for i in [0,1])<1e-7
assert max(abs(maxs[i]-.06) for i in [0,1])<1e-7
assert abs(mins[2])<1e-7 and abs(maxs[2]-.09)<1e-7
assert all(o.location.length<1e-9 and tuple(o.scale)==(1,1,1) for o in objs)
assert not [o for o in bpy.context.scene.objects if o.type in {'LIGHT','CAMERA'}]
assert not [im for im in bpy.data.images if im.source=='FILE']
assert len({m.name for o in objs for m in o.data.materials})==2
assert abs((2.57+maxs[2])-2.66)<1e-7
bpy.ops.object.select_all(action='SELECT')
bpy.ops.export_scene.gltf(filepath=str(root/'editable_check.glb'),export_format='GLB',use_selection=True,export_yup=True,export_extras=False,export_cameras=False,export_lights=False)
original=(root/'soffit_dome_fixture.glb').read_bytes();editable=(root/'editable_check.glb').read_bytes();assert original==editable
json.dump({'pass':True,'blender':bpy.app.version_string,'mesh_count':3,'materials':2,'bbox_min':mins,'bbox_max':maxs,'origin_bottom_centre':True,'top_plane':.09,'attachment_contact_error_m':abs(2.57+maxs[2]-2.66),'editable_export_byte_exact':True,'glb_sha256':hashlib.sha256(original).hexdigest()},open(root/'validation.json','w'),indent=2)
