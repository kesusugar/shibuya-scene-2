"""Verify editable mesh export and absence of external dependencies in Blender 4.2.3."""
import bpy,hashlib,tempfile,json
from pathlib import Path
R=Path(__file__).resolve().parent
assert bpy.app.version[:3]==(4,2,3)
bpy.ops.wm.open_mainfile(filepath=str(R/'asset/source/blender/takagi.blend'))
assert not bpy.data.libraries and not bpy.data.images and not bpy.data.fonts and not bpy.data.texts
assert not any(o.type in ['FONT','CURVE'] for o in bpy.context.scene.objects)
bpy.ops.object.select_all(action='DESELECT')
meshes=[o for o in bpy.context.scene.objects if o.type=='MESH']
for o in meshes:o.select_set(True)
with tempfile.TemporaryDirectory() as td:
 p=Path(td)/'editable.glb'
 bpy.ops.export_scene.gltf(filepath=str(p),export_format='GLB',use_selection=True,export_yup=True)
 assert p.read_bytes()==(R/'asset/web/takagi.glb').read_bytes(), 'Editable export differs'
print(json.dumps({'editable_export_byte_identical':True,'mesh_objects':len(meshes),'external_dependencies':False,'glb_sha256':hashlib.sha256((R/'asset/web/takagi.glb').read_bytes()).hexdigest()}))
