"""One-pass authoring-file audit; run via Blender 4.2.3 with output dir after --."""
import bpy,json,sys,math
from pathlib import Path
from mathutils import Vector
O=Path(sys.argv[sys.argv.index('--')+1]);bpy.ops.wm.open_mainfile(filepath=str(O/'shibu_hachi_counter_laptop.blend'))
s=bpy.context.scene;obs=[o for o in s.objects if o.type=='MESH'];assert len(obs)==80
assert bpy.app.version[:3]==(4,2,3) and s.unit_settings.system=='METRIC' and s.unit_settings.scale_length==1
assert len(s.objects)==len(obs) and all(i.source=='VIEWER' for i in bpy.data.images) and len(bpy.data.libraries)==0
assert all(all(abs(c)<1e-7 for c in o.location) for o in obs)
assert all(o.get('evidence') and o.get('asset_id') for o in obs)
assert all(len(o.modifiers)==0 for o in obs)
pts=[o.matrix_world@v.co for o in obs for v in o.data.vertices];mn=[min(p[i] for p in pts) for i in range(3)];mx=[max(p[i] for p in pts) for i in range(3)]
assert abs(mn[2])<1e-6 and abs(mn[0]+mx[0])<1e-6 and abs(mn[1]+mx[1])<1e-6
r={'status':'pass','blender':'4.2.3 LTS','editable_meshes':len(obs),'all_objects_have_evidence_classification':True,'origins_at_bottom_centre':True,'units':'metres','external_libraries':0,'external_images':0,'self_contained':True,'pack_status':'No external data dependencies exist; pack_all invoked in generator.','cameras':0,'lights':0,'modifiers_pending':0,'bounds_blender_m':[mn,mx]}
json.dump(r,open(O/'qa'/'blend_structure.json','w'),indent=2);print(r)
