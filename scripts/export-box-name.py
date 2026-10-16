"""Extract the existing authored factual name only; never restore its old carrier.
Blender 4.2.3; run from repository root. No new lettering or source imagery.
"""
import bpy, hashlib, json
from pathlib import Path
from mathutils import Vector
R=Path(__file__).resolve().parents[1]
source=R/'assets/street/props/incoming/shibu_hachi_box_architecture_reference/output/shibu_hachi_box.blend'
assert bpy.app.version==(4,2,3)
assert hashlib.sha256(source.read_bytes()).hexdigest()=='54e6add82ba35918f01496ab1a4402bdf6ad994edf1e7d26f893f8afb1528ec2'
bpy.ops.wm.open_mainfile(filepath=str(source))
name=bpy.data.objects['SHIBU_HACHI_BOX_factual_identifier']
points=[name.matrix_world@v.co for v in name.data.vertices]
lo=Vector(tuple(min(p[i] for p in points) for i in range(3)));hi=Vector(tuple(max(p[i] for p in points) for i in range(3)))
offset=Vector(((lo.x+hi.x)/2,(lo.y+hi.y)/2,lo.z))
for v in name.data.vertices:v.co-=offset
bpy.ops.object.select_all(action='DESELECT');name.select_set(True);bpy.context.view_layer.objects.active=name
out=R/'assets/buildings/shibu-hachi-box/source/exterior-signs/existing-name.glb'
out.parent.mkdir(parents=True,exist_ok=True)
bpy.ops.export_scene.gltf(filepath=str(out),export_format='GLB',use_selection=True,export_yup=True,export_extras=False,export_cameras=False,export_lights=False)
print('Original name only; normalized bottom centre',list(offset),'size',list(hi-lo))
