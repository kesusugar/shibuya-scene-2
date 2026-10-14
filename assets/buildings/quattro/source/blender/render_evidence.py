import bpy,sys,math
from pathlib import Path
from mathutils import Vector
asset,out,view=sys.argv[sys.argv.index('--')+1:]
era=view.endswith('-january')
if era:view=view.replace('-january','')
bpy.ops.wm.read_factory_settings(use_empty=True);bpy.ops.import_scene.gltf(filepath=asset)
if era:bpy.ops.import_scene.gltf(filepath=str(Path(asset).with_name('signs-2025-01.glb')))
aim=Vector((-44.6,64,15.7))
if view=='front':d=Vector((-.695,-.718,.12));scale=34;res=(1000,1150)
elif view=='side':d=Vector((.85,-.52,.24));scale=35;res=(850,1150)
else:d=Vector((.521,-.847,.104));scale=35;res=(850,1200)
bpy.ops.object.camera_add(location=aim+d*100);c=bpy.context.object;c.rotation_euler=(aim-c.location).to_track_quat('-Z','Y').to_euler();c.data.type='ORTHO';c.data.ortho_scale=scale;bpy.context.scene.camera=c
bpy.ops.object.light_add(type='SUN',location=(-80,-70,100));l=bpy.context.object;l.rotation_euler=(aim-l.location).to_track_quat('-Z','Y').to_euler();l.data.energy=2;l.data.angle=.10
s=bpy.context.scene;s.render.engine='CYCLES';s.cycles.samples=32;s.cycles.use_denoising=True;s.world=bpy.data.worlds.new('World');s.world.color=(.6,.6,.6);s.render.resolution_x,s.render.resolution_y=res;s.render.resolution_percentage=100;s.view_settings.view_transform='AgX';s.view_settings.look='AgX - Medium High Contrast';s.render.image_settings.file_format='PNG';s.render.filepath=out;s.render.film_transparent=False
bpy.ops.render.render(write_still=True)
