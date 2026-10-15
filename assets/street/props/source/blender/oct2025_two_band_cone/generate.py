"""Blender 4.2.3: two-white-band construction cone, dimensions inferred from dated reference."""
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
red=mat('prop_furniture_0',(.72,.055,.018),0,.42)
white=mat('prop_furniture_1',(.82,.84,.82),0,.3)
rubber=mat('prop_furniture_2',(.012,.014,.014),0,.83)
def block(name,loc,scale,material,bevel):
 bpy.ops.mesh.primitive_cube_add(size=1,location=loc);o=bpy.context.object;o.name=name;move(o,asset);o.dimensions=scale;bpy.ops.object.transform_apply(location=False,rotation=False,scale=True);o.data.materials.append(material)
 m=o.modifiers.new('rounded_moulded_edges','BEVEL');m.width=bevel;m.segments=3;bpy.context.view_layer.objects.active=o;bpy.ops.object.modifier_apply(modifier=m.name)
 return o
block('black_weight_base',(0,0,.016),(.38,.38,.032),rubber,.012)
block('red_square_foot',(0,0,.044),(.32,.32,.032),red,.010)
# A continuous cone surface with two white material bands; no emissive material.
rings=[(.06,.145),(.29,.099),(.38,.081),(.47,.063),(.55,.047),(.69,.019),(.7,.015)]
N=48;vs=[];fs=[];mi=[]
for z,r in rings:
 for i in range(N):a=2*math.pi*i/N;vs.append((r*math.cos(a),r*math.sin(a),z))
for j in range(len(rings)-1):
 for i in range(N):fs.append((j*N+i,j*N+(i+1)%N,(j+1)*N+(i+1)%N,(j+1)*N+i));mi.append(1 if j in (1,3) else 0)
fs.append(tuple(reversed(range(N))));mi.append(0)
fs.append(tuple((len(rings)-1)*N+i for i in range(N)));mi.append(0)
me=bpy.data.meshes.new('cone_body');me.from_pydata(vs,[],fs);me.update();o=bpy.data.objects.new('two_band_cone_body',me);asset.objects.link(o);me.materials.append(red);me.materials.append(white)
for poly,idx in zip(me.polygons,mi):poly.material_index=idx;poly.use_smooth=len(poly.vertices)==4
bpy.ops.object.select_all(action='DESELECT')
for o in asset.objects:o.select_set(True)
bpy.context.view_layer.objects.active=asset.objects[0];bpy.ops.object.transform_apply(location=True,rotation=True,scale=True)
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
bpy.context.view_layer.objects.active=copies[0];bpy.ops.object.join();exp=bpy.context.object;exp.name='oct2025_two_band_cone'
mod=exp.modifiers.new('triangulated_export','TRIANGULATE');bpy.ops.object.modifier_apply(modifier=mod.name)
tri=len(exp.data.polygons);assert tri<6000
out=ROOT/'oct2025_two_band_cone.glb'
bpy.ops.export_scene.gltf(filepath=str(out),export_format='GLB',use_selection=True,export_yup=True,export_cameras=False,export_lights=False,export_animations=False)
bpy.data.objects.remove(exp,do_unlink=True)
# Neutral studio is never exported.
floor=mat('studio_floor',(.16,.18,.17),0,.8)
bpy.ops.mesh.primitive_plane_add(size=200,location=(0,0,-.001));plane=bpy.context.object;plane.name='studio_floor';move(plane,studio);plane.data.materials.append(floor)
scene.world.color=(.25,.25,.25);scene.world.use_nodes=True;scene.world.node_tree.nodes['Background'].inputs[0].default_value=(.28,.32,.3,1);scene.world.node_tree.nodes['Background'].inputs[1].default_value=.5
for name,pos,power,size in [('key',(-2,-3,4),650,4),('fill',(3,-1,2),250,3),('rim',(0,3,3),500,3)]:
 d=bpy.data.lights.new(name,'AREA');d.energy=power;d.shape='DISK';d.size=size;o=bpy.data.objects.new(name,d);studio.objects.link(o);o.location=pos;o.rotation_euler=(Vector((0,0,.35))-o.location).to_track_quat('-Z','Y').to_euler()
d=bpy.data.cameras.new('camera');cam=bpy.data.objects.new('camera',d);studio.objects.link(cam);scene.camera=cam
scene.render.engine='CYCLES';scene.cycles.samples=48;scene.cycles.use_denoising=True;scene.render.resolution_x=900;scene.render.resolution_y=1100;scene.render.resolution_percentage=100;scene.view_settings.view_transform='AgX'
for name,pos,scale in [('front',(0,-5,.35),1.15),('side',(5,0,.35),1.15),('photo_like',(1.5,-5,1.3),1.15)]:
 cam.location=pos;cam.rotation_euler=(Vector((0,0,.35))-cam.location).to_track_quat('-Z','Y').to_euler();d.type='ORTHO';d.ortho_scale=scale;scene.render.filepath=str(ROOT/(name+'.png'));bpy.ops.render.render(write_still=True)
scene.render.filepath='//photo_like.png'
bpy.ops.wm.save_as_mainfile(filepath=str(ROOT/'oct2025_two_band_cone.blend'))
(ROOT/'generation.json').write_text(json.dumps({'blender':bpy.app.version_string,'triangles':tri,'bytes':out.stat().st_size,'sha256':hashlib.sha256(out.read_bytes()).hexdigest(),'dimensions_m':list(hi-lo),'origin':'bounding-bottom-center','scope':'one cone only, two white bands, inferred base and absolute dimensions, no placement'},indent=2))
