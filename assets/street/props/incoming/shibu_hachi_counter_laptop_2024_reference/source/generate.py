"""Counter laptop silhouette, 2024 photographic reference; Blender 4.2.3.
Run: blender -b -t 2 -P source/generate.py -- OUTPUT_DIRECTORY
No source photo, fonts, textures, internet, or nonstandard Python dependencies.
"""
import bpy, sys, math, json, time, bmesh
from pathlib import Path
from mathutils import Vector, Matrix
START=time.perf_counter()
O=Path(sys.argv[sys.argv.index('--')+1]).resolve() if '--' in sys.argv else Path(__file__).resolve().parent.parent
O.mkdir(parents=True,exist_ok=True)
bpy.ops.object.select_all(action='SELECT');bpy.ops.object.delete(use_global=False)
for m in list(bpy.data.materials):bpy.data.materials.remove(m)
s=bpy.context.scene;s.unit_settings.system='METRIC';s.unit_settings.scale_length=1.0
s['asset']='shibu_hachi_counter_laptop_2024_reference'
s['evidence_scope']='Temporary movable equipment in September 2024 photograph; not current fixed landmark; no manufacturer/model assertion.'
s['placement']='Unplaced; bottom centre of full open envelope; visitor-facing lid back is Blender -Y.'
M={}
def material(name,rgba,rough,metal=0):
 m=bpy.data.materials.new(name);m.use_nodes=True;m.diffuse_color=(*rgba,1);p=m.node_tree.nodes.get('Principled BSDF');p.inputs['Base Color'].default_value=(*rgba,1);p.inputs['Roughness'].default_value=rough;p.inputs['Metallic'].default_value=metal;M[name]=m;return m
shell=material('01_Champagne_metal_observed_warm_light_estimate',(.43,.34,.24),.30,.72)
black=material('02_Neutral_dark_hinge_and_estimated_input_details',(.014,.016,.018),.42,.05)
glass=material('03_Inactive_neutral_display_no_UI',(.021,.028,.032),.19,.12)
objects=[]
def mesh_obj(name,verts,faces,mat,status):
 me=bpy.data.meshes.new(name+'_mesh');me.from_pydata(verts,[],faces);me.update();ob=bpy.data.objects.new(name,me);s.collection.objects.link(ob);me.materials.append(mat);ob['evidence']=status;objects.append(ob);return ob

def box(name,loc,dim,mat,bev=.001,status='Unseen conservative closure geometry, not surveyed'):
 bpy.ops.mesh.primitive_cube_add(size=1,location=loc);ob=bpy.context.object;ob.name=name;ob.dimensions=dim;bpy.ops.object.transform_apply(location=False,rotation=False,scale=True);ob.data.materials.append(mat)
 if bev:
  mod=ob.modifiers.new('Manufactured_edge','BEVEL');mod.width=bev;mod.segments=2;bpy.context.view_layer.objects.active=ob;bpy.ops.object.modifier_apply(modifier=mod.name)
 ob['evidence']=status;objects.append(ob);return ob

def round_outline(width,height,r,n=6):
 v=[]
 for cx,cz,a0 in [(width/2-r,height/2-r,0),(-width/2+r,height/2-r,90),(-width/2+r,-height/2+r,180),(width/2-r,-height/2+r,270)]:
  for j in range(n+1):
   a=math.radians(a0+j*90/n);v.append((cx+r*math.cos(a),cz+r*math.sin(a)))
 return v

def rounded_slab(name,w,h,t,r,mat,status):
 # In local X/Z with thickness along Y, chamfered cross section.
 bevel=min(t*.22,.0007);verts=[]
 layers=[(-t/2,w-2*bevel,h-2*bevel,r-bevel),(-t/2+bevel,w,h,r),(t/2-bevel,w,h,r),(t/2,w-2*bevel,h-2*bevel,r-bevel)]
 for y,ww,hh,rr in layers:verts.extend([(x,y,z) for x,z in round_outline(ww,hh,max(rr,.0001))])
 N=len(verts)//4;faces=[tuple(range(N-1,-1,-1)),tuple(range(3*N,4*N))]
 for k in range(3):
  for i in range(N):faces.append((k*N+i,k*N+(i+1)%N,(k+1)*N+(i+1)%N,(k+1)*N+i))
 ob=mesh_obj(name,verts,faces,mat,status)
 # Recalculate so orientation does not depend on local ring winding.
 bpy.context.view_layer.objects.active=ob;ob.select_set(True);bpy.ops.object.mode_set(mode='EDIT');bpy.ops.mesh.select_all(action='SELECT');bpy.ops.mesh.normals_make_consistent(inside=False);bpy.ops.object.mode_set(mode='OBJECT');ob.select_set(False)
 return ob

# Base envelope is mostly occluded in reference. Do not assert branded hardware.
# Rear at -Y; operator edge at +Y. Wedge is an explicitly estimated closure.
w=.304;d=.212
v=[(-w/2,-d/2,.0018),(w/2,-d/2,.0018),(w/2,d/2,.0018),(-w/2,d/2,.0018),(-w/2,-d/2,.0145),(w/2,-d/2,.0145),(w/2,d/2,.0065),(-w/2,d/2,.0065)]
f=[(3,2,1,0),(0,1,5,4),(1,2,6,5),(2,3,7,6),(3,0,4,7),(4,5,6,7)]
base=mesh_obj('Estimated_tapered_input_chassis',v,f,shell,'Rear base edge visible; depth, taper and underside conservatively estimated.')
bpy.context.view_layer.objects.active=base;mod=base.modifiers.new('Soft_chassis_edges','BEVEL');mod.width=.002;mod.segments=4;bpy.ops.object.modifier_apply(modifier=mod.name)
# Subtle bottom seam and four supports kept deliberately generic.
for x in [-.112,.112]:
 for y in [-.074,.074]:
  bpy.ops.mesh.primitive_cylinder_add(vertices=16,radius=.006,depth=.002,location=(x,y,.001));ob=bpy.context.object;ob.name='Estimated_rubber_support';ob.data.materials.append(black);ob['evidence']='Unseen support estimate, no manufacturer match';objects.append(ob)
# Long dark hinge line has simple metal ends. No invented ports or screws.
box('Estimated_hinge_bar',(0,-.095,.016),(.263,.011,.010),black,.002)
for x in [-.138,.138]:box('Estimated_hinge_end',(x,-.095,.016),(.012,.011,.010),shell,.002)
# Lid leans away from the operator by 12 degrees. The photograph cannot calibrate this.
angle=math.radians(12);hinge=Vector((0,-.096,.017));R=Matrix.Rotation(angle,4,'X');H=.207
lid=rounded_slab('Observed_plain_rounded_lid_back',.304,H,.0058,.007,shell,'Observed lid outline and metallic appearance; logo/stickers intentionally excluded. Size and angle estimated.')
lid.location=hinge+R@Vector((0,0,H/2));lid.rotation_euler.x=angle
# Operator-side content cannot be seen in the source. This neutral closed surface is not a photographed UI.
bezel=rounded_slab('Estimated_operator_bezel',.297,.199,.0012,.005,black,'Unseen conservative neutral display bezel; exact construction unverified.')
bezel.location=hinge+R@Vector((0,.0031,H/2));bezel.rotation_euler.x=angle
panel=rounded_slab('Estimated_inactive_display',.277,.173,.0006,.0025,glass,'Unseen neutral inactive panel; not a photograph or inferred live interface.')
panel.location=hinge+R@Vector((0,.00385,H/2+.003));panel.rotation_euler.x=angle
# Generic input silhouette on occluded side, with no language, key legends, or brand geometry.
# This is NOT a claimed physical key layout. It prevents an open unfinished reverse side.
def top_z(y):return .0145-(y+d/2)/d*.008
kb=box('Estimated_keyboard_recess',(0,-.031,top_z(-.031)+.0003),(.264,.094,.0008),black,.001)
kb.rotation_euler.x=-math.atan(.008/d)
for row in range(5):
 y=-.067+row*.0174
 for col in range(13):
  x=(col-6)*.0192
  key=box('Estimated_unlabelled_key_%02d_%02d'%(row,col),(x,y,top_z(y)+.0010),(.0168,.0148,.0013),black,.0006)
  key.rotation_euler.x=-math.atan(.008/d)
space=box('Estimated_unlabelled_space_key',(0,.022,top_z(.022)+.0010),(.106,.013,.0013),black,.0006);space.rotation_euler.x=-math.atan(.008/d)
# Trackpad: fine dark shadow seam, with warm shell insert, fully labelled estimated.
pad=box('Estimated_trackpad_shadow',(0,.066,top_z(.066)+.0002),(.107,.048,.00045),black,.0006);pad.rotation_euler.x=-math.atan(.008/d)
pad=box('Estimated_trackpad_surface',(0,.066,top_z(.066)+.0005),(.1058,.0468,.0004),shell,.0005);pad.rotation_euler.x=-math.atan(.008/d)
# Full open-envelope bottom-centre origin, not hinge origin. Apply transforms to all editable parts.
bpy.context.view_layer.update();pts=[o.matrix_world@v.co for o in objects for v in o.data.vertices]
mn=[min(p[i] for p in pts) for i in range(3)];mx=[max(p[i] for p in pts) for i in range(3)];shift=Vector((-(mn[0]+mx[0])/2,-(mn[1]+mx[1])/2,-mn[2]))
for o in objects:o.location+=shift
bpy.ops.object.select_all(action='DESELECT')
for o in objects:o.select_set(True)
bpy.context.view_layer.objects.active=objects[0];bpy.ops.object.transform_apply(location=True,rotation=True,scale=True)
for o in objects:o['asset_id']='shibu_hachi_counter_laptop_2024_reference'
# Collapse zero-area bevel residues on submillimetre keys before final export.
for o in objects:
 bm=bmesh.new();bm.from_mesh(o.data);bmesh.ops.remove_doubles(bm,verts=list(bm.verts),dist=1e-7);bmesh.ops.dissolve_degenerate(bm,edges=list(bm.edges),dist=1e-7);bm.to_mesh(o.data);bm.free();o.data.update()
# Apply weighted custom normals so broad planes stay flat despite edge bevels.
for o in objects:
 bpy.context.view_layer.objects.active=o
 for p in o.data.polygons:p.use_smooth=True
 mod=o.modifiers.new('Area_weighted_normals','WEIGHTED_NORMAL');mod.keep_sharp=True;mod.weight=50;bpy.ops.object.modifier_apply(modifier=mod.name)
# Retain editable parts in blend, batch GLB by material for three portable draw primitives.
batches=[]
for m in M.values():
 bpy.ops.object.select_all(action='DESELECT');copies=[]
 for original in objects:
  if original.data.materials[0]==m:
   ob=original.copy();ob.data=original.data.copy();s.collection.objects.link(ob);ob.select_set(True);copies.append(ob)
 if copies:
  bpy.context.view_layer.objects.active=copies[0]
  if len(copies)>1:bpy.ops.object.join()
  ob=bpy.context.object;ob.name='Batch_'+m.name;batches.append(ob)
bpy.ops.object.select_all(action='DESELECT')
for o in batches:o.select_set(True)
bpy.context.view_layer.objects.active=batches[0]
bpy.ops.export_scene.gltf(filepath=str(O/'shibu_hachi_counter_laptop.glb'),export_format='GLB',use_selection=True,export_yup=True,export_extras=False,export_cameras=False,export_lights=False)
for o in batches:bpy.data.objects.remove(o,do_unlink=True)
bpy.ops.object.select_all(action='DESELECT')
for o in objects:o.select_set(True)
bpy.context.view_layer.objects.active=objects[0]
bpy.context.preferences.filepaths.save_version=0
bpy.ops.file.pack_all();bpy.ops.wm.save_as_mainfile(filepath=str(O/'shibu_hachi_counter_laptop.blend'))
pts=[o.matrix_world@v.co for o in objects for v in o.data.vertices];mn=[min(p[i] for p in pts) for i in range(3)];mx=[max(p[i] for p in pts) for i in range(3)]
tri=sum(len(p.vertices)-2 for o in objects for p in o.data.polygons)
assert bpy.app.version[:3]==(4,2,3)
assert all(math.isfinite(c) for p in pts for c in p)
assert abs(mn[2])<1e-6 and abs(mx[0]+mn[0])<1e-6 and abs(mx[1]+mn[1])<1e-6
assert tri<16000
json.dump({'blender_version':bpy.app.version_string,'asset':'shibu_hachi_counter_laptop_2024_reference','units':'metres','origin':'bottom centre of full open envelope','visitor_facing_lid_back':'-Y','bounds_blender_m':[mn,mx],'dimensions_m':[mx[i]-mn[i] for i in range(3)],'triangles':tri,'editable_objects':len(objects),'export_material_batches':len(M),'external_files':[],'textures':0,'reference_date':'2024-09-19 publication; capture date unknown','current_presence_verified':False,'runtime_placement':False,'seconds_build_export_save':time.perf_counter()-START},open(O/'build_stats.json','w'),indent=2)
print('BUILD_COMPLETE',json.load(open(O/'build_stats.json')))
