import bpy,sys,math
from pathlib import Path
from mathutils import Vector
args=sys.argv[sys.argv.index('--')+1:];root,out=args[:2];view=args[2] if len(args)>2 else 'front'
bpy.ops.wm.read_factory_settings(use_empty=True)
for f in ['ekimae.glb','signs-2025-11.glb']:bpy.ops.import_scene.gltf(filepath=str(Path(root)/'assets/buildings/ekimae/web'/f))
for m in bpy.data.materials:
 if m.use_nodes:
  p=m.node_tree.nodes.get('Principled BSDF')
  if p:p.inputs['Emission Strength'].default_value=0.15 if m.name.startswith('ek_sign_') else 0
scene=bpy.context.scene;scene.render.engine='CYCLES';scene.cycles.samples=48;scene.cycles.use_denoising=True
scene.world=bpy.data.worlds.new('World');scene.world.color=(.45,.45,.45)
bpy.ops.object.light_add(type='AREA', location=(-10,10,80));bpy.context.object.data.energy=50000;bpy.context.object.data.shape='DISK';bpy.context.object.data.size=70
bpy.ops.object.camera_add(location=(24,42,28) if view=='front' else (40,-20,29));cam=bpy.context.object;target=Vector((-44,-13,25.2));cam.rotation_euler=(target-cam.location).to_track_quat('-Z','Y').to_euler();cam.data.type='ORTHO';cam.data.ortho_scale=31;scene.camera=cam
scene.render.resolution_x=1400;scene.render.resolution_y=800;scene.render.resolution_percentage=100;scene.view_settings.view_transform='Standard';scene.render.image_settings.file_format='PNG';scene.render.filepath=out;bpy.ops.render.render(write_still=True)
