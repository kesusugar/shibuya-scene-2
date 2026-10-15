"""Independent GLB-loaded model render, no source photos/textures."""
import bpy,sys,math
from pathlib import Path
from mathutils import Vector
arg=sys.argv[sys.argv.index('--')+1:];bpy.ops.object.select_all(action='SELECT');bpy.ops.object.delete(use_global=False)
bpy.ops.import_scene.gltf(filepath=str(Path(arg[0]).resolve()));s=bpy.context.scene
s.render.engine='CYCLES';s.cycles.samples=24;s.cycles.use_denoising=True;s.render.resolution_x=1600;s.render.resolution_y=900;s.render.resolution_percentage=100;s.render.image_settings.file_format='PNG';s.world.color=(.3,.3,.3);s.view_settings.view_transform='AgX'
m=bpy.data.materials.new('Studio');m.diffuse_color=(.28,.31,.34,1);m.use_nodes=True;n=m.node_tree.nodes.get('Principled BSDF');n.inputs['Base Color'].default_value=(.28,.31,.34,1);n.inputs['Roughness'].default_value=.85
bpy.ops.mesh.primitive_cube_add(size=1,location=(0,0,-.065));o=bpy.context.object;o.dimensions=(200,200,.1);o.data.materials.append(m);o.name='StudioFloor'
for loc,power,size in [((0,-7,10),2500,9),((-8,1,7),1700,7),((7,4,8),2200,7)]:
 bpy.ops.object.light_add(type='AREA',location=loc);o=bpy.context.object;o.data.energy=power;o.data.shape='DISK';o.data.size=size;o.rotation_euler=(Vector((0,0,1))-o.location).to_track_quat('-Z','Y').to_euler()
side=len(arg)>2 and arg[2]=='side'
bpy.data.objects['StudioFloor'].hide_render=side
bpy.ops.object.camera_add(location=(-22,0,1.3) if side else (-12,-15,3.8));c=bpy.context.object;c.rotation_euler=(Vector((0,0,1.3))-c.location).to_track_quat('-Z','Y').to_euler();c.data.type='ORTHO' if side else 'PERSP';c.data.lens=42;c.data.clip_end=1000;c.data.ortho_scale=8 if side else 16;s.camera=c;s.render.filepath=str(Path(arg[1]).resolve());bpy.ops.render.render(write_still=True)
