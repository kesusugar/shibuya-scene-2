"""Blender 4.2.3: individual, photo-type facades on unchanged PLATEAU 2025 shells.
-- source.json layout.json ground.glb webdir
Source rings already use T.P.-15; no global vertical translation.
"""
import bpy,bmesh,json,sys,math,zlib
from pathlib import Path
from mathutils import Vector
from mathutils.bvhtree import BVHTree
from mathutils.geometry import tessellate_polygon
source,layout,ground,output=sys.argv[sys.argv.index('--')+1:][:4];D=json.load(open(source));L=json.load(open(layout));OUT=Path(output);OUT.mkdir(parents=True,exist_ok=True);ID=L['id'];BASE=D['ground_tp']-15
bpy.ops.wm.read_factory_settings(use_empty=True);bpy.ops.import_scene.gltf(filepath=ground);
extra=sys.argv[sys.argv.index('--')+1:][4:]
for extension in extra:bpy.ops.import_scene.gltf(filepath=extension)
bm=bmesh.new()
for o in list(bpy.context.scene.objects):
 if o.name=='ground_fill' and any('exterior-' in path for path in extra):continue
 if o.type=='MESH' and o.name.startswith(('ground_road','ground_intersection','ground_sidewalk','ground_fill')):
  me=o.data.copy();me.transform(o.matrix_world);bm.from_mesh(me);bpy.data.meshes.remove(me)
bvh=BVHTree.FromBMesh(bm);bm.free()
for o in list(bpy.context.scene.objects):bpy.data.objects.remove(o,do_unlink=True)
M={};G={};samples=[];missing=0
for name,color,metal,rough in [('wall',L['wall_rgb'],0,.8),('roof',L.get('roof_rgb',[.3,.31,.3]),0,.95),('frame',L['frame_rgb'],.5,.45),('spandrel',L['spandrel_rgb'],.25,.7),('dark',[.018,.023,.025],0,.8),('sign_housing',[.03,.035,.04],.15,.6),('shop_glass',[.025,.045,.05],.3,.4)]:
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

shell=None;normal_flips=0;internal_walls=0
if L.get('probe_solid_normals'):
 sb=bmesh.new()
 for surface in D['surfaces']:
  rr=[Vector(p) for p in surface['ring']]
  if len(rr)>1 and (rr[0]-rr[-1]).length<1e-6:rr.pop()
  if len(rr)>2:
   try:sb.faces.new([sb.verts.new(p) for p in rr])
   except ValueError:pass
 shell=BVHTree.FromBMesh(sb);sb.free()
 def inside_shell(p):
  direction=Vector((.801,.307,.211)).normalized();q=p.copy();count=0
  for i in range(100):
   hit=shell.ray_cast(q,direction)[0]
   if hit is None:break
   count+=1;q=hit+direction*.0001
  return count%2==1
points=[Vector(p) for s in D['surfaces'] for p in s['ring']];centre=sum(points,Vector())/len(points);storey=(D['top_tp']-D['ground_tp'])/L['floors'];pitch=L['bay_pitch_m'];panels=0;facades=0
for si,s in enumerate(D['surfaces']):
 ring=[Vector(p) for p in s['ring']];n=normal(ring);face('wall' if s['kind']=='WallSurface' else 'roof',ring)
 if s['kind']!='WallSurface' or abs(n.z)>(.65 if L['style']=='parco' else .2) or n.length<.5:continue
 c=sum(ring,Vector())/len(ring)
 if n.dot(c-centre)<0:n=-n
 if shell:
  tris=tessellate_polygon([ring]);tris=[[ring[i] for i in tri] if isinstance(tri[0],int) else tri for tri in tris];probe=sum(max(tris,key=lambda tri:(tri[1]-tri[0]).cross(tri[2]-tri[0]).length),Vector())/3 if tris else c
  plus=inside_shell(probe+n*.22);minus=inside_shell(probe-n*.22)
  if plus and not minus:n=-n;normal_flips+=1
  elif plus and minus:internal_walls+=1;continue
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
  if L['style']=='hikarie' and row<5 and row>0:h=storey*.36
  columns=max(1,round((umax-umin)/pitch));actual_pitch=(umax-umin)/columns
  for col in range(columns):
   u=umin+(col+.5)*actual_pitch;w=(actual_pitch-.12)*L.get("bay_width_ratio",1)
   if L['style']=='hikarie' and 0<row<5:w*=.4
   if L['style'] in ['cylinder','retail'] and row>=L.get('podium_floors',2):
    if L['style']=='cylinder' and all(inside(u-w/2,localv+dy,poly) for dy in [-h/2,h/2]):panel(u-w/2,z,.02,h,'frame',.10)
    if L['style']=='retail' and all(inside(u+dx,localv+dy,poly) for dx in [-w/2,w/2] for dy in [-h/2,h/2]):panel(u,z,w,h*.8,'sign_housing',.09)
    continue
   if L['style']=='parco' and row>=L.get('podium_floors',2) and min(p.z for p in ring)<BASE+25:continue
   if not all(inside(u+dx,localv+dy,poly) for dx in [-w/2,w/2] for dy in [-h/2,h/2]):continue
   variant=(zlib.crc32((str(si)+':'+str(row)+':'+str(col)).encode())%3);panel(u,z,w,h,'glass'+str(variant));panels+=1
   # Thin physical mullions, with building-specific rhythm and podium infill.
   if L['style'] not in ['square','sakura']:panel(u,z,w,.055,'frame',.10)
   panel(u-w/2,z,.055,h,'frame',.105)
   if L['style']=='square' and (col+row//3)%5==0:panel(u-w/2+.12,z,.16,h,'dark',.11)
   if L['style']=='stream' and row>=6 and col%4==0 and (row//3+col//4)%3!=0:
    if all(inside(u+dx,localv+dy,poly) for dx in [-actual_pitch/2,actual_pitch/2] for dy in [-storey/2,storey/2]):panel(u,z,actual_pitch,storey+.01,'spandrel',.19)
   if L['style']=='fukuras' and (row+col)%4==0:panel(u,z-h*.25,w,h*.48,'spandrel',.12)
   if row<L.get('podium_floors',1):
    panel(u,BASE+3.35 if L['style']=='kiosk' else z-h*.35,w,.50,'sign_housing',.13)
  if all(inside(uu,localv,poly) for uu in [umin+.15,umax-.15]):
   band=L.get('band_m', .16 if L['style']=='square' else .32 if L['style']=='centre' else .24 if L['style']=='station' else .65)
   panel((umin+umax)/2,z-h/2-.08,umax-umin-.12,band,'spandrel',.12)
 if L['style']=='kiosk' and n.y>.5 and umax-umin>5:
  u=umin+1.5;z=BASE+1.15
  if all(inside(u+dx,(z-origin.z)/v.z+dy,poly) for dx in [-.5,.5] for dy in [-1.05,1.05]):
   panel(u,z,.95,2.1,'shop_glass',.15)
   for du in [-.5,.5]:panel(u+du,z,.06,2.18,'frame',.18)
   panel(u,BASE+2.23,1.06,.06,'frame',.18)
   panel(u+.34,BASE+1.05,.035,.18,'frame',.20)
 if L['style']=='sakura' and umax-umin>20 and max(p.z for p in ring)-min(p.z for p in ring)>60 and n.dot(Vector((6.5,-2,0))-c)>0:
  width=min(12,(umax-umin)*.24)
  for row in range(3,L['floors']-3,3):
   z0=BASE+row*storey;z1=z0+3*storey
   u0=umin+.25;u1=u0+width
   if not all(inside(uu,(zz-origin.z)/v.z,poly) for uu in [u0,u1] for zz in [z0,z1]):continue
   for aa,bb in [((u0,z0),(u1,z1)),((u1,z0),(u0,z1))]:
    pa=origin+t*aa[0]+v*((aa[1]-origin.z)/v.z)+n*.18;pb=origin+t*bb[0]+v*((bb[1]-origin.z)/v.z)+n*.18;side=n.cross(pb-pa).normalized()*.055;face('frame',[pa-side,pb-side,pb+side,pa+side])
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
if L.get('roof_sign'):
 cfg=L['roof_sign'];high=[p for surf in D['surfaces'] if surf['kind']=='RoofSurface' for p in map(Vector,surf['ring']) if p.z>D['top_tp']-15-.10]
 if len(high)>=3:
  rc=sum(high,Vector())/len(high);n=Vector((6.5-rc.x,-2-rc.y,0)).normalized();t=Vector((-n.y,n.x,0));up=Vector((0,0,1));w=min(cfg['width_m'],max((p-rc).dot(t) for p in high)-min((p-rc).dot(t) for p in high)-.5);h=cfg['height_m'];bottom=rc+up*cfg.get('base_offset_m',1)
  if w>1:
   corners=[bottom+t*u+up*v for u,v in [(-w/2,0),(w/2,0),(w/2,h),(-w/2,h)]]
   face('sign_housing',corners);face('sign_housing',[p-n*.20 for p in reversed(corners)])
   for i in range(4):
    a=corners[i];b=corners[(i+1)%4];side=n.cross(b-a).normalized()*.06;face('frame',[a-side,b-side,b+side,a+side]);face('frame',[a,b,b-n*.20,a-n*.20])
   for u in [-w*.4,w*.4]:
    a=rc+t*u;b=bottom+t*u+up*.2;side=t*.08;face('frame',[a-side,b-side,b+side,a+side])
if L.get('identity_109'):
 high=[p for surf in D['surfaces'] if surf['kind']=='RoofSurface' for p in map(Vector,surf['ring']) if p.z>D['top_tp']-15-.10]
 if len(high)>=3:
  rc=sum(high,Vector())/len(high);n=Vector((6.5-rc.x,-2-rc.y,0)).normalized();t=Vector((-n.y,n.x,0));radius=max((p-rc).dot(n) for p in high);scale=L.get('logo_scale_m',1.3);level=D['top_tp']-15-6.3
  def logo_point(x,y,depth):
   u=x*scale;return rc+t*u+n*(math.sqrt(max(.1,radius*radius-u*u))+.08+depth)+Vector((0,0,level+y*scale-rc.z))
  for name,color in [('logo_one',[.75,.14,.31]),('logo_zero',[.66,.09,.28]),('logo_nine',[.36,.075,.43])]:
   m=bpy.data.materials.new(ID+'_'+name);m.use_nodes=True;p=m.node_tree.nodes['Principled BSDF'];p.inputs['Base Color'].default_value=(*color,1);p.inputs['Roughness'].default_value=.75;M[name]=m
  def logo_polygon(name,ring):
   front=[logo_point(x,y,.07) for x,y in ring];back=[logo_point(x,y,0) for x,y in ring];face(name,front);face(name,list(reversed(back)))
   for i in range(len(ring)):j=(i+1)%len(ring);face(name,[back[i],back[j],front[j],front[i]])
  for name,x in [('logo_zero',-.3),('logo_nine',1.90)]:
   for i in range(48):
    a=i*math.tau/48;b=(i+1)*math.tau/48
    logo_polygon(name,[(x+math.cos(a)*1.18,.4+math.sin(a)*1.18),(x+math.cos(b)*1.18,.4+math.sin(b)*1.18),(x+math.cos(b)*.78,.4+math.sin(b)*.78),(x+math.cos(a)*.78,.4+math.sin(a)*.78)])
  logo_polygon('logo_one',[(-2.6,1.58),(-1.7,1.58),(-1.50,1.20),(-1.50,-.78),(-1.93,-.78),(-1.93,1.05),(-2.60,1.15)])
  logo_polygon('logo_nine',[(3.02,.5),(3.02,-.28),(2.90,-.86),(2.50,-1.34),(1.94,-1.65),(1.32,-1.66),(1.30,-1.25),(1.84,-1.23),(2.20,-.99),(2.51,-.64),(2.64,-.22),(2.64,.5)])
counts={}
for name,bm in G.items():
 bmesh.ops.triangulate(bm,faces=bm.faces[:]);me=bpy.data.meshes.new(ID+'_'+name);bm.to_mesh(me);bm.free();me.materials.append(M[name]);ob=bpy.data.objects.new(ID+'_'+name,me);bpy.context.collection.objects.link(ob);counts[name]=sum(len(p.vertices)-2 for p in me.polygons)
bpy.ops.export_scene.gltf(filepath=str(OUT/(ID+'.glb')),export_format='GLB',export_yup=True)
(OUT/'viewer.json').write_text(json.dumps({'groundElevationTP':15,'planBounds':[min(p.x for p in points),min(p.y for p in points),max(p.x for p in points),max(p.y for p in points)],'sun':{'azimuth_deg':207,'elevation_deg':57}},indent=1)+'\n')
for time in ['day','night']:(OUT/('emissive_'+time+'.json')).write_text('{}\n')
Path(layout).with_name('stats.json').write_text(json.dumps({'id':ID,'source_id':D['id'],'datum_tp_m':15,'source_ground_tp':D['ground_tp'],'source_top_tp':D['top_tp'],'roof_translation_m':0,'facades':facades,'solid_probe_normal_flips':normal_flips,'internal_wall_overlays_skipped':internal_walls,'glass_panels':panels,'triangles':sum(counts.values()),'primitives':len(counts),'pavement_samples':samples,'missing_pavement_samples':missing,'status':'individual facade prototype; counts/dimensions/2025 exterior not independently surveyed; no advertising imagery'},indent=1)+'\n')
print(ID,panels,'panels',sum(counts.values()),'triangles',len(samples),'ground hits',missing,'missing')
