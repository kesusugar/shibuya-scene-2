import bpy,sys
from pathlib import Path
r=Path(__file__).resolve().parents[1];bpy.ops.wm.open_mainfile(filepath=str(r/'output/groundcover.blend'))
assert len(bpy.data.objects)==1 and len(bpy.data.images)==0
assert not bpy.data.libraries
obj=bpy.data.objects[0];assert tuple(obj.location)==(0,0,0) and tuple(obj.scale)==(1,1,1)
bpy.ops.export_scene.gltf(filepath='/tmp/hachiko_groundcover_blend_export.glb',export_format='GLB',use_selection=True,export_yup=True,export_extras=True)
assert Path('/tmp/hachiko_groundcover_blend_export.glb').read_bytes()==(r/'output/groundcover.glb').read_bytes()
print('PASS: editable blend exports byte-identical GLB; no images, libraries, lights or cameras')
