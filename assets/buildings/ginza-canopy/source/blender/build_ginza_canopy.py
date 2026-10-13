"""Ginza canopy upper-hall B prototype, original roof/upper deck retained; inferred sloping platform floor.
Blender4.2.3 -b --python-exit-code 1 -t 4 -P script -- parts.json layout.json ground.glb outdir
"""
import bpy,bmesh,json,math,sys
from pathlib import Path
from mathutils import Vector
from mathutils.bvhtree import BVHTree
src,config,ground,out=sys.argv[sys.argv.index('--')+1:][:4]
assert bpy.app.version==(4,2,3)
D=json.loads(Path(src).read_text());F=json.loads(Path(config).read_text());ROOT=Path(config).parent;OUT=Path(out);OUT.mkdir(parents=True,exist_ok=True)
bpy.ops.wm.read_factory_settings(use_empty=True);bpy.ops.import_scene.gltf(filepath=ground)
bm=bmesh.new()
for ob in list(bpy.context.scene.objects):
 if ob.type=='MESH' and ob.name.startswith(('ground_road','ground_sidewalk','ground_intersection','ground_fill')):
  me=ob.data.copy();me.transform(ob.matrix_world);bm.from_mesh(me);bpy.data.meshes.remove(me)
bvh=BVHTree.FromBMesh(bm);bm.free();ground_samples=[]
for xy in F['ground_query_xy_m']:
 hit=bvh.ray_cast(Vector((*xy,80)),Vector((0,0,-1)))[0];ground_samples.append({'x':xy[0],'y':xy[1],'tp':round(hit.z+15,4) if hit else None,'basis':'C2a ray' if hit else 'outside C2a; lower source base retained'})
for ob in list(bpy.context.scene.objects):bpy.data.objects.remove(ob,do_unlink=True)
M={};GROUP={}
for name,rgb,rough,metal in [('gc_roof',(.40,.44,.44),.8,0),('gc_ceiling',(.56,.60,.60),.8,0),('gc_base',(.55,.59,.57),.85,0),('gc_arch',(.84,.85,.82),.6,.15),('gc_floor',(.62,.63,.57),.7,0),('gc_bed',(.20,.23,.23),.9,0),('gc_tactile',(.91,.67,.035),.85,0),('gc_door',(.82,.85,.82),.5,.15),('gc_glass',(.30,.46,.46),.2,.1),('gc_rail',(.36,.42,.41),.4,.6),('gc_ceil_light',(.92,.93,.87),.5,0)]:
 m=bpy.data.materials.new(name);m.use_nodes=True;p=m.node_tree.nodes['Principled BSDF'];p.inputs['Base Color'].default_value=(*rgb,1);p.inputs['Roughness'].default_value=rough;p.inputs['Metallic'].default_value=metal;M[name]=m
M['gc_glass'].node_tree.nodes['Principled BSDF'].inputs['Alpha'].default_value=F['door_glass_alpha'];M['gc_glass'].surface_render_method='DITHERED'
def face(name,pts):
 pts=[Vector(p) for p in pts]
 if (pts[0]-pts[-1]).length<1e-6:pts=pts[:-1]
 bm=GROUP.setdefault(name,bmesh.new());f=bm.faces.new([bm.verts.new(p) for p in pts]);f.normal_update()
def box(center,size,name,angle=0):
 x,y,z=center;w,d,h=size;c,s=math.cos(angle),math.sin(angle)
 p=[(x+c*a-s*b,y+s*a+c*b,z+k) for a,b,k in [(-w/2,-d/2,-h/2),(w/2,-d/2,-h/2),(w/2,d/2,-h/2),(-w/2,d/2,-h/2),(-w/2,-d/2,h/2),(w/2,-d/2,h/2),(w/2,d/2,h/2),(-w/2,d/2,h/2)]]
 for ids in [(0,3,2,1),(4,5,6,7),(0,1,5,4),(1,2,6,5),(2,3,7,6),(3,0,4,7)]:face(name,[p[i] for i in ids])
def bar(a,b,width,depth,name):
 a,b=Vector(a),Vector(b);t=(b-a).normalized();n=t.cross(Vector((0,0,1)))
 if n.length<.001:n=t.cross(Vector((1,0,0)))
 n.normalize();v=t.cross(n).normalized();pts=[p+n*u+v*w for p in [a,b] for u,w in [(-width/2,-depth/2),(width/2,-depth/2),(width/2,depth/2),(-width/2,depth/2)]]
 for ids in [(0,3,2,1),(4,5,6,7),(0,1,5,4),(1,2,6,5),(2,3,7,6),(3,0,4,7)]:face(name,[pts[i] for i in ids])
A=Vector((*F['roof_axis_xy_m'][0],0));B=Vector((*F['roof_axis_xy_m'][1],0));T=(B-A).normalized();N=Vector((-T.y,T.x,0));L=(B-A).length;angle=math.atan2(T.y,T.x)
platform_width=F.get('platform_width_m',6.0);edges=[-6-platform_width/2,-6+platform_width/2]
def floor_z(u):return F['floor_west_tp_m']-15+(F['floor_east_tp_m']-F['floor_west_tp_m'])*u/L
def point(u,v,z):return A+T*u+N*v+Vector((0,0,z))
def below_bed(poly):
 def q(p):return p.z-(floor_z((p-A).dot(T))-F['platform_step_m'])
 out=[]
 for a,b in zip(poly,poly[1:]+poly[:1]):
  qa,qb=q(a),q(b);ai,bi=qa<=0,qb<=0
  if ai:out.append(a)
  if ai!=bi:out.append(a.lerp(b,qa/(qa-qb)))
 return out
opened=0
for part in D:
 for s in part['surfaces']:
  ring=[Vector(p) for p in s['ring']]
  if (ring[0]-ring[-1]).length<1e-6:ring=ring[:-1]
  if s['kind']=='RoofSurface':
   face('gc_roof',ring);face('gc_ceiling',[p-Vector((0,0,.15)) for p in reversed(ring)])
  else:
   lower=below_bed(ring)
   if len(lower)>=3:face('gc_base',lower)
   opened+=1
# Sloped deck and raised island floor interpolate nearby PLATEAU bridge surfaces; not a surveyed station floor.
for v0,v1,offset,mat in [(-17.7,6.1,-F['platform_step_m'],'gc_bed'),(edges[0],edges[1],0,'gc_floor')]:
 face(mat,[point(0,v0,floor_z(0)+offset),point(L,v0,floor_z(L)+offset),point(L,v1,floor_z(L)+offset),point(0,v1,floor_z(0)+offset)])
for v in edges:
 face('gc_base',[point(0,v,floor_z(0)-F['platform_step_m']),point(L,v,floor_z(L)-F['platform_step_m']),point(L,v,floor_z(L)),point(0,v,floor_z(0))])
for v in [edges[1]+F.get('rail_edge_offset_m',2.7),edges[0]-F.get('rail_edge_offset_m',2.7)]:
 for d in [-.7175,.7175]:bar(point(0,v+d,floor_z(0)-F['platform_step_m']+.10),point(L,v+d,floor_z(L)-F['platform_step_m']+.10),.07,.10,'gc_rail')
for v in [edges[0]+.5,edges[1]-.5]:
 face('gc_tactile',[point(0,v-.16,floor_z(0)+.012),point(L,v-.16,floor_z(L)+.012),point(L,v+.16,floor_z(L)+.012),point(0,v+.16,floor_z(0)+.012)])
# The exterior upper deck remains unchanged; M-profile ribs hang below it.
controls=[(6.1,15.50),(0,20.23),(-5.85,18.85),(-11.7,20.23),(-17.7,15.50)]
profile=[]
for j,((v0,z0),(v1,z1)) in enumerate(zip(controls,controls[1:])):
 for k in range(8):
  t=k/8;s=t if j in [0,3] else (1-math.cos(math.pi*t))/2;profile.append((v0+(v1-v0)*t,z0+(z1-z0)*s))
profile.append(controls[-1])
for i in range(F['rib_count']):
 u=L*i/(F['rib_count']-1)
 for (v0,z0),(v1,z1) in zip(profile,profile[1:]):bar(point(u,v0,z0-F.get('rib_drop_m',0)),point(u,v1,z1-F.get('rib_drop_m',0)),.20,.32,'gc_arch')
 for v,z in [profile[0],profile[-1]]:bar(point(u,v,floor_z(u)-F['platform_step_m']),point(u,v,z-F.get('rib_drop_m',0)),.18,.24,'gc_arch')
 for v in [-8,-4]:
  box(tuple(point(u,v,18.85-.25)),(2.1,.13,.055),'gc_ceil_light',angle)
# Closed static screen-door bays; no people, train, advertisement texture or operating simulation.
for v in edges:
 for i in range(F['door_bays']):
  u=(i+.5)*L/F['door_bays'];z=floor_z(u)
  for shift in [-.48,.48]:
   c=point(u+shift,v,z+.67);w=.92;h=1.05
   face('gc_glass',[c-T*w/2-Vector((0,0,h/2)),c-T*w/2+Vector((0,0,h/2)),c+T*w/2+Vector((0,0,h/2)),c+T*w/2-Vector((0,0,h/2))])
  for dz in [.13,1.22]:bar(point(u-.98,v,z+dz),point(u+.98,v,z+dz),.06,.07,'gc_door')
  for shift in [-.98,0,.98]:box(tuple(point(u+shift,v,z+.67)),(.06,.16,1.15),'gc_door',angle)
  housing_u=u+L/F['door_bays']/2 if F.get('continuous_housing',False) else u+1.42
  housing_width=L/F['door_bays']-2.04 if F.get('continuous_housing',False) else .75
  box(tuple(point(housing_u,v,z+.58)),(housing_width,.22,1.16),'gc_door',angle)
counts={}
for name,bm in GROUP.items():
 bmesh.ops.triangulate(bm,faces=bm.faces[:]);me=bpy.data.meshes.new(name);bm.to_mesh(me);bm.free();me.materials.append(M[name]);me.calc_loop_triangles();ob=bpy.data.objects.new(name,me);bpy.context.collection.objects.link(ob);counts[name]={'triangles':len(me.loop_triangles),'vertices':len(me.vertices)}
bpy.ops.export_scene.gltf(filepath=str(OUT/'ginza-canopy.glb'),export_format='GLB',export_yup=True)
points=[p for b in D for s in b['surfaces'] for p in s['ring']]
(OUT/'viewer.json').write_text(json.dumps({'planBounds':[min(p[0] for p in points),min(p[1] for p in points),max(p[0] for p in points),max(p[1] for p in points)],'groundElevationTP':15},indent=2)+'\n')
for mode in ['day','night']:(OUT/f'emissive_{mode}.json').write_text(json.dumps({'gc_glass':{'kind':'glass','emit':[0,0,0],'estr':0},'gc_ceil_light':{'kind':'interior','emit':[1,.98,.87],'estr':.15 if mode=='day' else .8}},indent=2)+'\n')
(ROOT/'stats.json').write_text(json.dumps({'source_ids':[p['id'] for p in D],'datum_tp_m':15,'roof_deviation_vs_plateau_m':0,'floor_reference_tp_m':[F['floor_west_tp_m'],F['floor_east_tp_m']],'floor_status':'nearby bridge levels interpolated, not measured platform floor','ground_queries':ground_samples,'lower_base_status':'original geometry below track bed retained as C, ground matching unconfirmed','platform_width_m':platform_width,'continuous_housing':F.get('continuous_housing',False),'rib_drop_m':F.get('rib_drop_m',0),'opened_upper_wall_faces':opened,'objects':counts,'triangles':sum(v['triangles'] for v in counts.values()),'status':'Partial B upper hall. Original roof/top deck preserved; M ribs/doors from dated auxiliary references, October interior independently unconfirmed. Floor/rib/door/track dimensions and positions estimated.'},indent=2)+'\n')
print('GINZA',sum(v['triangles'] for v in counts.values()),'ground',ground_samples)
