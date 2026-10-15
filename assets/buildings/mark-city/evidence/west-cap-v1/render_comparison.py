import bpy,json,sys,hashlib
from pathlib import Path
from mathutils import Vector
R=Path(__file__).resolve().parents[2];O=Path(sys.argv[sys.argv.index('--')+1]);O.mkdir(parents=True,exist_ok=True)
views={'west':((-305.448,-2.833,98),(-245.24,-172.465,98),134),'context':((-330,-35,100),(-180,-145,65),290)}
for label,path in [('main',R/'source/main-baseline-v1/mark-city.glb'),('revision',R/'web/mark-city.glb')]:
 bpy.ops.wm.read_factory_settings(use_empty=True);bpy.ops.import_scene.gltf(filepath=str(path));s=bpy.context.scene;s.render.engine='BLENDER_WORKBENCH';s.display.shading.light='STUDIO';s.display.shading.color_type='MATERIAL';s.display.shading.show_shadows=True;s.display.shading.show_cavity=True;s.display.shading.cavity_type='BOTH';s.display.shading.background_type='WORLD';s.world=bpy.data.worlds.new('World');s.world.color=(.16,.18,.2);s.view_settings.view_transform='Standard';bpy.ops.object.camera_add();c=bpy.context.object;s.camera=c
 for name,(loc,target,scale) in views.items():
  c.data.type='ORTHO';c.data.ortho_scale=scale;c.location=loc;c.rotation_euler=(Vector(target)-c.location).to_track_quat('-Z','Y').to_euler();s.render.resolution_x=1100;s.render.resolution_y=770;s.render.resolution_percentage=100;s.render.filepath=str(O/f'{name}-{label}.png');bpy.ops.render.render(write_still=True)
