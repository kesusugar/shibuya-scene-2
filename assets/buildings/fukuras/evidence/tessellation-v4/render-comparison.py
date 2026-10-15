import bpy,json,math
from pathlib import Path
from mathutils import Vector
A=Path(__file__).resolve().parents[2];E=A/'evidence/tessellation-v4'
bpy.ops.wm.read_factory_settings(use_empty=True);sc=bpy.context.scene;sc.render.engine='CYCLES';sc.cycles.samples=24;sc.cycles.use_denoising=True;sc.render.resolution_x=1600;sc.render.resolution_y=1000;sc.render.resolution_percentage=100;sc.render.image_settings.file_format='JPEG';sc.render.image_settings.quality=95;sc.view_settings.view_transform='AgX'
sc.world=bpy.data.worlds.new('Balanced studio');sc.world.use_nodes=True;sc.world.node_tree.nodes['Background'].inputs[0].default_value=(.55,.55,.55,1);sc.world.node_tree.nodes['Background'].inputs[1].default_value=.8
# Same orthographic direction/scale for both copies. Side-by-side translation only for comparison.
target=Vector((-25,-193,53));direction=Vector((1.3,2.5,1.35)).normalized();right=Vector((0,0,1)).cross(direction).normalized();gap=115
for phase,path,offset in [('MAIN',A/'source/tessellation-v4/main.glb',-gap/2),('DELIVERED',A/'web/fukuras.glb',gap/2)]:
 old=set(bpy.data.objects);bpy.ops.import_scene.gltf(filepath=str(path));new=set(bpy.data.objects)-old
 for ob in new:
  if ob.parent not in new:ob.location+=right*offset
bpy.ops.object.light_add(type='SUN');bpy.context.object.rotation_euler=(.4,-.3,-.4);bpy.context.object.data.energy=2
bpy.ops.object.camera_add(location=target+direction*300);cam=bpy.context.object;cam.rotation_euler=(-direction).to_track_quat('-Z','Y').to_euler();cam.data.type='ORTHO';cam.data.ortho_scale=245;sc.camera=cam
# Labels are native scene text facing the same camera, not edited pixels.
up=cam.rotation_euler.to_matrix()@Vector((0,1,0))
for label,offset in [('MAIN  954439cc',-gap/2),('DELIVERED  fa1010e8',gap/2)]:
 bpy.ops.object.text_add(location=target+right*offset+up*67+direction*90);ob=bpy.context.object;ob.rotation_euler=cam.rotation_euler;ob.data.body=label;ob.data.align_x='CENTER';ob.data.size=4;mat=bpy.data.materials.get('label') or bpy.data.materials.new('label');mat.diffuse_color=(.03,.03,.03,1);ob.data.materials.append(mat)
sc.render.filepath=str(E/'main-before-after.jpg');bpy.ops.render.render(write_still=True)
(E/'cameras.json').write_text(json.dumps({'type':'ORTHO','target':list(target),'direction':list(direction),'scale':245,'comparison_display_translation_only':[-gap/2,gap/2],'camera_right':list(right),'sun_euler':[.4,-.3,-.4],'sun_energy':2,'world_strength':.8,'resolution':[1600,1000],'samples':24,'color':'AgX','native_format':'JPEG','scope':'Actual pinned main versus exact delivered final. No camera calibration or whole-scene claim.'},indent=2)+'\n')
