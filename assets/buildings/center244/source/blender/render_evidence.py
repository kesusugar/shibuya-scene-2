import bpy,sys,math
from pathlib import Path
from mathutils import Vector
root,out,view=sys.argv[sys.argv.index('--')+1:]
bpy.ops.wm.read_factory_settings(use_empty=True)
for name in ['center244.glb','signs-2025-01.glb']:
 if (Path(root)/name).exists():bpy.ops.import_scene.gltf(filepath=str(Path(root)/name))
for m in bpy.data.materials:
 if m.use_nodes:
  p=m.node_tree.nodes.get('Principled BSDF')
  if p:p.inputs['Emission Strength'].default_value=0
import json
vf=json.loads((Path(__file__).resolve().parents[1]/'data/view_fit.json').read_text())['parameters']
az,el,roll,scale,tx,ty=vf
D=Vector((math.sin(az)*math.cos(el),-math.cos(az)*math.cos(el),math.sin(el)))
right=Vector((math.cos(az),math.sin(az),0));up=D.cross(right)
rr=right*math.cos(roll)+up*math.sin(roll);uu=-right*math.sin(roll)+up*math.cos(roll)
if view=='full':crop=(1500,600,2250,1970);factor=.8
else:crop=(1740,1180,2110,1800);factor=1.4
cx,cy=(crop[0]+crop[2])/2,(crop[1]+crop[3])/2
# Match the source-photo crop under the explicitly approximate orthographic fit.
aim=rr*((cx-tx)/scale)+uu*((ty-cy)/scale)
loc=aim+D*180
bpy.ops.object.camera_add(location=loc);c=bpy.context.object;c.rotation_euler=(aim-c.location).to_track_quat('-Z','Y').to_euler();c.rotation_euler.rotate_axis('Z',roll);c.data.type='ORTHO';c.data.ortho_scale=(crop[3]-crop[1])/scale;bpy.context.scene.camera=c
res=(round((crop[2]-crop[0])*factor),round((crop[3]-crop[1])*factor))
if view in ['front','side']:
 aim=Vector((-68.5,76,18));c.location=aim+Vector((.47,-.88,0))*100 if view=='front' else aim+Vector((.89,-.45,0))*100;c.rotation_euler=(aim-c.location).to_track_quat('-Z','Y').to_euler();c.data.ortho_scale=38;res=(850,1200)
bpy.ops.object.light_add(type='SUN',location=(-90,-100,100));l=bpy.context.object;l.rotation_euler=(Vector((-50,26,0))-l.location).to_track_quat('-Z','Y').to_euler();l.data.energy=1.6;l.data.angle=.05
s=bpy.context.scene;s.render.engine='CYCLES';s.cycles.samples=24;s.cycles.use_denoising=True;s.world=bpy.data.worlds.new('World');s.world.color=(.60,.60,.60);s.render.resolution_x,s.render.resolution_y=res;s.render.resolution_percentage=100;s.view_settings.view_transform='AgX';s.view_settings.look='AgX - Medium High Contrast';s.render.image_settings.file_format='PNG';s.render.filepath=out;s.render.film_transparent=False
bpy.ops.render.render(write_still=True)
