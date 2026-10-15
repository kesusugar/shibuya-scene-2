import bpy,sys,json
from pathlib import Path
from mathutils import Vector
assert bpy.app.version==(4,2,3),bpy.app.version_string
root=Path(sys.argv[sys.argv.index('--')+1]).resolve()
for state in ['before','after']:
 bpy.ops.wm.read_factory_settings(use_empty=True)
 folder=root/('inputs/current' if state=='before' else 'web')
 for name in ['west-block.glb','signs-2025-01.glb']:
  old=set(bpy.data.objects);bpy.ops.import_scene.gltf(filepath=str(folder/name));coll=bpy.data.collections.new('Architecture' if name=='west-block.glb' else 'January_2025_sign_layer');bpy.context.scene.collection.children.link(coll)
  for ob in set(bpy.data.objects)-old:
   for c in list(ob.users_collection):c.objects.unlink(ob)
   coll.objects.link(ob)
 if state=='after':
  bpy.ops.file.pack_all();bpy.ops.wm.save_as_mainfile(filepath=str(root/'west-awning-support-repair.blend'))
 if '--save-only' in sys.argv:continue
 for m in bpy.data.materials:
  if m.use_nodes:
   p=m.node_tree.nodes.get('Principled BSDF')
   if p:p.inputs['Emission Strength'].default_value=0
 bpy.ops.object.camera_add(location=(-43,-15,12));cam=bpy.context.object;aim=Vector((-55.4,21.279+(-55.4+67.253)*3.501/31.213,3.3));cam.rotation_euler=(aim-cam.location).to_track_quat('-Z','Y').to_euler();cam.data.type='ORTHO';cam.data.ortho_scale=15;bpy.context.scene.camera=cam
 bpy.ops.object.light_add(type='SUN',location=(-90,-100,100));l=bpy.context.object;l.rotation_euler=(Vector((-50,26,0))-l.location).to_track_quat('-Z','Y').to_euler();l.data.energy=1.6
 s=bpy.context.scene;s.render.engine='CYCLES';s.cycles.samples=24;s.cycles.use_denoising=False;s.world=bpy.data.worlds.new('World');s.world.color=(.6,.6,.6);s.render.resolution_x=1400;s.render.resolution_y=650;s.render.resolution_percentage=100;s.render.image_settings.file_format='PNG';s.render.filepath=str(root/'evidence'/('awning-'+state+'.png'));bpy.ops.render.render(write_still=True)
(root/'evidence/render-settings.json').write_text(json.dumps(dict(blender=bpy.app.version_string,camera=[-43,-15,12],aim=[-55.4,22.60848941146317,3.3],ortho_scale=15,resolution=[1400,650],samples=24,denoise=False,scope='Actual before/after GLB imports, isolated building. Same camera/settings as inspection. Not full scene or photo calibrated.',render_override='Emission zero for render only; saved blend keeps original values.'),indent=2))
