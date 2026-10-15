"""Actual GLB renders and editable asset, exact Blender 4.2.3. No GLB re-export."""
import bpy,json,sys,hashlib
from pathlib import Path
from mathutils import Vector
assert bpy.app.version==(4,2,3)
ROOT=Path(__file__).resolve().parent.parent
cameras={'front':{'aim':(-44,-15,2.1),'direction':(.76,.65,-.02),'scale':24},'side':{'aim':(-51,-10,1.8),'direction':(.08,1,.05),'scale':11}}
(ROOT/'evidence/cameras.json').write_text(json.dumps(cameras,indent=2)+'\n')
for stage,path in [('before',ROOT/'input/ekimae.glb'),('after',ROOT/'web/ekimae.glb')]:
 if '--blend-only' in sys.argv and stage=='before':continue
 bpy.ops.wm.read_factory_settings(use_empty=True);bpy.ops.import_scene.gltf(filepath=str(path))
 assets=list(bpy.context.scene.objects)
 for ob in assets:ob['source_glb']=path.name;ob['repair_scope']='north-return doorway shell and handles only; no photogrammetric claim'
 if stage=='after':
  # Save the actual imported asset without camera/light or staging geometry.
  bpy.context.scene.unit_settings.system='METRIC';bpy.context.scene.unit_settings.scale_length=1
  bpy.context.scene['generator_version']='Blender 4.2.3';bpy.context.scene['source_glb_sha256']=hashlib.sha256(path.read_bytes()).hexdigest()
  bpy.ops.wm.save_as_mainfile(filepath=str(ROOT/'source/ekimae-door-envelope.blend'),compress=True)
 if '--blend-only' in sys.argv:continue
 s=bpy.context.scene;s.render.engine='CYCLES';s.cycles.samples=24;s.world=bpy.data.worlds.new('World');s.world.color=(.65,.65,.65)
 s.render.resolution_x=1200;s.render.resolution_y=600;s.render.resolution_percentage=100
 bpy.ops.object.light_add(type='SUN',location=(-40,-100,100));bpy.context.object.data.energy=2
 for name,c in cameras.items():
  aim=Vector(c['aim']);d=Vector(c['direction']).normalized();bpy.ops.object.camera_add(location=aim+d*120);cam=bpy.context.object;cam.rotation_euler=(aim-cam.location).to_track_quat('-Z','Y').to_euler();cam.data.type='ORTHO';cam.data.ortho_scale=c['scale'];s.camera=cam;s.render.filepath=str(ROOT/'evidence'/f'{stage}-{name}.png');bpy.ops.render.render(write_still=True);bpy.data.objects.remove(cam,do_unlink=True)
