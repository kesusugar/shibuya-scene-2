"""Blender 4.2.3 CLI: photo-informed planter wall, inclined silver rail and low pine-like shrubs."""
import bpy,bmesh,json,sys,math,random
from pathlib import Path
from mathutils import Vector
from mathutils.bvhtree import BVHTree
cfg,ground,out,stats=sys.argv[sys.argv.index('--')+1:][:4]
D=json.load(open(cfg));H=json.load(open(D['statue_layout']));cx,cy=H['xy'];a=math.radians(H['yaw_deg']);rng=random.Random(73)
bpy.ops.wm.read_factory_settings(use_empty=True);bpy.ops.import_scene.gltf(filepath=ground)
bm=bmesh.new()
for ob in list(bpy.context.scene.objects):
 if ob.type=='MESH' and ob.name.startswith('ground_sidewalk'):
  me=ob.data.copy();me.transform(ob.matrix_world);bm.from_mesh(me);bpy.data.meshes.remove(me)
bvh=BVHTree.FromBMesh(bm);bm.free()
for ob in list(bpy.context.scene.objects):bpy.data.objects.remove(ob,do_unlink=True)
def world(x,y):return cx+x*math.cos(a)-y*math.sin(a),cy+x*math.sin(a)+y*math.cos(a)
def height(x,y):
 wx,wy=world(x,y);hit=bvh.ray_cast(Vector((wx,wy,50)),Vector((0,0,-1)))
 if hit[0] is None:raise ValueError('equipment outside original sidewalk: '+str((x,y)))
 return hit[0].z
mats={}
def mat(name,color,metal=0,rough=.9):
 m=bpy.data.materials.new('street_surround_'+name);m.use_nodes=True;b=m.node_tree.nodes['Principled BSDF'];b.inputs['Base Color'].default_value=(*color,1);b.inputs['Metallic'].default_value=metal;b.inputs['Roughness'].default_value=rough;mats[name]=m
for name,color,metal,rough in [('stone',(.14,.15,.14),0,.95),('joint',(.055,.065,.06),0,.97),('silver',(.55,.58,.60),.8,.32),('soil',(.07,.06,.04),0,1),('branch',(.11,.075,.04),0,.95),('needle',(.11,.17,.065),0,.92),('needle_light',(.19,.24,.08),0,.92),('rock',(.22,.19,.15),0,.95),('panel',(.065,.105,.10),.5,.88)]:mat(name,color,metal,rough)
objects=[];records=[];leaf_vertices=[];leaf_faces=[];leaf_materials=[]
def finish(o,name,material):
 o.name='street_surround_'+name;o.data.materials.append(mats[material]);objects.append(o);return o
def box(name,loc,size,material,bevel=0):
 bpy.ops.mesh.primitive_cube_add(size=1,location=loc);o=bpy.context.object;o.scale=size;bpy.ops.object.transform_apply(location=False,rotation=False,scale=True)
 if bevel:
  m=o.modifiers.new('stone edge','BEVEL');m.width=bevel;m.segments=2;bpy.ops.object.modifier_apply(modifier=m.name)
 return finish(o,name,material)
def tube(name,p,q,r,material,vertices=12):
 p,q=Vector(p),Vector(q);bpy.ops.mesh.primitive_cylinder_add(vertices=vertices,radius=r,depth=(q-p).length,location=(p+q)/2);o=bpy.context.object;o.rotation_euler=(q-p).to_track_quat('Z','Y').to_euler();return finish(o,name,material)
for seg in D['segments']:
 x0,x1=seg['x0'],seg['x1'];y=D['front_y_m'];depth=D['depth_m'];h=D['wall_height_m'];t=D['wall_thickness_m']
 contacts=[{'local':[x,yy],'xy':world(x,yy),'ground_z':height(x,yy)} for x in [x0,(x0+x1)/2,x1] for yy in [y,y-depth/2,y-depth]];z=min(p['ground_z'] for p in contacts)
 # Individual vertical stone courses rather than a single unbroken box. Bottoms are embedded in the slope.
 count=math.ceil((x1-x0)/.38);step=(x1-x0)/count
 for i in range(count):box('wall_'+seg['id'],(x0+(i+.5)*step,y-t/2,z+h/2),(step-.006,t,h),'stone',.004)
 box('cap_'+seg['id'],((x0+x1)/2,y-t/2,z+h+.035),(x1-x0,.27,.07),'stone',.007)
 for x in [x0+t/2,x1-t/2]:box('return_'+seg['id'],(x,y-depth/2,z+h/2),(t,depth,h),'stone',.004)
 for i in range(count):box('rear_'+seg['id'],(x0+(i+.5)*step,y-depth+t/2,z+h/2),(step-.006,t,h),'stone',.004)
 box('rear_cap_'+seg['id'],((x0+x1)/2,y-depth+t/2,z+h+.035),(x1-x0,.27,.07),'stone',.007)
 box('soil_'+seg['id'],((x0+x1)/2,y-depth/2,z+h-.04),(x1-x0-t*2,depth-t*2,.08),'soil')
 yf=y+.12;yb=yf-D['rail_depth_m'];zf=z+D['rail_front_height_m'];zb=z+D['rail_rear_height_m']
 for yy,zz in [(yf,zf),(yb,zb)]:tube('rail_'+seg['id'],(x0+.05,yy,zz),(x1-.05,yy,zz),D['rail_radius_m'],'silver',20)
 for i in range(4):
  x=x0+.08+i*(x1-x0-.16)/3
  tube('inclined_support_'+seg['id'],(x,yf,zf),(x,yb,zb),.014,'silver')
  tube('leg_'+seg['id'],(x,y+.02,z+.01),(x,y+.02,zf),.018,'silver')
  box('wall_light_'+seg['id'],(x,y+.007,z+.10),(.23,.012,.09),'panel',.003)
 for i in range(D['shrubs_per_segment']):
  x=x0+t+.25+(x1-x0-t*2-.5)*i/max(1,D['shrubs_per_segment']-1);yy=y-depth*.6;bottom=z+h-.03
  tube('shrub_trunk',(x,yy,bottom),(x,yy,bottom+D['shrub_height_m']*.7),.013,'branch')
  # Claude review 2026-10-14: july094/095 show clipped black pine (dense rounded needle tufts on short branches),
  # not the radiating agave-like fans of the first version. Each shrub = a few short branches ending in a
  # rounded tuft: a dark core plus short needles sprouting outward from its surface.
  srng=random.Random(793+(0 if seg['id']=='left' else 100)+i)
  for j in range(D.get('pine_tufts',6)):
   ang=srng.uniform(0,math.tau);reach=srng.uniform(.08,.30);lift=srng.uniform(.35,D['shrub_height_m'])
   tip=Vector((x+math.cos(ang)*reach,yy+math.sin(ang)*reach*.6,bottom+lift));start=Vector((x,yy,bottom+lift*.45))
   tube('shrub_branch',start,tip,.012,'branch',6)
   rad=srng.uniform(.13,.21)
   bpy.ops.mesh.primitive_ico_sphere_add(subdivisions=2,radius=1,location=tip);core=bpy.context.object;core.scale=(rad*.85,rad*.85,rad*.62)
   for v in core.data.vertices:v.co*=srng.uniform(.85,1.1)
   for poly in core.data.polygons:poly.use_smooth=True
   finish(core,'tuft_core','needle')
   for k in range(150):
    d=Vector([srng.gauss(0,1) for _ in range(3)]).normalized()
    if d.z<-.3:d.z=-d.z*.3
    d.normalize();base_p=tip+Vector((d.x*rad*.8,d.y*rad*.8,d.z*rad*.55));end_p=base_p+d*srng.uniform(.05,.10)+Vector((0,0,.015))
    side=d.cross(Vector((0,0,1)));side=side.normalized() if side.length>1e-6 else Vector((1,0,0))
    w=D.get('needle_bundle_width_m',.012)*.6
    start_index=len(leaf_vertices);leaf_vertices.extend([tuple(base_p+side*w),tuple(base_p-side*w),tuple(end_p)]);leaf_faces.append((start_index,start_index+1,start_index+2));leaf_materials.append(1 if srng.random()<.4 else 0)
 for i in range(3):
  x=x0+.35+(x1-x0-.7)*i/2;yy=y-depth*.48
  bpy.ops.mesh.primitive_ico_sphere_add(subdivisions=2,radius=1,location=(x,yy,z+h+.06));o=bpy.context.object;o.scale=(rng.uniform(.30,.42),.24,rng.uniform(.28,.38));   # july094/095: boulders rise well above the cap
  for v in o.data.vertices:v.co*=rng.uniform(.86,1.12)
  for poly in o.data.polygons:poly.use_smooth=True
  finish(o,'rock','rock')
 records.append({'id':seg['id'],'contact_samples':contacts,'anchor_tp':z+15,'max_burial_m':max(p['ground_z'] for p in contacts)-z,'local_bounds':[x0,x1,y-depth,y+.155]})
me=bpy.data.meshes.new('needles');me.from_pydata(leaf_vertices,[],leaf_faces);o=bpy.data.objects.new('needles',me);bpy.context.collection.objects.link(o);finish(o,'needles','needle');me.materials.append(mats['needle_light'])
for polygon,slot in zip(me.polygons,leaf_materials):polygon.material_index=slot
P=D['panel'];px,py=P['xy_local'];w=P['width_m'];dep=P['depth_m'];samples=[{'local':[x,y],'xy':world(x,y),'ground_z':height(x,y)} for x in [px-w/2,px,px+w/2] for y in [py-dep/2,py+dep/2]];z=min(p['ground_z'] for p in samples)
if not P.get('replaced_by'):
 box('stone_panel',(px,py,z+P['height_m']/2),(w,dep,P['height_m']),'stone',.015)
 box('unread_inscription',(px,py+dep/2+.003,z+P['height_m']*.62),(w*.78,.008,P['height_m']*.52),'panel',.003)
records.append({'id':'stone-panel','contact_samples':samples,'anchor_tp':z+15,'max_burial_m':max(p['ground_z'] for p in samples)-z,'replaced_by':P.get('replaced_by')})
# Bake transforms then group by material: few draw calls despite thousands of procedural needles.
for o in objects:
 bpy.ops.object.select_all(action='DESELECT');o.select_set(True);bpy.context.view_layer.objects.active=o;bpy.ops.object.transform_apply(location=False,rotation=True,scale=True)
 o.rotation_euler.z=a;x,y=world(o.location.x,o.location.y);o.location.x=x;o.location.y=y
groups={material:[o for o in objects if o.data.materials[0]==material] for material in mats.values()}
for material,group in groups.items():
 if not group:continue
 bpy.ops.object.select_all(action='DESELECT')
 for o in group:o.select_set(True)
 bpy.context.view_layer.objects.active=group[0]
 if len(group)>1:bpy.ops.object.join()
 o=bpy.context.object;o.name='street_surround_'+material.name.removeprefix('street_surround_')
 # Leaves are visible from both sides in glTF.
 if 'needle' in material.name:material.use_backface_culling=False
bpy.ops.object.empty_add();root=bpy.context.object;root.name='street_surround'
for o in list(bpy.context.scene.objects):
 if o!=root:o.parent=root
bpy.ops.export_scene.gltf(filepath=out,export_format='GLB',export_yup=True,export_materials='EXPORT')
Path(stats).write_text(json.dumps({'config':D,'items':records,'triangles':sum(len(p.vertices)-2 for o in bpy.context.scene.objects if o.type=='MESH' for p in o.data.polygons)},indent=1)+'\n')

