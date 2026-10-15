import bpy,sys,json
from pathlib import Path
from mathutils import Vector
A=Path(__file__).resolve().parents[2];out=Path(sys.argv[sys.argv.index('--')+1]) if '--' in sys.argv else A/'review/main-vs-final';out.mkdir(parents=True,exist_ok=True)
assert bpy.app.version==(4,2,3)
views={'north143':((-22,-30,94),(96.6575,-246.846,94)), 'east113':((390,-135,100),(145,-270,95))}
for label,fp in [('main',A/'source/data/baseline.glb'),('final',A/'web/sakura-stage.glb')]:
 bpy.ops.wm.read_factory_settings(use_empty=True);bpy.ops.import_scene.gltf(filepath=str(fp));sc=bpy.context.scene;sc.render.engine='BLENDER_WORKBENCH';s=sc.display.shading;s.light='STUDIO';s.studiolight_rotate_z=.5;s.color_type='MATERIAL';s.show_shadows=True;s.show_cavity=True;s.cavity_type='BOTH';s.background_type='WORLD';sc.world=bpy.data.worlds.new('Evidence studio');sc.world.color=(.20,.22,.25);sc.view_settings.view_transform='Standard';sc.render.resolution_x=1000;sc.render.resolution_y=1300;sc.render.resolution_percentage=100;sc.render.image_settings.file_format='JPEG';sc.render.image_settings.quality=95
 bpy.ops.object.camera_add();cam=bpy.context.object;sc.camera=cam;cam.data.type='ORTHO';cam.data.ortho_scale=210
 for name,(loc,target) in views.items():
  cam.location=loc;cam.rotation_euler=(Vector(target)-cam.location).to_track_quat('-Z','Y').to_euler();sc.render.filepath=str(out/(label+'-'+name+'.jpg'));bpy.ops.render.render(write_still=True)
(out/'settings.json').write_text(json.dumps({'blender':bpy.app.version_string,'engine':'BLENDER_WORKBENCH','resolution':[1000,1300],'ortho_scale':210,'views':views,'world_color':[.20,.22,.25],'studio_rotate_z':.5,'purpose':'same-camera actual-main/final asset-local geometry only; no full-scene or FPS validation'},indent=2)+'\n')
