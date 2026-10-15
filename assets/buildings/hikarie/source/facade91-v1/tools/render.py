import bpy,json,sys
from pathlib import Path
from mathutils import Vector
R=Path(__file__).resolve().parents[1]
cams=json.loads((R/'source/cameras.json').read_text())
selected=sys.argv[sys.argv.index('--')+1:] if '--' in sys.argv else []
for label,fn in [('before','baseline/hikarie.glb'),('after','web/hikarie.glb')]:
 bpy.ops.wm.read_factory_settings(use_empty=True);bpy.ops.import_scene.gltf(filepath=str(R/fn));s=bpy.context.scene;s.render.resolution_x=1000;s.render.resolution_y=1200;s.render.resolution_percentage=100;s.render.engine='CYCLES';s.cycles.samples=16;s.cycles.use_denoising=True;s.world=bpy.data.worlds.new('Studio');s.world.color=(.35,.35,.35);s.view_settings.view_transform='AgX'
 bpy.ops.object.light_add(type='SUN');bpy.context.object.rotation_euler=(.4,-.5,-.6);bpy.context.object.data.energy=2.5
 bpy.ops.object.camera_add();cam=bpy.context.object;s.camera=cam
 for name,c in cams.items():
  if selected and name not in selected:continue
  cam.location=c['location'];cam.rotation_euler=(Vector(c['target'])-cam.location).to_track_quat('-Z','Y').to_euler();cam.data.type=c['type'];cam.data.ortho_scale=c.get('scale',215);cam.data.lens=c.get('lens',39);s.render.filepath=str(R/'evidence'/f'{name}-{label}.png');bpy.ops.render.render(write_still=True)
