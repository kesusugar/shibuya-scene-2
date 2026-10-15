import bpy,hashlib
from pathlib import Path
R=Path(__file__).resolve().parents[1];assert bpy.app.version==(4,2,3)
bpy.ops.wm.read_factory_settings(use_empty=True);bpy.ops.import_scene.gltf(filepath=str(R/'web/ekimae.glb'))
bpy.context.scene.unit_settings.system='METRIC';bpy.context.scene['status']='Review prototype, not accepted or photo-calibrated';bpy.context.scene['input_glb_sha256']=hashlib.sha256((R/'web/ekimae.glb').read_bytes()).hexdigest();bpy.ops.wm.save_as_mainfile(filepath=str(R/'source/ekimae-ground-frontage-prototype.blend'),compress=True)
