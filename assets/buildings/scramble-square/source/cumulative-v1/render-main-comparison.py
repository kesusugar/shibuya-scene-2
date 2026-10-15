import bpy,json
from pathlib import Path
from mathutils import Vector
A=Path(__file__).resolve().parents[2];E=A/'evidence/cumulative-v1';c=json.loads((E/'cameras.json').read_text())['views']
for label,p in [('before',A/'source/cumulative-v1/main.glb'),('after',A/'web/scramble-square.glb')]:
 bpy.ops.wm.read_factory_settings(use_empty=True);bpy.ops.import_scene.gltf(filepath=str(p));s=bpy.context.scene;s.render.engine='BLENDER_WORKBENCH';s.display.shading.light='STUDIO';s.display.shading.studio_light='paint.sl';s.display.shading.color_type='MATERIAL';s.display.shading.show_shadows=True;s.display.shading.show_cavity=True;s.display.shading.cavity_type='BOTH';s.display.shading.background_type='WORLD';s.world=bpy.data.worlds.new('World');s.world.color=(.8,.8,.8);s.render.resolution_x=850;s.render.resolution_y=850;s.render.resolution_percentage=100;s.render.image_settings.file_format='PNG';s.view_settings.view_transform='Standard'
 for name,v in c.items():
  cam=bpy.data.cameras.new(name);ob=bpy.data.objects.new(name,cam);s.collection.objects.link(ob);s.camera=ob;ob.location=v['location'];ob.rotation_euler=(Vector(v['target'])-ob.location).to_track_quat('-Z','Y').to_euler();cam.type='ORTHO';cam.ortho_scale=v['scale'];cam.clip_end=5000;s.render.filepath=str(E/(name+'-'+label+'.png'));bpy.ops.render.render(write_still=True)
