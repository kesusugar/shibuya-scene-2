"""Save an editable snapshot after build_ekimae.py; exact Blender 4.2.3.
Architecture and the separate November sign layer retain georeferenced coordinates.
"""
from pathlib import Path
import bpy
assert bpy.app.version == (4, 2, 3)
ROOT = Path(__file__).resolve().parents[2]
bpy.ops.wm.read_factory_settings(use_empty=True)
for name in ('ekimae.glb', 'signs-2025-11.glb'):
    bpy.ops.import_scene.gltf(filepath=str(ROOT / 'web' / name))
bpy.context.scene.unit_settings.system = 'METRIC'
bpy.context.scene.unit_settings.scale_length = 1
bpy.ops.file.pack_all()
bpy.ops.wm.save_as_mainfile(filepath=str(Path(__file__).with_name('ekimae-uv.blend')), compress=True)
