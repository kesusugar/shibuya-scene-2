"""Western station viaduct B prototype; PLATEAU top retained, lower solid replaced by estimated piers/girders.
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
extra=sys.argv[sys.argv.index("--")+1:][4:]
for extension in extra:bpy.ops.import_scene.gltf(filepath=extension)
bm=bmesh.new()
for ob in list(bpy.context.scene.objects):
 if ob.type=='MESH' and ob.name.startswith(('ground_road','ground_sidewalk','ground_intersection','ground_fill')):
  me=ob.data.copy();me.transform(ob.matrix_world);bm.from_mesh(me);bpy.data.meshes.remove(me)
bvh=BVHTree.FromBMesh(bm);bm.free()
for ob in list(bpy.context.scene.objects):bpy.data.objects.remove(ob,do_unlink=True)
M={};GROUP={}
for name,rgb,rough,metal in [('wv_top',(.38,.41,.40),.9,0),('wv_concrete',(.66,.69,.65),.8,0),('wv_steel',(.50,.55,.53),.5,.45),('wv_rail',(.46,.53,.54),.45,.6),('wv_mesh',(.025,.18,.28),.9,0)]:
 m=bpy.data.materials.new(name);m.use_nodes=True;p=m.node_tree.nodes['Principled BSDF'];p.inputs['Base Color'].default_value=(*rgb,1);p.inputs['Roughness'].default_value=rough;p.inputs['Metallic'].default_value=metal;M[name]=m
if F['barrier_alpha']<1:
 M['wv_mesh'].node_tree.nodes['Principled BSDF'].inputs['Alpha'].default_value=F['barrier_alpha'];M['wv_mesh'].surface_render_method='DITHERED'
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
def above(poly,z):
 out=[]
 for a,b in zip(poly,poly[1:]+poly[:1]):
  ai=a.z>=z;bi=b.z>=z
  if ai:out.append(a)
  if ai!=bi:out.append(a.lerp(b,(z-a.z)/(b.z-a.z)))
 return out
A=Vector((*F['north_edge_xy_m'][0],0));B=Vector((*F['north_edge_xy_m'][1],0));T=(B-A).normalized();N=Vector((-T.y,T.x,0));L=(B-A).length;top=F['top_tp_m']-15;under=top-F['girder_depth_m'];mid=F['middle_beam_tp_m']-15;angle=math.atan2(T.y,T.x)
for part in D:
 for s in part['surfaces']:
  ring=[Vector(p) for p in s['ring']]
  if (ring[0]-ring[-1]).length<1e-6:ring=ring[:-1]
  if s['kind']=='RoofSurface':
   face('wv_top',ring);face('wv_concrete',[p-Vector((0,0,F['girder_depth_m'])) for p in reversed(ring)])
  else:
   upper=above(ring,under)
   if len(upper)>=3:face('wv_concrete',upper)
# Regular support layout follows the source strip, ground heights come from C2a.
samples=[];supports=[]
for i in range(F['support_count']):
 u=1.5+(L-3)*i/(F['support_count']-1);p=A+T*u-N*F['support_offset_m'];hit=bvh.ray_cast(Vector((p.x,p.y,50)),Vector((0,0,-1)))[0]
 g=hit.z if hit else F['fallback_ground_tp_m']-15;samples.append({'x':round(p.x,3),'y':round(p.y,3),'tp':round(g+15,4),'basis':('Core/DEM substrate ray' if extra else 'C2a ray') if hit else 'PLATEAU fallback'});supports.append((p,g))
 box((p.x,p.y,(mid+g)/2),(.42,.75,mid-g),'wv_steel',angle)
 for d in [-.26,.26]:
  q=p+T*d;box((q.x,q.y,(mid+g)/2),(.12,1.05,mid-g),'wv_steel',angle)
 box((p.x,p.y,(under+mid)/2),(1.1,1.3,under-mid),'wv_concrete',angle)
 box((p.x,p.y,under-.23),(2.3,3.7,.46),'wv_concrete',angle)
 bar(p-N*3+Vector((0,0,mid)),p+N*3+Vector((0,0,mid)),.42,.48,'wv_steel')
for offset in [1.4,7.0]:bar(A+T*1.5-N*offset+Vector((0,0,mid)),B-T*1.5-N*offset+Vector((0,0,mid)),.55,.60,'wv_concrete')
for (p,g),(q,h) in zip(supports,supports[1:]):
 bar(p+Vector((0,0,g+.5)),q+Vector((0,0,mid-.4)),.13,.13,'wv_steel')
 bar(q+Vector((0,0,h+.5)),p+Vector((0,0,mid-.4)),.13,.13,'wv_steel')
# Blue construction-edge net is a light transparent-panel approximation, not a photo texture.
for ends in [F['north_edge_xy_m'],F['south_edge_xy_m']]:
 a,b=[Vector((*p,top)) for p in ends];t=(b-a).normalized();l=(b-a).length;height=F['barrier_height_m']
 face('wv_mesh',[a+Vector((0,0,.12)),b+Vector((0,0,.12)),b+Vector((0,0,height)),a+Vector((0,0,height))])
 for dz in [.10,height]:bar(a+Vector((0,0,dz)),b+Vector((0,0,dz)),.045,.045,'wv_rail')
 for i in range(int(l/3)+1):
  p=a.lerp(b,i/int(l/3));box((p.x,p.y,p.z+height/2),(.055,.055,height),'wv_rail')
counts={}
for name,bm in GROUP.items():
 bmesh.ops.triangulate(bm,faces=bm.faces[:]);me=bpy.data.meshes.new(name);bm.to_mesh(me);bm.free();me.materials.append(M[name]);me.calc_loop_triangles();ob=bpy.data.objects.new(name,me);bpy.context.collection.objects.link(ob);counts[name]={'triangles':len(me.loop_triangles),'vertices':len(me.vertices)}
bpy.ops.export_scene.gltf(filepath=str(OUT/'station-west-viaduct.glb'),export_format='GLB',export_yup=True)
points=[p for b in D for s in b['surfaces'] for p in s['ring']]
(OUT/'viewer.json').write_text(json.dumps({'planBounds':[min(p[0] for p in points),min(p[1] for p in points),max(p[0] for p in points),max(p[1] for p in points)],'groundElevationTP':15},indent=2)+'\n')
for mode in ['day','night']:(OUT/f'emissive_{mode}.json').write_text('{}\n')
(ROOT/'stats.json').write_text(json.dumps({'source_ids':[p['id'] for p in D],'datum_tp_m':15,'roof_deviation_vs_plateau_m':0,'top_tp_m':F['top_tp_m'],'ground_samples':samples,'lower_closed_wall_faces_removed':sum(s['kind']=='WallSurface' for p in D for s in p['surfaces']),'objects':counts,'triangles':sum(v['triangles'] for v in counts.values()),'status':'B prototype. Association with October18 western/Ginza elevated structure inferred, not independent identity certification. Source upper surface retained; girder/pier/brace/barrier dimensions and positions estimated. No photo texture or generic windows.'},indent=2)+'\n')
print('STATION VIADUCT',sum(v['triangles'] for v in counts.values()),'ground',samples)
