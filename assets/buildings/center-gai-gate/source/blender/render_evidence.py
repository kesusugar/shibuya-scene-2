import bpy,sys,json,math
from pathlib import Path
from mathutils import Vector
root=Path(sys.argv[sys.argv.index('--')+1]); mode=sys.argv[-1]
bpy.ops.wm.read_factory_settings(use_empty=True)
p=root/('baseline' if mode=='before' else 'assets/buildings/center-gai-gate/web')
bpy.ops.import_scene.gltf(filepath=str(p/'center-gai-gate.glb'));bpy.ops.import_scene.gltf(filepath=str(p/'signs-2025-01.glb'))
scene=bpy.context.scene;scene.render.engine='CYCLES';scene.cycles.samples=32
scene.render.resolution_x=1100;scene.render.resolution_y=850;scene.render.resolution_percentage=100
scene.world=bpy.data.worlds.new('World');scene.world.color=(.45,.45,.45);scene.view_settings.view_transform='Standard'
mid=Vector((-27.1,35.5,3.3));T=Vector((8.2,-1,0)).normalized();N=Vector((T.y,-T.x,0))
bpy.ops.object.light_add(type='AREA',location=mid+N*8+Vector((-4,-2,10)));bpy.context.object.data.energy=2200;bpy.context.object.data.shape='DISK';bpy.context.object.data.size=9
bpy.context.object.rotation_euler=(mid-bpy.context.object.location).to_track_quat('-Z','Y').to_euler()
bpy.ops.mesh.primitive_plane_add(size=200, location=(mid.x,mid.y,.23));ob=bpy.context.object;mat=bpy.data.materials.new('display_only_ground');mat.diffuse_color=(.17,.19,.20,1);ob.data.materials.append(mat)
out=root/'evidence/center-gai-fidelity';out.mkdir(parents=True,exist_ok=True)
for name,offset in [('front',N*16+Vector((0,0,1))),('side',N*10+T*11+Vector((0,0,2))),('walk',N*12+T*2+Vector((0,0,-1.6)))]:
    bpy.ops.object.camera_add(location=mid+offset);cam=bpy.context.object;cam.rotation_euler=(mid-cam.location).to_track_quat('-Z','Y').to_euler();cam.data.type='ORTHO';cam.data.ortho_scale=11.5;scene.camera=cam
    scene.render.filepath=str(out/f'{mode}-{name}.png');bpy.ops.render.render(write_still=True);bpy.data.objects.remove(cam,do_unlink=True)
