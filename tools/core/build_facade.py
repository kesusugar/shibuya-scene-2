"""Blender 4.2.3: individual, photo-type facades on unchanged PLATEAU 2025 shells.
-- source.json layout.json ground.glb webdir
Source rings already use T.P.-15; no global vertical translation.
"""
import bpy,bmesh,json,sys,math,zlib
from pathlib import Path
from mathutils import Vector
from mathutils.bvhtree import BVHTree
source,layout,ground,output=sys.argv[sys.argv.index('--')+1:][:4];D=json.load(open(source));L=json.load(open(layout));OUT=Path(output);OUT.mkdir(parents=True,exist_ok=True);ID=L['id'];BASE=D['ground_tp']-15
bpy.ops.wm.read_factory_settings(use_empty=True);bpy.ops.import_scene.gltf(filepath=ground);
extra=sys.argv[sys.argv.index('--')+1:][4:]
for extension in extra:bpy.ops.import_scene.gltf(filepath=extension)
bm=bmesh.new()
for o in list(bpy.context.scene.objects):
 if o.type=='MESH' and o.name.startswith(('ground_road','ground_intersection','ground_sidewalk','ground_fill')):
  me=o.data.copy();me.transform(o.matrix_world);bm.from_mesh(me);bpy.data.meshes.remove(me)
bvh=BVHTree.FromBMesh(bm);bm.free()
for o in list(bpy.context.scene.objects):bpy.data.objects.remove(o,do_unlink=True)
M={};G={};samples=[];missing=0
for name,color,metal,rough in [('wall',L['wall_rgb'],0,.8),('roof',[.3,.31,.3],0,.95),('frame',L['frame_rgb'],.5,.45),('spandrel',L['spandrel_rgb'],.25,.7),('dark',[.018,.023,.025],0,.8),('sign_housing',[.03,.035,.04],.15,.6),('shop_glass',[.025,.045,.05],.3,.4)]:
 m=bpy.data.materials.new(ID+'_'+name);m.use_nodes=True;p=m.node_tree.nodes['Principled BSDF'];p.inputs['Base Color'].default_value=(*color,1);p.inputs['Metallic'].default_value=metal;p.inputs['Roughness'].default_value=rough;M[name]=m
for i,factor in enumerate([.93,1,1.05]):
 m=bpy.data.materials.new(ID+'_glass_'+str(i));m.use_nodes=True;p=m.node_tree.nodes['Principled BSDF'];p.inputs['Base Color'].default_value=(*(min(1,v*factor) for v in L['glass_rgb']),1);p.inputs['Metallic'].default_value=.3;p.inputs['Roughness'].default_value=.28;M['glass'+str(i)]=m

def face(name,points):
 bm=G.setdefault(name,bmesh.new());ps=[Vector(p) for p in points]
 if len(ps)>1 and (ps[0]-ps[-1]).length<1e-6:ps.pop()
 if len(ps)<3:return
 try:bm.faces.new([bm.verts.new(p) for p in ps])
 except ValueError:pass

def normal(ring):
 n=Vector((0,0,0))
 for i,p in enumerate(ring):
  q=ring[i-1];n.x+=(p.y-q.y)*(p.z+q.z);n.y+=(p.z-q.z)*(p.x+q.x);n.z+=(p.x-q.x)*(p.y+q.y)
 return n.normalized() if n.length else n

def inside(u,v,poly):
 ok=False
 for i,p in enumerate(poly):
  q=poly[i-1]
  if (p[1]>v)!=(q[1]>v) and u<(q[0]-p[0])*(v-p[1])/(q[1]-p[1])+p[0]:ok=not ok
 return ok

points=[Vector(p) for s in D['surfaces'] for p in s['ring']];centre=sum(points,Vector())/len(points);storey=(D['top_tp']-D['ground_tp'])/L['floors'];pitch=L['bay_pitch_m'];panels=0;facades=0
for si,s in enumerate(D['surfaces']):
 ring=[Vector(p) for p in s['ring']];n=normal(ring);face('wall' if s['kind']=='WallSurface' else 'roof',ring)
 if s['kind']!='WallSurface' or abs(n.z)>.2 or n.length<.5:continue
 c=sum(ring,Vector())/len(ring)
 if n.dot(c-centre)<0:n=-n
 t=Vector((-n.y,n.x,0)).normalized();v=n.cross(t).normalized()
 if v.z<0:v=-v
 origin=ring[0];poly=[((p-origin).dot(t),(p-origin).dot(v)) for p in ring];umin=min(p[0] for p in poly);umax=max(p[0] for p in poly)
 if umax-umin<.7:continue
 facades+=1
 def panel(u,z,w,h,name,depth=.075):
  p=origin+t*u+v*((z-origin.z)/v.z)+n*depth
  face(name,[p-t*w/2-v*h/2,p+t*w/2-v*h/2,p+t*w/2+v*h/2,p-t*w/2+v*h/2])
 for row in range(L['floors']):
  z=BASE+(row+.5)*storey;localv=(z-origin.z)/v.z;h=storey*L.get('glass_height_ratio',.78)
  if L['style']=='kiosk':z=BASE+1.85;localv=(z-origin.z)/v.z;h=2.6
  columns=max(1,round((umax-umin)/pitch));actual_pitch=(umax-umin)/columns
  for col in range(columns):
   u=umin+(col+.5)*actual_pitch;w=(actual_pitch-.12)*L.get("bay_width_ratio",1)
   if not all(inside(u+dx,localv+dy,poly) for dx in [-w/2,w/2] for dy in [-h/2,h/2]):continue
   variant=(zlib.crc32((str(si)+':'+str(row)+':'+str(col)).encode())%3);panel(u,z,w,h,'glass'+str(variant));panels+=1
   # Thin physical mullions, with building-specific rhythm and podium infill.
   if L['style']!='square':panel(u,z,w,.055,'frame',.10)
   panel(u-w/2,z,.055,h,'frame',.105)
   if L['style']=='square' and (col+row//3)%5==0:panel(u-w/2+.12,z,.16,h,'dark',.11)
   if L['style']=='fukuras' and (row+col)%4==0:panel(u,z-h*.25,w,h*.48,'spandrel',.12)
   if row<L.get('podium_floors',1):
    panel(u,BASE+3.35 if L['style']=='kiosk' else z-h*.35,w,.50,'sign_housing',.13)
  if all(inside(uu,localv,poly) for uu in [umin+.15,umax-.15]):
   band= .16 if L['style']=='square' else .32 if L['style']=='centre' else .24 if L['style']=='station' else .65
   panel((umin+umax)/2,z-h/2-.08,umax-umin-.12,band,'spandrel',.12)
 if L['style']=='kiosk' and n.y>.5 and umax-umin>5:
  u=umin+1.5;z=BASE+1.15
  if all(inside(u+dx,(z-origin.z)/v.z+dy,poly) for dx in [-.5,.5] for dy in [-1.05,1.05]):
   panel(u,z,.95,2.1,'shop_glass',.15)
   for du in [-.5,.5]:panel(u+du,z,.06,2.18,'frame',.18)
   panel(u,BASE+2.23,1.06,.06,'frame',.18)
   panel(u+.34,BASE+1.05,.035,.18,'frame',.20)
 # Follow actual diagonal source boundaries rather than inventing rectangular cut-outs.
 if L['style']=='square':
  for i,p in enumerate(ring):
   q=ring[i-1]
   if abs(p.z-q.z)>5 and math.hypot(p.x-q.x,p.y-q.y)>2:
    d=(q-p).normalized();side=n.cross(d).normalized()*.06;face('frame',[p+n*.10-side,q+n*.10-side,q+n*.10+side,p+n*.10+side])
 # Skirts follow available finished pavement, leaving roof coordinates intact.
 low=min(p.z for p in ring)
 if low<BASE+.4:
  for i,p in enumerate(ring):
   q=ring[i-1]
   if abs(p.z-low)>.2 or abs(q.z-low)>.2 or (p-q).length<.8:continue
   segment=[]
   for k in range(9):
    pt=p.lerp(q,k/8)+n*.22;hit=bvh.ray_cast(Vector((pt.x,pt.y,50)),Vector((0,0,-1)))
    if hit[0] is None:missing+=1;segment.append(None)
    else:samples.append({'xy':[pt.x,pt.y],'tp':hit[0].z+15});segment.append(hit[0].z-.02)
   for k in range(8):
    if segment[k] is None or segment[k+1] is None:continue
    p0=p.lerp(q,k/8)+n*.02;p1=p.lerp(q,(k+1)/8)+n*.02
    face('wall',[(p0.x,p0.y,BASE+.05),(p1.x,p1.y,BASE+.05),(p1.x,p1.y,min(BASE,segment[k+1])),(p0.x,p0.y,min(BASE,segment[k]))])
counts={}
for name,bm in G.items():
 bmesh.ops.triangulate(bm,faces=bm.faces[:]);me=bpy.data.meshes.new(ID+'_'+name);bm.to_mesh(me);bm.free();me.materials.append(M[name]);ob=bpy.data.objects.new(ID+'_'+name,me);bpy.context.collection.objects.link(ob);counts[name]=sum(len(p.vertices)-2 for p in me.polygons)
bpy.ops.export_scene.gltf(filepath=str(OUT/(ID+'.glb')),export_format='GLB',export_yup=True)
(OUT/'viewer.json').write_text(json.dumps({'groundElevationTP':15,'planBounds':[min(p.x for p in points),min(p.y for p in points),max(p.x for p in points),max(p.y for p in points)],'sun':{'azimuth_deg':207,'elevation_deg':57}},indent=1)+'\n')
for time in ['day','night']:(OUT/('emissive_'+time+'.json')).write_text('{}\n')
Path(layout).with_name('stats.json').write_text(json.dumps({'id':ID,'source_id':D['id'],'datum_tp_m':15,'source_ground_tp':D['ground_tp'],'source_top_tp':D['top_tp'],'roof_translation_m':0,'facades':facades,'glass_panels':panels,'triangles':sum(counts.values()),'primitives':len(counts),'pavement_samples':samples,'missing_pavement_samples':missing,'status':'individual facade prototype; counts/dimensions/2025 exterior not independently surveyed; no advertising imagery'},indent=1)+'\n')
print(ID,panels,'panels',sum(counts.values()),'triangles',len(samples),'ground hits',missing,'missing')
