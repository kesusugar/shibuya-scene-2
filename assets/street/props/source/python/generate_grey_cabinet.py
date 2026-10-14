"""Rebuild the photo-referenced cabinet. Run with official Blender 4.2.3 -b -P thisfile.
No downloads/dependencies. Local coordinates: X right, Y back, Z up, front=-Y.
All absolute dimensions and concealed details are assumptions, NOT survey data.
"""
import bpy, math, json, sys
from pathlib import Path
from mathutils import Vector
OUT=Path(__file__).resolve().parent
ID='grey_louvered_cabinet'
assert bpy.app.version[:3]==(4,2,3), f'Required Blender 4.2.3, got {bpy.app.version_string}'
bpy.ops.wm.read_factory_settings(use_empty=True)
sc=bpy.context.scene; sc.unit_settings.system='METRIC'; sc.unit_settings.scale_length=1
asset=bpy.data.collections.new('ASSET | cabinet only');sc.collection.children.link(asset)
studio=bpy.data.collections.new('STUDIO | not exported');sc.collection.children.link(studio)
def mat(name,c,metal=.35,rough=.55):
 m=bpy.data.materials.new(name);m.diffuse_color=(*c,1);m.use_nodes=True;p=m.node_tree.nodes.get('Principled BSDF');p.inputs['Base Color'].default_value=(*c,1);p.inputs['Metallic'].default_value=metal;p.inputs['Roughness'].default_value=rough;return m
paint=mat('Cabinet charcoal paint',(.095,.115,.12),.5,.48)
dark=mat('Cabinet shadow recess',(.03,.04,.043),.35,.66)
edge=mat('Cabinet rib edges',(.15,.17,.17),.55,.42)
base=mat('Cabinet mineral footing',(.12,.13,.125),.05,.89)
def move(o,col):
 for c in list(o.users_collection):c.objects.unlink(o)
 col.objects.link(o)
def box(name,loc,dim,ma,bevel=0):
 bpy.ops.mesh.primitive_cube_add(size=1, location=loc);o=bpy.context.object;o.name=name;o.dimensions=dim;bpy.ops.object.transform_apply(location=False,rotation=False,scale=True);o.data.materials.append(ma);move(o,asset)
 if bevel:
  mod=o.modifiers.new('Small sheet-metal edge','BEVEL');mod.width=bevel;mod.segments=1;bpy.ops.object.modifier_apply(modifier=mod.name)
 return o
# Overall envelope including lip and slab: 1.28 x .43 x 1.92 m.
box('Concrete footing | inferred under occlusion',(0,0,.025),(1.28,.43,.05),base,.005)
box('Cabinet shell | unseen back plain',(0,0,.965),(1.23,.37,1.83),paint,.004)
box('Recessed front backing',(0,-.188,.967),(1.19,.012,1.77),dark)
box('Top cap lip',(0,0,1.90),(1.27,.415,.04),paint,.005)
box('Top shadow seam',(0,-.192,1.873),(1.23,.009,.012),dark)
# Insets observed in the photo. Lower right details are occluded and simplified.
upper=(-.545,.23,1.355,1.805);lower=(-.545,.52,.105,.53)
verts=[];faces=[];mats=[]
def rib(a,b,z,y,material):
 # folded metal strip: two facets, open back against opaque shell
 k=len(verts);verts.extend([(a,y,z),(b,y,z),(a,y-.006,z-.003),(b,y-.006,z-.003),(a,y-.003,z-.006),(b,y-.003,z-.006)])
 faces.extend([(k,k+1,k+3,k+2),(k+2,k+3,k+5,k+4)]);mats.extend([material,material])
for i in range(143):
 z=.095+i*.01235
 bounds=[(-.59,.59,False)]
 for x0,x1,z0,z1 in (upper,lower):
  if z0<z<z1:bounds=[(-.59,x0,False),(x0,x1,True),(x1,.59,False)]
 for a,b,inside in bounds:rib(a,b,z,-.201 if not inside else -.204,1 if inside else 0)
me=bpy.data.meshes.new('Folded horizontal ribs');me.from_pydata(verts,[],faces);me.materials.append(edge);me.materials.append(paint);o=bpy.data.objects.new('143 folded front ribs',me);asset.objects.link(o)
for p,mi in zip(me.polygons,mats):p.material_index=mi
for label,(x0,x1,z0,z1) in [('Upper three-bay vent',upper),('Lower service panel',lower)]:
 y=-.217
 for x in (x0,x1):box(label+' vertical frame',(x,y,(z0+z1)/2),(.012,.018,z1-z0+.015),edge)
 for z in (z0,z1):box(label+' horizontal frame',((x0+x1)/2,y,z),(x1-x0,.018,.012),edge)
 n=3 if 'Upper' in label else 4
 for j in range(1,n):box(label+' mullion',(x0+(x1-x0)*j/n,y,(z0+z1)/2),(.009,.017,z1-z0),paint)
# Narrow corner posts.
for x in [-.603,.603]:box('Folded corner',(x,-.196,.965),(.017,.017,1.81),paint)
# Side upper vent is visible on left; corresponding right is a symmetry assumption.
for side in (-1,1):
 x=side*.619
 box('Side vent dark recess',(x,0,1.565),(.008,.275,.46),dark)
 for y in (-.145,.145):box('Side grille edge',(x+side*.006,y,1.565),(.013,.012,.485),edge)
 for z in (1.325,1.805):box('Side grille edge',(x+side*.006,0,z),(.013,.29,.012),edge)
 for i in range(37):box('Side vent blade',(x+side*.006,0,1.34+i*.01235),(.011,.275,.004),paint)
# Original photo does not resolve a handle or brand; no invented lettering/hardware.
# Normalize the exact envelope including protruding frames to bottom-center.
coords=[o.matrix_world @ Vector(c) for o in asset.objects for c in o.bound_box]
lo=Vector(tuple(min(p[i] for p in coords) for i in range(3)));hi=Vector(tuple(max(p[i] for p in coords) for i in range(3)))
shift=Vector(((lo.x+hi.x)/2,(lo.y+hi.y)/2,lo.z))
for o in asset.objects:o.location-=shift
bpy.context.view_layer.update()
bpy.ops.object.select_all(action='DESELECT')
for o in asset.objects:o.select_set(True)
bpy.context.view_layer.objects.active=next(iter(asset.objects))
sc.cursor.location=(0,0,0);bpy.ops.object.origin_set(type='ORIGIN_CURSOR')
# Join temporary duplicates only; editable individual parts remain in the blend.
bpy.ops.object.duplicate()
bpy.ops.object.join()
joined=bpy.context.object;joined.name=ID
bpy.ops.export_scene.gltf(filepath=str(OUT/(ID+'_source.glb')),export_format='GLB',use_selection=True,export_yup=True)
bpy.data.objects.remove(joined,do_unlink=True)
# Non-export studio for reproducible inspection. White ground is only a render helper.
floor=box('STUDIO ground',(0,0,-.036),(2000,2000,.04),mat('Studio floor',(.15,.185,.21),0,.9));move(floor,studio)
world=bpy.data.worlds.new('Soft studio');sc.world=world;world.use_nodes=True;world.node_tree.nodes['Background'].inputs[0].default_value=(.5,.58,.65,1);world.node_tree.nodes['Background'].inputs[1].default_value=.45
for name,loc,power,size in [('Key',(-3,-4,5),650,4),('Fill',(3,-2,3),400,3),('Rim',(1,3,4),800,3)]:
 data=bpy.data.lights.new(name,'AREA');data.energy=power;data.shape='DISK';data.size=size;o=bpy.data.objects.new(name,data);studio.objects.link(o);o.location=loc;o.rotation_euler=(Vector((0,0,1))-o.location).to_track_quat('-Z','Y').to_euler()
camdata=bpy.data.cameras.new('Inspection camera');cam=bpy.data.objects.new('Inspection camera',camdata);studio.objects.link(cam);sc.camera=cam
sc.render.engine='CYCLES';sc.cycles.samples=32;sc.cycles.use_denoising=True;sc.render.resolution_x=1100;sc.render.resolution_y=1400;sc.render.resolution_percentage=100
sc.view_settings.view_transform='AgX';sc.render.image_settings.file_format='PNG'
def view(name,pos,target,ortho=None):
 cam.location=pos;cam.rotation_euler=(Vector(target)-cam.location).to_track_quat('-Z','Y').to_euler();camdata.type='ORTHO' if ortho else 'PERSP';camdata.ortho_scale=ortho or 2.5;camdata.lens=75
 sc.render.filepath=str(OUT/(name+'.png'));bpy.ops.render.render(write_still=True)
view('view_photo_matched',(-3.0,-6.0,2.7),(0,0,.98))
view('view_front',(0,-6,.96),(0,0,.96),2.23)
view('view_side',(-6,0,.96),(0,0,.96),2.23)
# Save editable source in the useful photo-like perspective.
cam.location=(-3,-6,2.7);cam.rotation_euler=(Vector((0,0,.98))-cam.location).to_track_quat('-Z','Y').to_euler();camdata.type='PERSP'
for o in studio.objects:o.hide_set(True)
for o in asset.objects:o.select_set(True)
sc['reference_location']='Minami-Azabu Building, Minato; NOT verified Shibuya placement'
sc['dimensions_status']='All metric dimensions inferred; no survey scale'
sc['regeneration_version']=bpy.app.version_string
bpy.ops.wm.save_as_mainfile(filepath=str(OUT/(ID+'.blend')), compress=True)
tri=0
for o in asset.objects:o.data.calc_loop_triangles();tri+=len(o.data.loop_triangles)
(OUT/'generation_qa.json').write_text(json.dumps({'blender':bpy.app.version_string,'source_triangles':tri,'asset_meshes':len(asset.objects),'units':'meter','origin':'bottom center','dimensions_m':[round(v,6) for v in (hi-lo)],'front':'-Y','reference_match':'Approximate camera only, not calibrated','placement':'NOT PLACED'},indent=2))
