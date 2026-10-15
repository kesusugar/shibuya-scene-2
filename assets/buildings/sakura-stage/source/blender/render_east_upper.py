"""Exact Blender4.2.3 same-camera asset-local controls, not full scene QA."""
import bpy,sys,json
from pathlib import Path
from mathutils import Vector
assert bpy.app.version==(4,2,3),bpy.app.version_string
A=Path(__file__).resolve().parents[2];args=sys.argv[sys.argv.index('--')+1:];mode=args[0];out=Path(args[1]);out.mkdir(parents=True,exist_ok=True)
bpy.ops.wm.read_factory_settings(use_empty=True)
bpy.ops.import_scene.gltf(filepath=str(A/('source/data/accepted-north143.glb' if mode=='before' else 'web/sakura-stage.glb')))
sc=bpy.context.scene;sc.render.engine='BLENDER_WORKBENCH';sc.display.shading.light='STUDIO';sc.display.shading.color_type='MATERIAL';sc.display.shading.show_shadows=True;sc.display.shading.show_cavity=True;sc.display.shading.cavity_type='BOTH';sc.display.shading.background_type='WORLD';sc.world=bpy.data.worlds.new('Evidence studio');sc.world.color=(.14,.16,.19);sc.view_settings.view_transform='Standard';sc.render.resolution_x=1000;sc.render.resolution_y=1300;sc.render.resolution_percentage=100
bpy.ops.object.camera_add();cam=bpy.context.object;sc.camera=cam;cam.data.type='ORTHO';cam.data.ortho_scale=210
views={'north143':((-22,-30,94),(96.6575,-246.846,94)), 'east113':((390,-135,100),(145,-270,95))}
for name,(loc,target) in views.items():
 cam.location=loc;cam.rotation_euler=(Vector(target)-cam.location).to_track_quat('-Z','Y').to_euler();sc.render.filepath=str(out/(mode+'-'+name+'.png'));bpy.ops.render.render(write_still=True)
if mode=='after':
 bpy.ops.file.pack_all();bpy.ops.wm.save_as_mainfile(filepath=str(A/'source/blender/sakura-stage.blend'))
(out/(mode+'-render-settings.json')).write_text(json.dumps({'blender':bpy.app.version_string,'engine':sc.render.engine,'resolution':[1000,1300],'ortho_scale':210,'views':views,'purpose':'asset-local workbench geometry controls only'},indent=2)+'\n')
