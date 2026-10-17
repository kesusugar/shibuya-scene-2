import bpy,math,json,sys
from pathlib import Path
from mathutils import Vector
R=Path(__file__).resolve().parents[1]
def p(x,y,z):
 a=math.radians(35);return Vector((11.568175521259887+x*math.cos(a)-y*math.sin(a),-48.68573220011713+x*math.sin(a)+y*math.cos(a),z))
files=[('after','hachiko_surround_v002.blend')]
for label,file in files:
 bpy.ops.wm.open_mainfile(filepath=str(R/'models'/file))
 scene=bpy.context.scene
 scene.render.engine='CYCLES';scene.cycles.device='CPU';scene.cycles.transparent_max_bounces=64;scene.cycles.samples=24;scene.cycles.use_denoising=True
 scene.render.resolution_x=1400;scene.render.resolution_y=1000;scene.render.resolution_percentage=100
 scene.render.image_settings.file_format='PNG';scene.render.film_transparent=False
 scene.world=bpy.data.worlds.new('Preview World');scene.world.color=(.15,.15,.15);scene.view_settings.view_transform='AgX'
 scene.world.use_nodes=True;scene.world.node_tree.nodes['Background'].inputs[0].default_value=(.63,.70,.80,1);scene.world.node_tree.nodes['Background'].inputs[1].default_value=.65
 bpy.ops.mesh.primitive_plane_add(size=200,location=p(0,0,.40));floor=bpy.context.object;floor.name='PREVIEW_ONLY_neutral_ground'
 m=bpy.data.materials.new('PREVIEW_ONLY_neutral_ground');m.diffuse_color=(.22,.23,.23,1);floor.data.materials.append(m)
 bpy.ops.object.light_add(type='AREA',location=p(-3,3,8));bpy.context.object.data.energy=1050;bpy.context.object.data.shape='DISK';bpy.context.object.data.size=6
 bpy.context.object.rotation_euler=(p(0,-1.4,1)-bpy.context.object.location).to_track_quat('-Z','Y').to_euler()
 bpy.ops.object.camera_add();camera=bpy.context.object;scene.camera=camera;camera.data.type='ORTHO'
 cameras={'close':((-1.925,2.2,2.5),(-1.925,-1.45,1.45),2.55),'context':((3.9,7,4.6),(0,-1.4,1.3),7.25),'detail':((-2.15,.2,2.25),(-2.3,-1.45,1.6),1.25),'back':((-1.7,-4.5,2.6),(-1.925,-1.45,1.5),2.55)}
 for name,(pos,target,scale) in {'context':cameras['context']}.items():
  camera.location=p(*pos);camera.rotation_euler=(p(*target)-camera.location).to_track_quat('-Z','Y').to_euler();camera.data.ortho_scale=scale
  scene.render.filepath=str(R/'evidence'/f'{label}_{name}.png');bpy.ops.render.render(write_still=True)
 (R/'evidence'/f'{label}_camera.json').write_text(json.dumps({'coordinate_system':'Blender Z up, scene-local axes rotated +35 degrees to world XY','views':{k:cameras[k] for k in ['close','context']},'render_engine':'Cycles CPU','samples':24,'lighting':'neutral preview, identical both variants','ground':'preview-only plane, not exported'},indent=2))
print('Finished matched-camera before/after renders')
