import bpy,sys,json
from pathlib import Path
p=Path(sys.argv[sys.argv.index('--')+1]).resolve();out=Path(sys.argv[sys.argv.index('--')+2]).resolve()
bpy.ops.wm.open_mainfile(filepath=str(p));objs=[o for o in bpy.context.scene.objects if o.type=='MESH'];assert len(objs)==1
assert not [o for o in bpy.context.scene.objects if o.type in ('LIGHT','CAMERA')]
assert not [i for i in bpy.data.images if i.source=='FILE']
o=objs[0];assert tuple(o.location)==(0,0,0);assert tuple(o.scale)==(1,1,1)
bpy.ops.object.select_all(action='DESELECT');o.select_set(True);bpy.context.view_layer.objects.active=o
bpy.ops.export_scene.gltf(filepath=str(out),export_format='GLB',use_selection=True,export_yup=True,export_extras=True)
print('EDITABLE_PASS')
