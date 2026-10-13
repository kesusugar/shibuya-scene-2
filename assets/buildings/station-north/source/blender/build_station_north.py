"""North platform canopy B / unchanged southern station and JR viaduct geometry, common absolute datum.
blender -b --python-exit-code 1 -t 4 -P build_station_north.py -- parts.json layout.json ground.glb outdir
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
bvh=BVHTree.FromBMesh(bm);bm.free();samples=[]
for i in range(31):
 y=-20-i;p=Vector((53.8+.09*i,y,50));hit=bvh.ray_cast(p,Vector((0,0,-1)))[0]
 if hit:samples.append({'x':round(p.x,3),'y':y,'tp':round(hit.z+15,3)})
for ob in list(bpy.context.scene.objects):bpy.data.objects.remove(ob,do_unlink=True)
M={};GROUP={}
for name,rgb,rough,metal in [('stn_roof',(.37,.39,.37),.8,0),('stn_ceiling',(.58,.61,.58),.75,0),('stn_service_wall',(.62,.65,.62),.75,0),('stn_concrete',(.50,.53,.50),.8,0),('stn_deck',(.29,.31,.29),.9,0),('stn_steel',(.29,.33,.32),.4,.4),('stn_column',(.62,.65,.62),.6,.25),('stn_light',(.95,.92,.79),.45,0),('stn_tactile',(.9,.63,.035),.8,0)]:
 m=bpy.data.materials.new(name);m.use_nodes=True;p=m.node_tree.nodes['Principled BSDF'];p.inputs['Base Color'].default_value=(*rgb,1);p.inputs['Roughness'].default_value=rough;p.inputs['Metallic'].default_value=metal;M[name]=m

def face(name,pts):
 bm=GROUP.setdefault(name,bmesh.new());f=bm.faces.new([bm.verts.new(p) for p in pts]);f.normal_update()
def box(center,size,name):
 x,y,z=center;w,d,h=size;pts=[(x+a,y+b,z+c) for a,b,c in [(-w/2,-d/2,-h/2),(w/2,-d/2,-h/2),(w/2,d/2,-h/2),(-w/2,d/2,-h/2),(-w/2,-d/2,h/2),(w/2,-d/2,h/2),(w/2,d/2,h/2),(-w/2,d/2,h/2)]]
 for ids in [(0,3,2,1),(4,5,6,7),(0,1,5,4),(1,2,6,5),(2,3,7,6),(3,0,4,7)]:face(name,[pts[i] for i in ids])
def bar(a,b,width,depth,name):
 a,b=Vector(a),Vector(b);t=(b-a).normalized();n=t.cross(Vector((0,0,1)))
 if n.length<.001:n=t.cross(Vector((1,0,0)))
 n.normalize();v=t.cross(n).normalized();pts=[p+n*u+v*w for p in [a,b] for u,w in [(-width/2,-depth/2),(width/2,-depth/2),(width/2,depth/2),(-width/2,depth/2)]]
 for ids in [(0,3,2,1),(4,5,6,7),(0,1,5,4),(1,2,6,5),(2,3,7,6),(3,0,4,7)]:face(name,[pts[i] for i in ids])
def clip(poly,axis,boundary,positive):
 out=[]
 for a,b in zip(poly,poly[1:]+poly[:1]):
  ai=a[axis]>=boundary if positive else a[axis]<=boundary;bi=b[axis]>=boundary if positive else b[axis]<=boundary
  if ai:out.append(a)
  if ai!=bi:out.append(a.lerp(b,(boundary-a[axis])/(b[axis]-a[axis])))
 clean=[]
 for p in out:
  if not clean or (p-clean[-1]).length>1e-6:clean.append(p)
 if len(clean)>1 and (clean[0]-clean[-1]).length<1e-6:clean.pop()
 return clean
split=F['north_y_min_m'];deck=F['platform_deck_tp']-15;removed=0
for part in D:
 for surface in part['surfaces']:
  ring=[Vector(p) for p in surface['ring']]
  if (ring[0]-ring[-1]).length<.001:ring=ring[:-1]
  if part['kind']=='structure':
   # Original viaduct vertices and faces remain intact; it is a C-preserved part of this aggregate.
   face('stn_deck' if surface['kind']=='OuterFloorSurface' else 'stn_roof' if surface['kind']=='RoofSurface' else 'stn_concrete',ring);continue
  if surface['kind']=='RoofSurface':
   face('stn_roof',ring);face('stn_ceiling',[p-Vector((0,0,F['roof_thickness_m'])) for p in reversed(ring)])
  elif surface['kind']=='WallSurface':
   south=clip(ring,1,split,False);north=clip(ring,1,split,True);lower=clip(north,2,deck,False)
   if len(south)>=3:face('stn_service_wall',south)
   if len(lower)>=3:face('stn_concrete',lower)
   if len(north)>=3 and max(p.z for p in north)>deck:removed+=1
# Posts and crossbeams follow the northern narrow PLATEAU roof strip, dimensions are standard B estimates.
for y in F['support_rows_y_m']:
 x=58.0+(-y-24)*.09;top=11.60
 # H-section steel columns, not another solid wall/window grid.
 box((x,y,(deck+top)/2),(.16,.22,top-deck),'stn_column');box((x-.115,y,(deck+top)/2),(.07,.38,top-deck),'stn_column');box((x+.115,y,(deck+top)/2),(.07,.38,top-deck),'stn_column')
 bar((x-3.45,y,11.60),(x+3.15,y,11.60),.20,.28,'stn_steel')
 bar((x-2.3,y,11.6),(x,y,10.55),.08,.10,'stn_steel');bar((x,y,10.55),(x+2.3,y,11.6),.08,.10,'stn_steel')
 box((x-1.4,y,11.32),(1.3,.14,.06),'stn_light')
for offset in [-3.2,2.9]:bar((58+offset,-24,11.70),(60.16+offset,-48,11.70),.12,.14,'stn_steel')
# Visible tactile strip type is photo-confirmed; its exact lateral location is estimated.
# One aligned continuous band avoids the zigzag produced by unrotated one-metre boxes.
y0,y1=-23.0,-49.0
x0=58+(-y0-24)*.09+F['tactile_offset_m'];x1=58+(-y1-24)*.09+F['tactile_offset_m']
bar((x0,y0,deck+.035),(x1,y1,deck+.035),.35,.025,'stn_tactile')
counts={}
for name,bm in GROUP.items():
 bmesh.ops.triangulate(bm,faces=bm.faces[:]);me=bpy.data.meshes.new(name);bm.to_mesh(me);bm.free();me.materials.append(M[name]);me.calc_loop_triangles();ob=bpy.data.objects.new(name,me);bpy.context.collection.objects.link(ob);counts[name]={'triangles':len(me.loop_triangles),'vertices':len(me.vertices)}
bpy.ops.export_scene.gltf(filepath=str(OUT/'station-north.glb'),export_format='GLB',export_yup=True)
points=[p for b in D for s in b['surfaces'] for p in s['ring']]
(OUT/'viewer.json').write_text(json.dumps({'planBounds':[min(p[0] for p in points),min(p[1] for p in points),max(p[0] for p in points),max(p[1] for p in points)],'groundElevationTP':15},indent=2)+'\n')
for mode in ['day','night']:(OUT/f'emissive_{mode}.json').write_text(json.dumps({'stn_light':{'kind':'interior','emit':[1,.97,.86],'estr':.2 if mode=='day' else .8}},indent=2)+'\n')
(ROOT/'stats.json').write_text(json.dumps({'source_ids':[p['id'] for p in D],'north_open_wall_faces':removed,'platform_deck_tp':F['platform_deck_tp'],'datum_tp_m':15,'roof_deviation_vs_plateau_m':0,'ground_samples':samples,'objects':counts,'triangles':sum(v['triangles'] for v in counts.values()),'status':'North canopy B prototype; southern facility/whole original JR viaduct geometry preserved, not October facade certification. October GPS/photo/deck association is supporting evidence; post/beam/tactile positions estimated.'},indent=2)+'\n')
print('STATION NORTH',sum(v['triangles'] for v in counts.values()),'opened faces',removed)
