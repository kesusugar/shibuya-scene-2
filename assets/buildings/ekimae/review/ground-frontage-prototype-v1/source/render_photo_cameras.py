import bpy,json,math
from pathlib import Path
from mathutils import Vector,Matrix
R=Path(__file__).resolve().parents[1];assert bpy.app.version==(4,2,3)
B=Vector((-46.78,-10.647,0));T=Vector((.9991711854627296,-.04070555417880273,0));N=Vector((.04070555417880273,.9991711854627296,0))
def xyz(v):return -T*v[0]+N*v[1]+Vector((0,0,v[2]))
bpy.ops.wm.read_factory_settings(use_empty=True);bpy.ops.import_scene.gltf(filepath=str(R/'web/ekimae.glb'));bpy.ops.import_scene.gltf(filepath=str(R/'input/signs-2025-11.glb'))
s=bpy.context.scene;s.render.engine='CYCLES';s.cycles.samples=16;s.cycles.use_denoising=True;s.world=bpy.data.worlds.new('World');s.world.color=(.65,.65,.65)
bpy.ops.object.light_add(type='SUN');bpy.context.object.data.energy=2;bpy.context.object.rotation_euler=(.35,-.5,-.2)
fits=json.loads((R/'evidence/photo-camera-fit.json').read_text())
for name,c in fits.items():
 cu,cd,ch,yaw,pitch,roll,fl=c['camera_local_u_d_h_yaw_pitch_roll_focal'];f=Vector((math.sin(yaw)*math.cos(pitch),-math.cos(yaw)*math.cos(pitch),math.sin(pitch)));r=Vector((math.cos(yaw),math.sin(yaw),0));down=r.cross(f);rr=math.cos(roll)*r+math.sin(roll)*down;dd=-math.sin(roll)*r+math.cos(roll)*down
 bpy.ops.object.camera_add(location=B+xyz((cu,cd,ch)));cam=bpy.context.object;cam.rotation_euler=Matrix([xyz(rr),-xyz(dd),-xyz(f)]).transposed().to_euler();cam.data.type='PERSP';cam.data.sensor_fit='HORIZONTAL';cam.data.sensor_width=36;cam.data.lens=fl*36/c['pixel_size'][0];s.camera=cam;s.render.resolution_x=c['pixel_size'][0];s.render.resolution_y=c['pixel_size'][1];s.render.resolution_percentage=100;s.render.filepath=str(R/'evidence'/f'conditional-camera-{name}.png');bpy.ops.render.render(write_still=True);bpy.data.objects.remove(cam,do_unlink=True)
