"""Blender 4.2.3 CLI: photo-informed planter wall, inclined silver rail and low pine-like shrubs."""
import bpy,bmesh,json,sys,math,random
from pathlib import Path
from mathutils import Vector
from mathutils.bvhtree import BVHTree
ROOT=Path(__file__).resolve().parents[1]
args=sys.argv[sys.argv.index('--')+1:] if '--' in sys.argv else []
OUT=Path(args[0]) if args else ROOT/'models'
OUT.mkdir(parents=True,exist_ok=True)
D=json.load(open(ROOT/'input/layout.json'))
H={'xy':[11.568175521259887,-48.68573220011713],'yaw_deg':35}
cx,cy=H['xy'];a=math.radians(H['yaw_deg']);rng=random.Random(73)
S=json.load(open(ROOT/'input/original_stats.json'))
POINTS={tuple(p['local']):p['ground_z'] for item in S['items'] for p in item['contact_samples']}
bpy.ops.wm.read_factory_settings(use_empty=True)
def world(x,y):return cx+x*math.cos(a)-y*math.sin(a),cy+x*math.sin(a)+y*math.cos(a)
def height(x,y):
 for (px,py),z in POINTS.items():
  if abs(px-x)<1e-7 and abs(py-y)<1e-7:return z
 raise ValueError('Missing pinned contact sample: '+str((x,y)))
mats={}
def mat(name,color,metal=0,rough=.9):
 m=bpy.data.materials.new('street_surround_'+name);m.use_nodes=True;b=m.node_tree.nodes['Principled BSDF'];b.inputs['Base Color'].default_value=(*color,1);b.inputs['Metallic'].default_value=metal;b.inputs['Roughness'].default_value=rough;mats[name]=m
for name,color,metal,rough in [('stone',(.14,.15,.14),0,.95),('joint',(.055,.065,.06),0,.97),('silver',(.55,.58,.60),.8,.32),('soil',(.07,.06,.04),0,1),('branch',(.11,.075,.04),0,.95),('needle',(.11,.17,.065),0,.92),('needle_light',(.19,.24,.08),0,.92),('rock',(.22,.19,.15),0,.95),('panel',(.065,.105,.10),.5,.88)]:mat(name,color,metal,rough)
mat('needle_deep',(.035,.068,.022),0,.86)
mat('needle_mid',(.075,.125,.035),0,.82)
# restrained saturation: material differences are local leaf variation, not a lighting change
mats['needle'].node_tree.nodes['Principled BSDF'].inputs['Base Color'].default_value=(.05,.095,.027,1)
mats['needle_light'].node_tree.nodes['Principled BSDF'].inputs['Base Color'].default_value=(.10,.155,.045,1)
objects=[];records=[];roots=[];leaf_vertices=[];leaf_faces=[];leaf_materials=[];leaf_uvs=[]
def finish(o,name,material):
 o.name='street_surround_'+name;o.data.materials.append(mats[material]);objects.append(o);return o
def box(name,loc,size,material,bevel=0):
 bpy.ops.mesh.primitive_cube_add(size=1,location=loc);o=bpy.context.object;o.scale=size;bpy.ops.object.transform_apply(location=False,rotation=False,scale=True)
 if bevel:
  m=o.modifiers.new('stone edge','BEVEL');m.width=bevel;m.segments=2;bpy.ops.object.modifier_apply(modifier=m.name)
 return finish(o,name,material)
def tube(name,p,q,r,material,vertices=12):
 p,q=Vector(p),Vector(q)
 if name.startswith('shrub'):
  bpy.ops.mesh.primitive_cone_add(vertices=8,radius1=r,radius2=r*.12,depth=(q-p).length,location=(p+q)/2)
 else:bpy.ops.mesh.primitive_cylinder_add(vertices=vertices,radius=r,depth=(q-p).length,location=(p+q)/2)
 o=bpy.context.object;o.rotation_euler=(q-p).to_track_quat('Z','Y').to_euler();return finish(o,name,material)
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
  srng=random.Random(6793+(0 if seg['id']=='left' else 100)+i)
  roots.append({'segment':seg['id'],'index':i,'local':[x,yy,bottom],'world':[*world(x,yy),bottom]})
  # Six fixed roots; asymmetric overlapping sprays rather than sphere-centered radial needles.
  # Lobe centers follow staggered branch growth, but no solid green core is generated.
  tube('shrub_trunk',(x,yy,bottom),(x+.018,yy+.005,bottom+.66),.013,'branch',12)
  phase=srng.uniform(0,math.tau)
  for j in range(6):
   ang=phase+j*2.39996323+srng.uniform(-.28,.28)
   reach=srng.uniform(.075,.135)*(1 if j<5 else .35)
   lift=.43+j*.09+srng.uniform(-.025,.025)
   center=Vector((x+math.cos(ang)*reach,yy+math.sin(ang)*reach*.62,bottom+lift))
   stem=Vector((x+.012,yy,bottom+lift*.65))
   tube('shrub_branch',stem,center,.007 if j<5 else .0055,'branch',6)
   # A coherent, curved branch spray. Nearby needles share a bearing but not a starburst center.
   for k in range(28):
    theta=srng.uniform(0,math.tau);radial=math.sqrt(srng.random())*.045
    shoot_base=center+Vector((math.cos(theta)*radial,math.sin(theta)*radial*.72,srng.uniform(-.035,.045)))
    heading=(ang+srng.uniform(-1.65,1.65)) if k%3 else srng.uniform(0,math.tau)
    direction=Vector((math.cos(heading),math.sin(heading),srng.uniform(.25,1.10))).normalized()
    drop=srng.uniform(.015,.06) if k%4 else srng.uniform(-.025,.01)
    length=srng.uniform(.14,.19);width=srng.uniform(.13,.18)
    side=direction.cross(Vector((0,0,1))).normalized()
    # Alternate cross-plane orientation so the same spray stays legible from above and below.
    from mathutils import Quaternion
    side=Quaternion(direction,srng.uniform(-1.2,1.2))@side
    n0=len(leaf_vertices);atlas=srng.randrange(4);col=atlas%2;row=atlas//2
    for u,tight in ((0,.22),(1/3,.60),(2/3,.92),(1,1)):
     p=shoot_base+direction*(length*u)+Vector((0,0,-drop*u*u))
     half=side*(width*tight/2)
     leaf_vertices.extend([tuple(p-half),tuple(p+half)])
     # PIL top-to-bottom atlas rows correspond to flipped UV rows.
     leaf_uvs.extend([((col+.5-.49*tight)/2,(1-row*.5)-.495+u*.49),((col+.5+.49*tight)/2,(1-row*.5)-.495+u*.49)])
    for m in range(3):
     b=n0+m*2
     leaf_faces.extend([(b,b+1,b+3),(b,b+3,b+2)]);leaf_materials.extend([0,0])
 for i in range(3):
  x=x0+.35+(x1-x0-.7)*i/2;yy=y-depth*.48
  bpy.ops.mesh.primitive_ico_sphere_add(subdivisions=2,radius=1,location=(x,yy,z+h+.06));o=bpy.context.object;o.scale=(rng.uniform(.30,.42),.24,rng.uniform(.28,.38));   # july094/095: boulders rise well above the cap
  for v in o.data.vertices:v.co*=rng.uniform(.86,1.12)
  for poly in o.data.polygons:poly.use_smooth=True
  finish(o,'rock','rock')
 records.append({'id':seg['id'],'contact_samples':contacts,'anchor_tp':z+15,'max_burial_m':max(p['ground_z'] for p in contacts)-z,'local_bounds':[x0,x1,y-depth,y+.155]})
# One masked leaf material = one glTF foliage primitive, with packed procedural RGBA atlas.
leafmat=mats['needle'];nodes=leafmat.node_tree.nodes;links=leafmat.node_tree.links
tex=nodes.new('ShaderNodeTexImage');tex.image=bpy.data.images.load(str(ROOT/'textures/needle_spray_atlas.png'));tex.image.pack();tex.interpolation='Linear'
bsdf=nodes['Principled BSDF'];links.new(tex.outputs['Color'],bsdf.inputs['Base Color'])
clip=nodes.new('ShaderNodeMath');clip.operation='ROUND';links.new(tex.outputs['Alpha'],clip.inputs[0]);links.new(clip.outputs[0],bsdf.inputs['Alpha'])
bsdf.inputs['Roughness'].default_value=.83;leafmat.use_backface_culling=False
me=bpy.data.meshes.new('curved_needle_sprays');me.from_pydata(leaf_vertices,[],leaf_faces);me.update()
o=bpy.data.objects.new('curved_needle_sprays',me);bpy.context.collection.objects.link(o);finish(o,'needles','needle')
uv=me.uv_layers.new(name='UVMap')
for poly in me.polygons:
 poly.use_smooth=True
 for li in poly.loop_indices:uv.data[li].uv=leaf_uvs[me.loops[li].vertex_index]
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
bpy.ops.wm.save_as_mainfile(filepath=str(OUT/'hachiko_surround_v002.blend'))
bpy.ops.export_scene.gltf(filepath=str(OUT/'hachiko_surround_v002.glb'),export_format='GLB',export_yup=True,export_materials='EXPORT')
(OUT/'after_stats.json').write_text(json.dumps({'config':D,'items':records,'triangles':sum(len(p.vertices)-2 for o in bpy.context.scene.objects if o.type=='MESH' for p in o.data.polygons)},indent=1)+'\n')


# Export vegetation only. Integrator must REMOVE old branch and needle nodes, never append atop them.
bpy.ops.object.select_all(action='DESELECT')
for ob in bpy.context.scene.objects:
 if ob.type=='MESH' and ('needle' in ob.name or ob.name=='street_surround_branch'):ob.select_set(True)
bpy.ops.export_scene.gltf(filepath=str(OUT/'hachiko_low_shrubs_only_v002.glb'),export_format='GLB',use_selection=True,export_yup=True,export_materials='EXPORT')
(OUT/'shrub_roots.json').write_text(json.dumps(roots,indent=2)+'\n')
