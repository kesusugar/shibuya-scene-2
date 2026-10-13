"""Blender 4.2.3: photo-informed seated bronze dog and stone plinth; dimensions estimated."""
import bpy,bmesh,json,math,sys,random
from pathlib import Path
from mathutils import Vector
from mathutils.bvhtree import BVHTree
cfg,ground,out,stats=sys.argv[sys.argv.index('--')+1:][:4]
D=json.load(open(cfg));cx,cy=D['xy'];angle=math.radians(D['yaw_deg']);base_objects=[]
bpy.ops.wm.read_factory_settings(use_empty=True);bpy.ops.import_scene.gltf(filepath=ground)
bm=bmesh.new()
for ob in list(bpy.context.scene.objects):
 if ob.type=='MESH' and ob.name.startswith('ground_sidewalk'):
  me=ob.data.copy();me.transform(ob.matrix_world);bm.from_mesh(me);bpy.data.meshes.remove(me)
bvh=BVHTree.FromBMesh(bm);bm.free()
for ob in list(bpy.context.scene.objects):bpy.data.objects.remove(ob,do_unlink=True)
def world(x,y):return cx+x*math.cos(angle)-y*math.sin(angle),cy+x*math.sin(angle)+y*math.cos(angle)
samples=[]
for x in [-D['base_size_m'][0]/2,0,D['base_size_m'][0]/2]:
 for y in [-D['base_size_m'][1]/2,0,D['base_size_m'][1]/2]:
  wx,wy=world(x,y);hit=bvh.ray_cast(Vector((wx,wy,50)),Vector((0,0,-1)))
  if hit[0] is None:raise ValueError('plinth footprint outside original sidewalk')
  samples.append({'xy':[wx,wy],'ground_z':hit[0].z})
anchor=min(p['ground_z'] for p in samples)
materials={}
def material(name,color,metal=0,rough=.9,texture=None):
 m=bpy.data.materials.new('street_hachiko_'+name);m.use_nodes=True;b=m.node_tree.nodes['Principled BSDF'];b.inputs['Base Color'].default_value=(*color,1);b.inputs['Metallic'].default_value=metal;b.inputs['Roughness'].default_value=rough
 if texture:
  t=m.node_tree.nodes.new('ShaderNodeTexImage');t.image=bpy.data.images.load(str(Path(cfg).parent/texture));m.node_tree.links.new(t.outputs['Color'],b.inputs['Base Color'])
 materials[name]=m;return m
material('bronze',(1,1,1),.35,.78,'bronze.png');material('stone',(1,1,1),0,.92,'granite.png');material('base',(.12,.13,.13));material('dark',(.025,.032,.028),.65,.85);material('letter',(.20,.14,.09),.6,.82)
def finish(ob,name,mat):
 ob.name='street_hachiko_'+name;ob.data.materials.append(materials[mat]);return ob
def box(name,loc,size,mat,bevel=.008):
 bpy.ops.mesh.primitive_cube_add(size=1,location=loc);o=bpy.context.object;o.scale=size;bpy.ops.object.transform_apply(location=False,rotation=False,scale=True)
 if bevel:
  m=o.modifiers.new('soft stone edges','BEVEL');m.width=bevel;m.segments=2;bpy.context.view_layer.objects.active=o;bpy.ops.object.modifier_apply(modifier=m.name)
 return finish(o,name,mat)
box('foot',(0,0,.125),(*D['base_size_m'],.25),'base')
box('plinth',(0,0,.25+D['plinth_height_m']/2),(*D['plinth_size_m'],D['plinth_height_m']),'stone')
top=.25+D['plinth_height_m'];box('bronze_base',(0,0,top+.045),(*D['bronze_base_size_m'],.09),'bronze')
# Plaque text is a self-made glyph texture, not a crop of a reference photograph.
plaque=box('plaque',(0,D['plinth_size_m'][1]/2+.002,.25+D['plinth_height_m']*.49),(.16,.009,.55),'dark',.002)
material('plaque',(1,1,1),.6,.85,'plaque.png')
me=bpy.data.meshes.new('plaque_text');me.from_pydata([(-.076,D['plinth_size_m'][1]/2+.008,.25+D['plinth_height_m']*.49-.267),(.076,D['plinth_size_m'][1]/2+.008,.25+D['plinth_height_m']*.49-.267),(.076,D['plinth_size_m'][1]/2+.008,.25+D['plinth_height_m']*.49+.267),(-.076,D['plinth_size_m'][1]/2+.008,.25+D['plinth_height_m']*.49+.267)],[],[(0,3,2,1)]);me.uv_layers.new()
for loop,uv in zip(me.uv_layers.active.data,[(0,0),(0,1),(1,1),(1,0)]):loop.uv=uv
o=bpy.data.objects.new('street_hachiko_plaque_text',me);bpy.context.collection.objects.link(o);me.materials.append(materials['plaque'])
# Local coordinates: front is +Y; upright chest, separated front legs, seated haunches.
parts=[]
def ell(name,loc,scale,collect=True,mat='bronze'):
 bpy.ops.mesh.primitive_uv_sphere_add(segments=32,ring_count=20,location=loc);o=bpy.context.object;o.scale=scale;bpy.ops.object.transform_apply(location=False,rotation=False,scale=True);finish(o,name,mat)
 if collect:parts.append(o)
 return o
ell('rump',(0,-.12,.25),(.23,.26,.27));ell('chest',(0,.08,.54),(.195,.21,.36));ell('neck',(0,.15,.75),(.13,.145,.24));ell('head',(0,.21,.98),(.16,.17,.135));ell('jaw',(0,.34,.904),(.09,.105,.045))
# Tapered canine snout rather than a spherical muzzle; blends into the remeshed skull.
v=[];f=[]
for y,z,rx,rz in [(.30,.925,.10,.06),(.34,.94,.105,.07),(.40,.95,.075,.05),(.46,.95,.045,.025)]:
 for i in range(16):
  t=i*math.tau/16;v.append((rx*math.cos(t),y,z+rz*math.sin(t)))
for j in range(3):
 for i in range(16):f.append((j*16+i,j*16+(i+1)%16,(j+1)*16+(i+1)%16,(j+1)*16+i))
f.extend([tuple(range(15,-1,-1)),tuple(range(48,64))]);me=bpy.data.meshes.new('tapered_muzzle');me.from_pydata(v,[],f);o=bpy.data.objects.new('tapered_muzzle',me);bpy.context.collection.objects.link(o);finish(o,'muzzle','bronze');parts.append(o)
for x in [-.145,.145]:
 ell('thigh',(x*1.22,-.15,.20),(.105,.17,.20));ell('hind_paw',(x*1.32,-.03,.055),(.095,.13,.052));ell('shoulder',(x,.10,.58),(.08,.13,.16));ell('foreleg',(x,.21,.29),(.051,.072,.285));ell('front_paw',(x,.255,.047),(.068,.10,.047))
# Tail curls onto the back of the bronze base, visible in the side reference.
for i in range(13):
 a=math.pi+i*math.pi/17;ell('tail',(.14+.19*math.cos(a),-.22+.19*math.sin(a),.067),(.065,.065,.054))
# Closed triangular ear solids: one upright, the other bent, as visible in July photographs.
def ear(name,points):
 v=[(x,y-.018,z) for x,y,z in points]+[(x,y+.018,z) for x,y,z in points];f=[(0,2,1),(3,4,5),(0,1,4,3),(1,2,5,4),(2,0,3,5)];me=bpy.data.meshes.new(name);me.from_pydata(v,[],f);o=bpy.data.objects.new(name,me);bpy.context.collection.objects.link(o);finish(o,name,'bronze');parts.append(o)
ear('upright_ear',[(.055,.20,1.035),(.16,.145,1.15),(.185,.24,1.04)])
ear('bent_ear',[(-.075,.20,1.06),(-.185,.20,1.07),(-.17,.26,1.01)])
bpy.ops.object.select_all(action='DESELECT')
for o in parts:o.select_set(True)
bpy.context.view_layer.objects.active=parts[0];bpy.ops.object.join();dog=bpy.context.object;dog.name='street_hachiko_dog'
m=dog.modifiers.new('continuous sculpt','REMESH');m.mode='VOXEL';m.voxel_size=.009;m.use_smooth_shade=True;bpy.ops.object.modifier_apply(modifier=m.name)
m=dog.modifiers.new('sculpt smoothing','SMOOTH');m.factor=.55;m.iterations=3;bpy.ops.object.modifier_apply(modifier=m.name)
m=dog.modifiers.new('web reduction','DECIMATE');m.ratio=.55;bpy.ops.object.modifier_apply(modifier=m.name)
for v in dog.data.vertices:
 p=v.co;v.co+=v.normal*(.0015*math.sin(p.x*170)*math.sin(p.y*140)*math.sin(p.z*160))
# Small anatomical details remain separate, not fused into an indistinct head.
ell('nose',(0,.465,.96),(.040,.023,.024),False,'dark')
for x in [-.12,.12]:ell('eye',(x,.34,1.00),(.014,.018,.011),False,'dark')
def curve(name,pts,width,mat):
 c=bpy.data.curves.new(name,'CURVE');c.dimensions='3D';c.bevel_depth=width;c.bevel_resolution=2;s=c.splines.new('POLY');s.points.add(len(pts)-1)
 for p,xyz in zip(s.points,pts):p.co=(*xyz,1)
 o=bpy.data.objects.new(name,c);bpy.context.collection.objects.link(o);o.data.materials.append(materials[mat]);bpy.context.view_layer.objects.active=o;o.select_set(True);dog.select_set(False);bpy.ops.object.convert(target='MESH');o=bpy.context.object;o.name='street_hachiko_'+name;o.select_set(False);return o
curve('mouth',[(-.075,.41,.921),(0,.455,.917),(.075,.41,.921)],.003,'dark')
curve('collar',[(.171*math.cos(i*math.tau/48),.12+.185*math.sin(i*math.tau/48),.70-.035*math.sin(i*math.tau/48)) for i in range(49)],.014,'bronze')
for x in [-.145,.145]:
 for dx in [-.022,.022]:curve('toe',[(x+dx,.305,.067),(x+dx,.335,.043)],.002,'dark')
# Scale the sculpture as one object family; the stone proportions stay independent.
for o in list(bpy.context.scene.objects):
 if o.type!='MESH':continue
 if o.name not in [plaque.name] and not any(o.name.startswith('street_hachiko_'+n) for n in ['foot','plinth','bronze_base','plaque_text']):
  for v in o.data.vertices:v.co*=D['dog_scale']
  o.location*=D['dog_scale'];o.location.z+=top+.09
 # Deterministic UV for procedural materials.
 bpy.context.view_layer.objects.active=o;bpy.ops.object.select_all(action='DESELECT');o.select_set(True);bpy.ops.object.mode_set(mode='EDIT');bpy.ops.mesh.select_all(action='SELECT');
 if o.name!='street_hachiko_plaque_text':bpy.ops.uv.smart_project(angle_limit=1.15,island_margin=.015)
 bpy.ops.object.mode_set(mode='OBJECT')
 o.rotation_euler.z+=angle;x,y=world(o.location.x,o.location.y);o.location.x=x;o.location.y=y;o.location.z+=anchor
 for p in o.data.polygons:p.use_smooth=o.name not in ['street_hachiko_foot','street_hachiko_plinth','street_hachiko_bronze_base','street_hachiko_plaque']
bpy.ops.object.empty_add();root=bpy.context.object;root.name='street_hachiko'
for o in list(bpy.context.scene.objects):
 if o!=root:o.parent=root
bpy.ops.export_scene.gltf(filepath=out,export_format='GLB',export_yup=True,export_materials='EXPORT')
Path(stats).write_text(json.dumps({'config':D,'anchor_tp':anchor+15,'contact_samples':samples,'max_burial_m':max(p['ground_z'] for p in samples)-anchor,'triangles':sum(len(p.vertices)-2 for o in bpy.context.scene.objects if o.type=='MESH' for p in o.data.polygons)},indent=1)+'\n')
