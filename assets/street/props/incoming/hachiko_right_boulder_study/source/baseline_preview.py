import bpy,random
from pathlib import Path
from mathutils import Vector
OUT=Path(__file__).resolve().parents[1]
bpy.ops.object.select_all(action='SELECT');bpy.ops.object.delete(use_global=False)
# Representative original source algorithm, not exact merged main binary.
r=random.Random(73);bpy.ops.mesh.primitive_ico_sphere_add(subdivisions=2,radius=1);o=bpy.context.object;o.scale=(r.uniform(.30,.42),.24,r.uniform(.28,.38))
for v in o.data.vertices:v.co*=r.uniform(.86,1.12)
bpy.ops.object.transform_apply(location=False,rotation=False,scale=True)
zmin=min(v.co.z for v in o.data.vertices)
for v in o.data.vertices:v.co.z-=zmin
for p in o.data.polygons:p.use_smooth=True
m=bpy.data.materials.new('Source algorithm rock');m.use_nodes=True;bs=m.node_tree.nodes.get('Principled BSDF');bs.inputs['Base Color'].default_value=(.22,.19,.15,1);bs.inputs['Roughness'].default_value=.95;o.data.materials.append(m)
sc=bpy.context.scene;sc.render.engine='CYCLES';sc.cycles.samples=16;sc.render.resolution_x=720;sc.render.resolution_y=540;sc.render.resolution_percentage=100;sc.world.color=(.18,.18,.18);sc.view_settings.view_transform='AgX'
for loc,power,sz in [((-2,-3,4),450,3),((2,1,3),250,2)]:
 bpy.ops.object.light_add(type='AREA',location=loc);l=bpy.context.object;l.data.energy=power;l.data.shape='DISK';l.data.size=sz;l.rotation_euler=(Vector((0,0,.25))-l.location).to_track_quat('-Z','Y').to_euler()
bpy.ops.object.camera_add(location=(0,-3,.53));cam=bpy.context.object;sc.camera=cam;cam.data.type='ORTHO';cam.data.ortho_scale=1.13;cam.rotation_euler=(Vector((0,0,.28))-cam.location).to_track_quat('-Z','Y').to_euler();sc.render.filepath=str(OUT/'evidence'/'source_algorithm_baseline.png');bpy.ops.render.render(write_still=True)
