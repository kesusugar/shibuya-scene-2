"""B concourse/bridge replacement, original absolute PLATEAU datum; October structure reference, estimated dimensions."""
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
bvh=BVHTree.FromBMesh(bm);bm.free()
A=Vector((-44.855,-71.856,0));B=Vector((5.49,-65.663,0));T=(B-A).normalized();N=Vector((-T.y,T.x,0));L=(B-A).length
samples=[]
for i in range(81):
 p=A.lerp(B,i/80)+N*.5;hit=bvh.ray_cast(Vector((p.x,p.y,60)),Vector((0,0,-1)))[0]
 if hit:samples.append({'x':round(p.x,3),'y':round(p.y,3),'tp':round(hit.z+15,3)})
assert samples
for ob in list(bpy.context.scene.objects):bpy.data.objects.remove(ob,do_unlink=True)
M={};GROUP={}
for name,rgb,rough,metal in [('sc_wall',(.74,.76,.76),.45,.35),('sc_roof',(.32,.34,.32),.85,0),('sc_structure',(.73,.73,.70),.7,0),('sc_frame',(.55,.57,.57),.4,.45),('sc_glass',(.055,.12,.14),.28,.25),('sc_sheet',(.60,.64,.68),.9,0),('sc_safety_blue',(.025,.15,.25),.9,0),('sc_light',(.7,.65,.48),.5,0),('sc_interior',(.54,.52,.42),.8,0),('sc_interior_light',(.92,.89,.70),.6,0)]:
 m=bpy.data.materials.new(name);m.use_nodes=True;p=m.node_tree.nodes['Principled BSDF'];p.inputs['Base Color'].default_value=(*rgb,1);p.inputs['Roughness'].default_value=rough;p.inputs['Metallic'].default_value=metal;M[name]=m
# Shallow real window recesses: no photograph pasted on the facade.
M['sc_glass'].node_tree.nodes['Principled BSDF'].inputs['Alpha'].default_value=F['glass_alpha']
M['sc_glass'].surface_render_method='DITHERED'

def face(name,pts):
 bm=GROUP.setdefault(name,bmesh.new());f=bm.faces.new([bm.verts.new(p) for p in pts]);f.normal_update()
def box(center,size,name,angle=0):
 x,y,z=center;w,d,h=size;c,s=math.cos(angle),math.sin(angle)
 p=[(x+c*a-s*b,y+s*a+c*b,z+k) for a,b,k in [(-w/2,-d/2,-h/2),(w/2,-d/2,-h/2),(w/2,d/2,-h/2),(-w/2,d/2,-h/2),(-w/2,-d/2,h/2),(w/2,-d/2,h/2),(w/2,d/2,h/2),(-w/2,d/2,h/2)]]
 for ids in [(0,3,2,1),(4,5,6,7),(0,1,5,4),(1,2,6,5),(2,3,7,6),(3,0,4,7)]:face(name,[p[i] for i in ids])
def clip(poly,axis,boundary,right):
 out=[]
 for a,b in zip(poly,poly[1:]+poly[:1]):
  ai=a[axis]>=boundary if right else a[axis]<=boundary;bi=b[axis]>=boundary if right else b[axis]<=boundary
  if ai:out.append(a)
  if ai!=bi:out.append(a.lerp(b,(boundary-a[axis])/(b[axis]-a[axis])))
 clean=[]
 for p in out:
  if not clean or (p-clean[-1]).length>1e-6:clean.append(p)
 if len(clean)>1 and (clean[0]-clean[-1]).length<1e-6:clean.pop()
 return clean
floor=F['open_bay_floor_tp']-15;split=F['open_bay_x_min_m']
glass_z=F['glass_center_tp']-15;glass_bottom=glass_z-F['glass_height_m']/2;glass_top=glass_z+F['glass_height_m']/2
opened_glazing=0
for part in D:
 for surface in part['surfaces']:
  ring=[Vector(p) for p in surface['ring']]
  if (ring[0]-ring[-1]).length<.001:ring=ring[:-1]
  if part['kind']=='building':
   if surface['kind']=='WallSurface':
    west=clip(ring,0,split,False);east=clip(clip(ring,0,split,True),2,floor,True)
    for poly in [west,east]:
     if len(poly)<3:continue
     if max(abs((p-A).dot(N)) for p in poly)<.1:
      # Only cut the glass ribbon on the known north facade line, never the roof or lower bay.
      for rem in [clip(poly,2,glass_bottom,False),clip(poly,2,glass_top,True)]:
       if len(rem)>=3:face('sc_wall',rem)
      opened_glazing+=1
     else:face('sc_wall',poly)
   elif surface['kind']=='RoofSurface':face('sc_roof',ring)
  else:
   # Bridge LOD2 is also a solid wrapper, not actual columns. Keep its western part;
   # replace eastern lower walls with the estimated piers rather than closing the opening again.
   west=clip(ring,0,split,False)
   if len(west)>=3:face('sc_structure',west)
   if surface['kind']=='OuterFloorSurface':
    east=clip(ring,0,split,True)
    if len(east)>=3:face('sc_structure',east)
for triangle in F['open_bay_floor_triangles']:
 face('sc_structure',[(p[0],p[1],floor) for p in triangle])
# North glass band stays on the real PLATEAU wall line; dimensions/types are reference-based B estimates.
def panel(u,z,w,h,name,offset=.15):
 c=A+T*u+N*offset+Vector((0,0,z));face(name,[c-T*w/2-Vector((0,0,h/2)),c-T*w/2+Vector((0,0,h/2)),c+T*w/2+Vector((0,0,h/2)),c+T*w/2-Vector((0,0,h/2))])
# A shallow corridor box gives the glazing visible depth and a ceiling/floor.
depth=F['interior_depth_m']
panel(L/2,glass_z,L,F['glass_height_m'],'sc_interior',-depth)
for z in [glass_bottom,glass_top]:
 face('sc_interior',[A+N*.10+Vector((0,0,z)),B+N*.10+Vector((0,0,z)),B-N*depth+Vector((0,0,z)),A-N*depth+Vector((0,0,z))])
for p in [A,B]:
 face('sc_interior',[p+N*.10+Vector((0,0,glass_bottom)),p-N*depth+Vector((0,0,glass_bottom)),p-N*depth+Vector((0,0,glass_top)),p+N*.10+Vector((0,0,glass_top))])
for u in range(2,int(L),4):
 p=A+T*u-N*(depth/2)
 box((p.x,p.y,glass_top-.08),(2.6,.22,.055),'sc_interior_light',math.atan2(T.y,T.x))
# Visible interior columns use an estimated regular rhythm, not inferred exact positions.
for u in range(4,int(L),6):
 p=A+T*u-N*.40
 box((p.x,p.y,glass_z),(.12,.18,F['glass_height_m']),'sc_frame',math.atan2(T.y,T.x))
bays=F['window_bays']
for i in range(bays):panel((i+.5)*L/bays,F['glass_center_tp']-15,L/bays-.12,F['glass_height_m'],'sc_glass')
for i in range(bays+1):panel(i*L/bays,F['glass_center_tp']-15,.11,F['glass_height_m']+.3,'sc_frame',.19)
for z in [F['glass_center_tp']-15-F['glass_height_m']/2-.13,F['glass_center_tp']-15+F['glass_height_m']/2+.13]:panel(L/2,z,L,.22,'sc_frame',.19)
for relative_z in F['transom_offsets_m']:
 panel(L/2,glass_z+relative_z,L,.085,'sc_frame',.20)
# Silver fascia above the glazing (SC05): horizontal panel joints and a drip edge, no invented advertisement.
roof_z=max(p[2] for b in D if b['kind']=='building' for sf in b['surfaces'] if sf['kind']=='WallSurface' and max(abs((Vector(q)-A).dot(N)) for q in sf['ring'])<.1 for p in sf['ring'])   # top of the north wall
for z in [glass_top+.55+k*(roof_z-glass_top-.6)/3 for k in range(3)]:panel(L/2,z,L,.04,'sc_frame',.17)
panel(L/2,roof_z-.12,L+.2,.24,'sc_frame',.22)
# Lower silver band between the open soffit and the glazing, with the same joints.
for z in [floor+.9,floor+1.7]:panel(L/2,z,L,.035,'sc_frame',.17)
# A mid-height interior floor/slab edge read through the tall glazing (two-level concourse look in SC05; height estimated).
face('sc_interior',[A+N*.05+Vector((0,0,glass_bottom+4.4)),B+N*.05+Vector((0,0,glass_bottom+4.4)),B-N*depth+Vector((0,0,glass_bottom+4.4)),A-N*depth+Vector((0,0,glass_bottom+4.4))])
panel(L/2,glass_bottom+4.4,L,.35,'sc_frame',-.05)
# Make the lower beam explicit, leaving the opening below it rather than a solid wall.
u0=(split-A.x)/T.x
panel((u0+L)/2,floor+.25,L-u0,.5,'sc_structure',.3)
for u in [u0+1,u0+7,u0+13,L-1]:
 p=A+T*u+N*.45;hit=bvh.ray_cast(Vector((p.x,p.y,40)),Vector((0,0,-1)))[0]
 if hit:box((p.x,p.y,(hit.z+floor)/2),(.75,.75,floor-hit.z),'sc_structure')
# October reference confirms sheeted/scaffolded work around the elevated passage. Layout is explicitly estimated.
for u in [u0+2,u0+6,u0+10,u0+14,L-1]:
 p=A+T*u+N*.65;box((p.x,p.y,9.0),(.055,.055,6.0),'sc_frame')
for z in [6.25,7.25,9.25,11.25]:panel((u0+L)/2,z,L-u0,.045,'sc_frame',.7)
panel((u0+L)/2,6.7,L-u0,.7,'sc_safety_blue',.72)
panel((u0+L)/2,floor-.12,L-u0,.1,'sc_light',.33)
counts={}
for name,bm in GROUP.items():
 bmesh.ops.triangulate(bm,faces=bm.faces[:]);me=bpy.data.meshes.new(name);bm.to_mesh(me);bm.free();me.materials.append(M[name]);me.calc_loop_triangles();ob=bpy.data.objects.new(name,me);bpy.context.collection.objects.link(ob);counts[name]={'triangles':len(me.loop_triangles),'vertices':len(me.vertices)}
bpy.ops.export_scene.gltf(filepath=str(OUT/'station-concourse.glb'),export_format='GLB',export_yup=True)
points=[p for b in D for s in b['surfaces'] for p in s['ring']]
(OUT/'viewer.json').write_text(json.dumps({'planBounds':[min(p[0] for p in points),min(p[1] for p in points),max(p[0] for p in points),max(p[1] for p in points)],'groundElevationTP':15.0},indent=2)+'\n')
for mode in ['day','night']:
 (OUT/f'emissive_{mode}.json').write_text(json.dumps({'sc_glass':{'kind':'glass','emit':[0,0,0],'estr':0},'sc_light':{'kind':'interior','emit':[1,.9,.72],'estr':.24 if mode=='night' else 0},'sc_interior':{'kind':'interior','emit':[1,.95,.72],'estr':F['interior_night_strength'] if mode=='night' else 0},'sc_interior_light':{'kind':'interior','emit':[1,.96,.78],'estr':F['fixture_night_strength'] if mode=='night' else .15}},indent=2)+'\n')
(ROOT/'stats.json').write_text(json.dumps({'source_ids':[b['id'] for b in D],'datum_tp_m':15.0,'roof_deviation_vs_plateau_m':0,'opened_north_glazing_sections':opened_glazing,'interior_depth_m':depth,'ground_samples':samples,'ground_min_tp':min(p['tp'] for p in samples),'ground_max_tp':max(p['tp'] for p in samples),'open_bay_floor_tp':F['open_bay_floor_tp'],'open_bay_x_min_m':split,'objects':counts,'triangles':sum(row['triangles'] for row in counts.values()),'status':'B prototype. October10/18 north glazing/interior/transom types; October11 structural reference. Positions/dimensions/brightness estimated; western lower solid retained, four station candidates unconfirmed. No calibrated photographic pixel error.'},indent=2)+'\n')
print('CONCOURSE',sum(row['triangles'] for row in counts.values()),'ground',min(p['tp'] for p in samples),max(p['tp'] for p in samples))
