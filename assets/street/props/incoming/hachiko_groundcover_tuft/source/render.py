import bpy,sys
from pathlib import Path
from mathutils import Vector
r=Path(__file__).resolve().parents[1];bpy.ops.wm.open_mainfile(filepath=str(r/'output/groundcover.blend'))
s=bpy.context.scene;s.render.engine='CYCLES';s.cycles.samples=32;s.render.resolution_x=900;s.render.resolution_y=700;s.render.resolution_percentage=100
s.world=bpy.data.worlds.new('Neutral studio');s.world.color=(.3,.3,.3);s.view_settings.view_transform='AgX'
for pos,power,size in [((.6,-.8,1),35,.7),((-.5,-.2,.5),18,.6),((0,.8,.8),30,.6)]:
 bpy.ops.object.light_add(type='AREA',location=pos);o=bpy.context.object;o.data.energy=power;o.data.size=size;o.rotation_euler=(Vector((0,0,.08))-o.location).to_track_quat('-Z','Y').to_euler()
bpy.ops.object.camera_add();c=bpy.context.object;c.data.type='ORTHO';c.data.ortho_scale=.52;s.camera=c
for name,pos in [('front',(0,-1,.25)),('side',(1,0,.25)),('oblique',(.65,-1,.6)),('photo_angle',(0,-1,.32))]:
 c.location=pos;c.rotation_euler=(Vector((0,0,.085))-c.location).to_track_quat('-Z','Y').to_euler();s.render.filepath=str(r/'evidence'/f'{name}.png');bpy.ops.render.render(write_still=True)

# Neutral scale witnesses only: these are NOT existing scene meshes or placement evidence.
def mat(name,col):
 m=bpy.data.materials.new(name);m.diffuse_color=(*col,1);m.use_nodes=True;m.node_tree.nodes.get('Principled BSDF').inputs['Base Color'].default_value=(*col,1);m.node_tree.nodes.get('Principled BSDF').inputs['Roughness'].default_value=.95;return m
bpy.ops.mesh.primitive_cube_add(size=1,location=(0,-.19,-.09));o=bpy.context.object;o.name='SCALE_WITNESS_NOT_MAIN_stone';o.dimensions=(.64,.12,.28);o.data.materials.append(mat('Neutral stone',(.15,.16,.155)))
bpy.ops.mesh.primitive_ico_sphere_add(subdivisions=2,radius=.15,location=(.24,.08,.07));o=bpy.context.object;o.name='SCALE_WITNESS_NOT_MAIN_rock';o.scale=(1,.85,.75);o.data.materials.append(mat('Neutral rock',(.14,.12,.09)))
c.data.ortho_scale=.87;c.location=(.55,-1,.55);c.rotation_euler=(Vector((.04,0,.025))-c.location).to_track_quat('-Z','Y').to_euler();s.render.filepath=str(r/'evidence/context_scale_only.png');bpy.ops.render.render(write_still=True)
