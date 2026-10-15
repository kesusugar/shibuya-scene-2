"""Optional local-only context check. Existing pavilion is not redistributed."""
import bpy,sys,math
from pathlib import Path
from mathutils import Vector
args=sys.argv[sys.argv.index('--')+1:];fixture,pavilion,dest=map(lambda x:Path(x).resolve(),args)
bpy.ops.object.select_all(action='SELECT');bpy.ops.object.delete(use_global=False)
bpy.ops.import_scene.gltf(filepath=str(pavilion))
# Temporarily show the old pavilion materials more transparently for inspection only.
for m in bpy.data.materials:
 if m.use_nodes:
  p=m.node_tree.nodes.get('Principled BSDF')
  if p and p.inputs['Alpha'].default_value < 1:p.inputs['Alpha'].default_value=.10
for y in [.05,1.05]:
 bpy.ops.import_scene.gltf(filepath=str(fixture));o=bpy.context.selected_objects[0];o.rotation_euler[2]=-math.pi/2;o.location=(-5.94,y,2.30)
s=bpy.context.scene;s.render.engine='CYCLES';s.cycles.samples=32;s.render.resolution_x=1100;s.render.resolution_y=850;s.render.resolution_percentage=100;s.world.color=(.35,.35,.35)
for loc,pow,size in [((-8,-4,6),1200,5),((-8,4,5),900,4)]:
 bpy.ops.object.light_add(type='AREA',location=loc);o=bpy.context.object;o.data.energy=pow;o.data.size=size;o.rotation_euler=(Vector((-6,.5,1.4))-o.location).to_track_quat('-Z','Y').to_euler()
bpy.ops.object.camera_add(location=(-10,-1.4,1.8));c=bpy.context.object;c.rotation_euler=(Vector((-6,.65,1.7))-c.location).to_track_quat('-Z','Y').to_euler();c.data.type='ORTHO';c.data.ortho_scale=3.1;s.camera=c;s.render.filepath=str(dest);bpy.ops.render.render(write_still=True)
