import bpy, sys, math
from pathlib import Path
from mathutils import Vector
root=Path(__file__).resolve().parents[1];baseline='--baseline' in sys.argv;bpy.ops.wm.open_mainfile(filepath=str(root/'output'/('baseline_cluster.blend' if baseline else 'low_shrub.blend')))
glb='--glb' in sys.argv
if glb:
 bpy.ops.wm.read_factory_settings(use_empty=True);bpy.ops.import_scene.gltf(filepath=str(root/'output/low_shrub.glb'))
s=bpy.context.scene;s.render.engine='CYCLES';s.cycles.samples=32;s.cycles.transparent_max_bounces=64;s.render.resolution_x=900;s.render.resolution_y=1000;s.render.resolution_percentage=100
s.world=bpy.data.worlds.new('Studio');s.world.color=(.28,.28,.28);s.view_settings.view_transform='AgX'
for p,power,size in [((3,-4,5),650,4),((-3,-1,2),350,3),((0,3,4),800,3)]:
 bpy.ops.object.light_add(type='AREA',location=p);o=bpy.context.object;o.data.energy=power;o.data.shape='DISK';o.data.size=size;o.rotation_euler=(Vector((0,0,.5))-o.location).to_track_quat('-Z','Y').to_euler()
bpy.ops.object.camera_add();c=bpy.context.object;c.data.type='ORTHO';c.data.ortho_scale=1.5;s.camera=c
s.render.image_settings.file_format='PNG'
for name,pos in [('front',(0,-4,1.05)),('oblique',(2.1,-3.5,1.8)),('side',(4,0,1.05))]:
 c.location=pos;c.rotation_euler=(Vector((0,0,.56))-c.location).to_track_quat('-Z','Y').to_euler();s.render.filepath=str(root/'evidence'/f'{"baseline_" if baseline else "glb_" if glb else ""}{name}.png');bpy.ops.render.render(write_still=True)
