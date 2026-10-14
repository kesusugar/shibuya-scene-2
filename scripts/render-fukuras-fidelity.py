import bpy,sys,math,json
from mathutils import Vector
from pathlib import Path
repo=Path(__file__).resolve().parents[1];base=repo/'evidence/fukuras-fidelity';base.mkdir(parents=True,exist_ok=True);asset=repo/'assets/buildings/fukuras'
for phase,path in [('before',asset/'source/data/baseline.glb'),('after',asset/'web/fukuras.glb')]:
 bpy.ops.wm.read_factory_settings(use_empty=True);bpy.ops.import_scene.gltf(filepath=str(path));scene=bpy.context.scene;scene.render.engine='CYCLES';scene.cycles.samples=24;scene.cycles.use_denoising=True;scene.render.resolution_x=900;scene.render.resolution_y=900;scene.render.resolution_percentage=100
 scene.world=bpy.data.worlds.new('Studio');scene.world.color=(.25,.25,.25);scene.view_settings.view_transform='AgX'
 for loc,power,size in [((0,40,180),4500,100),((140,-100,110),2800,90)]:
  bpy.ops.object.light_add(type='AREA',location=loc);o=bpy.context.object;o.data.energy=power;o.data.shape='DISK';o.data.size=size;o.rotation_euler=(Vector((-25,-200,45))-o.location).to_track_quat('-Z','Y').to_euler()
 bpy.ops.object.light_add(type='SUN',location=(0,0,100));bpy.context.object.rotation_euler=(.4,-.3,-.4);bpy.context.object.data.energy=2
 bpy.ops.object.camera_add();cam=bpy.context.object;scene.camera=cam
 # Blender imported glTF returns original XY plan/Z up.
 cams={'corner_close':((0,-144,38),(-13.7,-168.7,38),16),'front':((-110,15,85),(-25,-193,52),135),'side':((170,-100,80),(-22,-198,52),135),'photo_oct11':((80,-65,20),(-25,-190,50),120),'photo_oct18':((20,60,8),(-25,-190,51),135)}
 for name,(loc,target,scale) in cams.items():
  cam.location=loc;cam.rotation_euler=(Vector(target)-cam.location).to_track_quat('-Z','Y').to_euler();cam.data.type='ORTHO' if name in ['front','side','corner_close'] else 'PERSP';cam.data.ortho_scale=scale;cam.data.lens=65 if name=='photo_oct18' else 48
  scene.render.filepath=str(base/f'{name}-{phase}.png');bpy.ops.render.render(write_still=True)
(base/'cameras.json').write_text(json.dumps(cams,indent=2))
