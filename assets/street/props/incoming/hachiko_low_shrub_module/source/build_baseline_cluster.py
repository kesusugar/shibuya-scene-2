"""Extracts the left middle shrub from saved current source. Not an exact main binary extraction."""
import bpy, math, random, json, textwrap
from pathlib import Path
from mathutils import Vector
ROOT=Path(__file__).resolve().parents[1];src=(ROOT/'source/baseline_build_surround.py').read_text()
bpy.ops.wm.read_factory_settings(use_empty=True)
exec(src[src.index('mats={}'):src.index("for seg in D['segments']:")])
D={'shrub_height_m':1.1,'needle_bundle_width_m':.012};x=0;yy=0;bottom=0;i=1;seg={'id':'left'}
part=src[src.index("  tube('shrub_trunk'"):src.index(' for i in range(3):')]
exec(textwrap.dedent(part))
exec(src[src.index("me=bpy.data.meshes.new('needles')"):src.index("P=D['panel']")])
bpy.ops.object.select_all(action='SELECT');bpy.context.view_layer.objects.active=objects[0];bpy.ops.object.join()
o=bpy.context.object;bpy.ops.object.transform_apply(location=True,rotation=True,scale=True)
lo=[min(v.co[k] for v in o.data.vertices) for k in range(3)];hi=[max(v.co[k] for v in o.data.vertices) for k in range(3)]
for v in o.data.vertices:v.co-=Vector(((hi[0]+lo[0])/2,(hi[1]+lo[1])/2,lo[2]))
bpy.ops.wm.save_as_mainfile(filepath=str(ROOT/'output/baseline_cluster.blend'))
bpy.ops.export_scene.gltf(filepath=str(ROOT/'output/baseline_cluster.glb'),export_format='GLB',use_selection=True)
