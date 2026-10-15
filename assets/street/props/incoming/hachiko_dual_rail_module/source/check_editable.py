import bpy,sys,hashlib,json
from pathlib import Path
R=Path(sys.argv[sys.argv.index('--')+1]).resolve();bpy.ops.wm.open_mainfile(filepath=str(R/'hachiko_dual_rail_module.blend'));assert bpy.app.version[:3]==(4,2,3);assert not bpy.data.images
out=Path('/tmp/hachiko-rail-editable.glb');bpy.ops.export_scene.gltf(filepath=str(out),export_format='GLB',export_yup=True)
a=hashlib.sha256(out.read_bytes()).hexdigest();b=hashlib.sha256((R/'hachiko_dual_rail_module.glb').read_bytes()).hexdigest();assert a==b
(R/'evidence'/'editable_check.json').write_text(json.dumps({'passed':True,'blender':bpy.app.version_string,'glb_sha256':a,'editable_export_byte_exact':True},indent=2)+'\n')
