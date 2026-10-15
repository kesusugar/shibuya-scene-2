"""Blender 4.2.3: visible upper decorative railing panel, not a complete fence."""
import bpy, math, json, hashlib, sys
from pathlib import Path
from mathutils import Vector
ROOT=Path(__file__).resolve().parent
assert bpy.app.version[:3]==(4,2,3), 'Use Blender 4.2.3'
bpy.ops.object.select_all(action='SELECT'); bpy.ops.object.delete(use_global=False)
scene=bpy.context.scene
scene.unit_settings.system='METRIC'; scene.unit_settings.scale_length=1.0
asset=bpy.data.collections.new('ASSET'); scene.collection.children.link(asset)
studio=bpy.data.collections.new('STUDIO_RENDER_ONLY'); scene.collection.children.link(studio)
def move(o,c):
 for old in list(o.users_collection): old.objects.unlink(o)
 c.objects.link(o)
def mat(name,color,metal,rough):
 m=bpy.data.materials.new(name); m.diffuse_color=(*color,1); m.use_nodes=True
 bs=m.node_tree.nodes.get('Principled BSDF');bs.inputs['Base Color'].default_value=(*color,1);bs.inputs['Metallic'].default_value=metal;bs.inputs['Roughness'].default_value=rough
 return m
paint=mat('prop_furniture_0',(0.025,0.205,0.145),.22,.4)
def tube(name,coords,radius,curved):
 c=bpy.data.curves.new(name,'CURVE');c.dimensions='3D';c.resolution_u=12;c.bevel_depth=radius;c.bevel_resolution=3;c.use_fill_caps=True
 s=c.splines.new('BEZIER' if curved else 'POLY')
 pts=s.bezier_points if curved else s.points;pts.add(len(coords)-1)
 for p,co in zip(pts,coords):
  if curved: p.co=co;p.handle_left_type='AUTO';p.handle_right_type='AUTO'
  else:p.co=(*co,1)
 o=bpy.data.objects.new(name,c);asset.objects.link(o);o.data.materials.append(paint)
 return o
# Absolute dimensions are project assumptions. Only the upper photographed motif is reconstructed.
tube('top_rail',[(-1,0,.47),(1,0,.47)],.022,False)
tube('middle_rail',[(-1,0,.018),(1,0,.018)],.018,False)
pts=[(-.94,0,.018),(-.81,0,.18),(-.64,0,.31),(-.43,0,.39),(-.22,0,.415),(-.12,0,.39),(-.09,0,.29),(0,0,.265),(.09,0,.29),(.12,0,.39),(.22,0,.415),(.43,0,.39),(.64,0,.31),(.81,0,.18),(.94,0,.018)]
tube('arched_U_dip_infill',pts,.013,True)
bpy.ops.object.select_all(action='DESELECT')
for o in asset.objects:o.select_set(True)
bpy.context.view_layer.objects.active=asset.objects[0];bpy.ops.object.convert(target='MESH');bpy.ops.object.transform_apply(location=False,rotation=True,scale=True)
# Exact bottom-center origin for this fragment's bounding box, not a claim about site pavement.
verts=[o.matrix_world@v.co for o in asset.objects for v in o.data.vertices]
lo=Vector(tuple(min(v[i] for v in verts) for i in range(3))); hi=Vector(tuple(max(v[i] for v in verts) for i in range(3)))
shift=Vector(((lo.x+hi.x)/2,(lo.y+hi.y)/2,lo.z))
for o in asset.objects:
 for v in o.data.vertices:v.co-=shift
 for p in o.data.polygons:p.use_smooth=True
bpy.ops.object.select_all(action='DESELECT')
# Export one mesh, retain three editable source components in .blend.
copies=[]
for o in list(asset.objects):
 n=o.copy();n.data=o.data.copy();asset.objects.link(n);copies.append(n);n.select_set(True)
bpy.context.view_layer.objects.active=copies[0];bpy.ops.object.join();exp=bpy.context.object;exp.name='green_railing_upper_panel'
mod=exp.modifiers.new('triangulated_export','TRIANGULATE');bpy.ops.object.modifier_apply(modifier=mod.name)
tri=len(exp.data.polygons);assert tri<6000
out=ROOT/'green_railing_upper_panel.glb'
bpy.ops.export_scene.gltf(filepath=str(out),export_format='GLB',use_selection=True,export_yup=True,export_cameras=False,export_lights=False,export_animations=False)
bpy.data.objects.remove(exp,do_unlink=True)
# Neutral studio is never exported.
floor=mat('studio_floor',(.16,.18,.17),0,.8)
bpy.ops.mesh.primitive_plane_add(size=200,location=(0,0,-.035));plane=bpy.context.object;plane.name='studio_floor';move(plane,studio);plane.data.materials.append(floor)
scene.world.color=(.25,.25,.25);scene.world.use_nodes=True;scene.world.node_tree.nodes['Background'].inputs[0].default_value=(.28,.32,.3,1);scene.world.node_tree.nodes['Background'].inputs[1].default_value=.5
for name,pos,power,size in [('key',(-2,-3,4),650,4),('fill',(3,-1,2),250,3),('rim',(0,3,3),500,3)]:
 d=bpy.data.lights.new(name,'AREA');d.energy=power;d.shape='DISK';d.size=size;o=bpy.data.objects.new(name,d);studio.objects.link(o);o.location=pos;o.rotation_euler=(Vector((0,0,.25))-o.location).to_track_quat('-Z','Y').to_euler()
d=bpy.data.cameras.new('camera');cam=bpy.data.objects.new('camera',d);studio.objects.link(cam);scene.camera=cam
scene.render.engine='CYCLES';scene.cycles.samples=48;scene.cycles.use_denoising=True;scene.render.resolution_x=1400;scene.render.resolution_y=650;scene.render.resolution_percentage=100;scene.view_settings.view_transform='AgX'
for name,pos,scale in [('front',(0,-5,.25),2.3),('side',(5,0,.25),1.3),('photo_like',(2,-5,2.2),2.4)]:
 cam.location=pos;cam.rotation_euler=(Vector((0,0,.23))-cam.location).to_track_quat('-Z','Y').to_euler();d.type='ORTHO';d.ortho_scale=scale;scene.render.filepath=str(ROOT/(name+'.png'));bpy.ops.render.render(write_still=True)
scene.render.filepath='//photo_like.png'
bpy.ops.wm.save_as_mainfile(filepath=str(ROOT/'green_railing_upper_panel.blend'))
(ROOT/'generation.json').write_text(json.dumps({'blender':bpy.app.version_string,'triangles':tri,'bytes':out.stat().st_size,'sha256':hashlib.sha256(out.read_bytes()).hexdigest(),'dimensions_m':list(hi-lo),'origin':'bounding-bottom-center of upper fragment','scope':'upper panel only; no posts/lower decoration/placement; all absolute dimensions inferred'},indent=2))
