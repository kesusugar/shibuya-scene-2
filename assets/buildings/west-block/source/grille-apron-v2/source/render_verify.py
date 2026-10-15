import bpy,sys,json
from pathlib import Path
from mathutils import Vector
assert bpy.app.version==(4,2,3),bpy.app.version_string
root=Path(sys.argv[sys.argv.index('--')+1]).resolve()
bpy.ops.wm.read_factory_settings(use_empty=True)
for name in ['west-block.glb','signs-2025-01.glb']:
 before=set(bpy.data.objects);bpy.ops.import_scene.gltf(filepath=str(root/'web'/name));collection=bpy.data.collections.new('Architecture' if name=='west-block.glb' else 'January_2025_sign_layer');bpy.context.scene.collection.children.link(collection)
 for ob in set(bpy.data.objects)-before:
  for c in list(ob.users_collection):c.objects.unlink(ob)
  collection.objects.link(ob)
bpy.ops.file.pack_all()
bpy.ops.wm.save_as_mainfile(filepath=str(root/'west-frontage-grille.blend'))
if '--save-only' in sys.argv: sys.exit(0)
# Render-only override matches the review's non-emissive daylight evidence.
for m in bpy.data.materials:
 if m.use_nodes:
  p=m.node_tree.nodes.get('Principled BSDF')
  if p:p.inputs['Emission Strength'].default_value=0
bpy.ops.object.camera_add();c=bpy.context.object;c.data.type='ORTHO';bpy.context.scene.camera=c
bpy.ops.object.light_add(type='SUN',location=(-90,-100,100));l=bpy.context.object;l.rotation_euler=(Vector((-50,26,0))-l.location).to_track_quat('-Z','Y').to_euler();l.data.energy=1.6;l.data.angle=.05
s=bpy.context.scene;s.render.engine='CYCLES';s.cycles.samples=16;s.cycles.use_denoising=True;s.world=bpy.data.worlds.new('World');s.world.color=(.60,.60,.60);s.render.resolution_x=1200;s.render.resolution_y=1000;s.render.resolution_percentage=100;s.view_settings.view_transform='AgX';s.view_settings.look='AgX - Medium High Contrast';s.render.image_settings.file_format='PNG';s.render.film_transparent=False
views=[('context',(-42,-30,17),(-49,23.3,4),8),('detail',(-47,-8,9),(-49,23.3,4.3),4.5),('front',(-45.432,-8.48,4.3),(-49,23.326344151,4.3),4.5)]
grille=[o for o in bpy.data.objects if o.type=='MESH' and o.name.startswith('west_six_cell_grille_apron')];assert len(grille)==1
for name,loc,aim,scale in views:
 c.location=loc;c.rotation_euler=(Vector(aim)-c.location).to_track_quat('-Z','Y').to_euler();c.data.ortho_scale=scale
 for state in ['before','after']:
  for o in grille:o.hide_render=state=='before'
  s.render.filepath=str(root/'evidence'/(name+'-'+state+'.png'));bpy.ops.render.render(write_still=True)
(root/'evidence/render-settings.json').write_text(json.dumps({'blender':bpy.app.version_string,'views':views,'samples':16,'resolution':[1200,1000],'scope':'Isolated building and January signs; not full scene or photo-calibrated. Before hides only appended object.','render_override':'Emission strength zero for evidence only; saved editable blend keeps original materials.'},indent=2))
