"""Blender 4.2.3: render actual exported GLB, three orthographic inspection views."""
import bpy,sys
from pathlib import Path
from mathutils import Vector
ROOT=Path(sys.argv[sys.argv.index('--')+1]).resolve()
bpy.ops.wm.read_factory_settings(use_empty=True);bpy.ops.import_scene.gltf(filepath=str(ROOT/'hachiko_dual_rail_module.glb'))
s=bpy.context.scene;s.render.engine='CYCLES';s.cycles.samples=16;s.cycles.use_denoising=True
s.world=bpy.data.worlds.new('Inspection studio');s.world.use_nodes=True;s.world.node_tree.nodes['Background'].inputs['Color'].default_value=(.22,.22,.22,1)
for loc,power,size in [((0,2,4),450,3),((3,-2,3),350,3),((-3,1,2),230,2)]:
 bpy.ops.object.light_add(type='AREA',location=loc);o=bpy.context.object;o.data.energy=power;o.data.size=size;o.rotation_euler=(Vector((0,0,.25))-o.location).to_track_quat('-Z','Y').to_euler()
bpy.ops.object.camera_add();c=bpy.context.object;c.data.type='ORTHO';s.camera=c
s.render.resolution_x=1200;s.render.resolution_y=650;s.render.resolution_percentage=100;s.render.image_settings.file_format='PNG';s.view_settings.view_transform='AgX';s.view_settings.look='AgX - Medium High Contrast'
(ROOT/'evidence').mkdir(exist_ok=True)
for name,loc,scale in [('front',(0,4,.4225),2.8),('side',(4,0,.4225),1.9),('oblique',(2.7,4,1.8),2.8)]:
 c.location=loc;c.rotation_euler=(Vector((0,0,.4225))-c.location).to_track_quat('-Z','Y').to_euler();c.data.ortho_scale=scale;s.render.filepath=str(ROOT/'evidence'/f'{name}.png');bpy.ops.render.render(write_still=True)
