import bpy,json,sys
from pathlib import Path
from mathutils import Vector
p=Path(sys.argv[sys.argv.index('--')+1]);bpy.ops.wm.open_mainfile(filepath=str(p))
objs=[o for o in bpy.context.scene.objects if o.type=='MESH'];assert len(objs)==4
assert all(o.location.length<1e-6 and all(abs(x-1)<1e-6 for x in o.scale) for o in objs)
vs=[o.matrix_world@v.co for o in objs for v in o.data.vertices]
lo=[min(v[k] for v in vs) for k in range(3)];hi=[max(v[k] for v in vs) for k in range(3)]
assert abs(lo[2])<1e-6 and abs(lo[0]+hi[0])<1e-6 and abs(lo[1]+hi[1])<1e-6
assert abs(hi[2]-.18)<1e-5 and abs(hi[0]-lo[0]-3.65)<1e-5
assert not [i for i in bpy.data.images if i.source=='FILE'];assert not bpy.data.libraries
print('EDITABLE PASS',json.dumps({'mesh_objects':len(objs),'bounds_blender':[lo,hi],'unit_scale':bpy.context.scene.unit_settings.scale_length}))
