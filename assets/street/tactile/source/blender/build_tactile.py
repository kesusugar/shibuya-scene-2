"""Blender 4.2.3: build local crossing tactile approaches on existing sidewalk.
blender -b -P build_tactile.py -- layout.json crossings.json street_input.json ground.glb output.glb stats.json
"""
import bpy,bmesh,json,sys,math
from pathlib import Path
from mathutils import Vector
from mathutils.bvhtree import BVHTree
sys.path.insert(0,str(Path(__file__).resolve().parents[4]/"ground/core/source/blender"))
from paving_boundary import partition
layout,crossings,street,ground,output,stats=sys.argv[sys.argv.index('--')+1:][:6]
P=json.load(open(Path(street).with_name('street_layout.json')))['items']
D=json.load(open(layout));C=json.load(open(crossings))['crosswalks'];F=json.load(open(street))['features']
bpy.ops.wm.read_factory_settings(use_empty=True);bpy.ops.import_scene.gltf(filepath=ground)
bm=bmesh.new()
for ob in list(bpy.context.scene.objects):
 if ob.type=='MESH' and ob.name.startswith('ground_sidewalk'):
  me=ob.data.copy();me.transform(ob.matrix_world);bm.from_mesh(me);bpy.data.meshes.remove(me)
bvh=BVHTree.FromBMesh(bm);bm.free()
for ob in list(bpy.context.scene.objects):bpy.data.objects.remove(ob,do_unlink=True)
def pavement(x,y):
 hit=bvh.ray_cast(Vector((x,y,50)),Vector((0,0,-1)))
 return hit[0].z if hit[0] is not None else None

def inside(x,y,ring):
 result=False
 for i,p in enumerate(ring):
  q=ring[i-1];x1,y1=p[:2];x2,y2=q[:2]
  if (y1>y)!=(y2>y) and x<(x2-x1)*(y-y1)/(y2-y1)+x1:result=not result
 return result

def clear(x,y):
 for f in F:
  if f['kind']=='entrance' and inside(x,y,f['ring']):return False
  if f['kind']=='tree' and math.hypot(x-f['point'][0],y-f['point'][1])<.7:return False
 return pavement(x,y) is not None

verts=[];faces=[];records=[];tiles=[];samples=[];clip_mask=None;route_records=[]
def polygon(points):
 pieces=[points] if clip_mask is None else [piece for piece,covered in partition(points,clip_mask) if not covered]
 for piece in pieces:
  vs=[]
  for x,y,dz in piece:
   z=pavement(x,y)
   if z is None:raise ValueError('tile relief outside sidewalk')
   samples.append({'x':x,'y':y,'ground_z':z,'offset':dz})
   vs.append(len(verts));verts.append((x,y,z+dz))
  faces.append(vs)

def tile(cx,cy,d,kind,group):
 # Local X across the route, local Y along it. No overlapping warning and guide tiles.
 face_start=len(faces)
 ux,uy=d[1],-d[0];vx,vy=d
 def point(x,y,z):return (cx+ux*x+vx*y,cy+uy*x+vy*y,z)
 half=D['tile_m']/2-.0015;base=D['base_offset_m'];top=base+D['relief_m']
 polygon([point(-half,-half,base),point(half,-half,base),point(half,half,base),point(-half,half,base)])
 if kind=='warning':
  for ix in range(5):
   for iy in range(5):
    x=(ix-2)*.06;y=(iy-2)*.06
    for k in range(8):
     a=k*math.tau/8;b=(k+1)*math.tau/8;r=D['dot_base_radius_m'];rt=D['dot_top_radius_m']
     polygon([point(x+math.cos(a)*r,y+math.sin(a)*r,base),point(x+math.cos(b)*r,y+math.sin(b)*r,base),point(x+math.cos(b)*rt,y+math.sin(b)*rt,top),point(x+math.cos(a)*rt,y+math.sin(a)*rt,top)])
     polygon([point(x,y,top),point(x+math.cos(a)*rt,y+math.sin(a)*rt,top),point(x+math.cos(b)*rt,y+math.sin(b)*rt,top)])
 else:
  for ix in range(4):
   x=(ix-1.5)*.06
   lower=[point(x-.0135,-.14,base),point(x+.0135,-.14,base),point(x+.0135,.14,base),point(x-.0135,.14,base)]
   upper=[point(x-.0085,-.135,top),point(x+.0085,-.135,top),point(x+.0085,.135,top),point(x-.0085,.135,top)]
   polygon(upper)
   for k in range(4):polygon([lower[k],lower[(k+1)%4],upper[(k+1)%4],upper[k]])
 if len(faces)==face_start:return
 tiles.append({'group':group,'kind':kind,'centre_xy':[cx,cy],'direction_xy':list(d)})

def tile_clear(cx,cy,d):
 ux,uy=d[1],-d[0]
 for obj in P:
  if 'xy' not in obj:continue
  dx,dy=obj['xy'][0]-cx,obj['xy'][1]-cy
  across=abs(dx*ux+dy*uy);along=abs(dx*d[0]+dy*d[1])
  if math.hypot(max(across-.15,0),max(along-.15,0))<D['pole_clearance_m']:return False
 return all(clear(cx+ux*x+d[0]*y,cy+uy*x+d[1]*y) for x in [-.15,0,.15] for y in [-.15,0,.15])

for c in C:
 if c['id'] not in D['crosswalk_ids']:continue
 for end in [0,-1]:
  p=c['points'][end];q=c['points'][1 if end==0 else -2];dx=p[0]-q[0];dy=p[1]-q[1];length=math.hypot(dx,dy);d=(dx/length,dy/length);ux,uy=d[1],-d[0]
  group=c['id']+('/start' if end==0 else '/end');chosen=None
  for step in range(int((D['maximum_search_m']-D['minimum_setback_m'])/.15)+1):
   setback=D['minimum_setback_m']+step*.15;cx=p[0]+d[0]*setback;cy=p[1]+d[1]*setback
   warning=[(cx+ux*a+d[0]*b,cy+uy*a+d[1]*b) for a in [-.15,.15] for b in [-.15,.15]]
   if all(tile_clear(x,y,d) for x,y in warning):chosen=(cx,cy,setback,warning);break
  if chosen is None:
   records.append({'id':group,'status':'no complete warning pad fits sidewalk'});continue
  cx,cy,setback,warning=chosen
  for x,y in warning:tile(x,y,d,'warning',group)
  guides=0
  for k in range(D['guide_tiles']):
   x=cx+d[0]*(.45+k*.3);y=cy+d[1]*(.45+k*.3)
   if not tile_clear(x,y,d):break
   tile(x,y,d,'guide',group);guides+=1
  records.append({'id':group,'status':'prototype','centre_xy':[cx,cy],'setback_from_measured_endpoint_m':setback,'guide_tiles':guides})
# Extend only the two plaza approaches, keeping the original 60 tiles unchanged.
if D.get('plaza_links'):
 links=D['plaza_links'];anchors=[]
 for group in links['approaches']:
  record=next(r for r in records if r['id']==group)
  direction=next(t['direction_xy'] for t in tiles if t['group']==group)
  anchors.append((Vector(record['centre_xy']),Vector(direction)))
 p0,d0=anchors[0];p1,d1=anchors[1]
 cross=lambda a,b:a.x*b.y-a.y*b.x
 denominator=cross(d0,d1)
 if abs(denominator)<1e-6:raise ValueError('parallel approach axes need explicit junction')
 distance0=cross(p1-p0,d1)/denominator
 distance1=cross(p1-p0,d0)/denominator
 if min(distance0,distance1)<=2.1:raise ValueError('junction overlaps original approaches')
 junction=p0+d0*distance0;south=(d0+d1).normalized();across=Vector((south.y,-south.x))
 count=links['junction_tiles'];half=count*D['tile_m']/2
 for i in range(count):
  for j in range(count):
   centre=junction+across*((i-(count-1)/2)*.3)+south*((j-(count-1)/2)*.3)
   if not tile_clear(centre.x,centre.y,south):raise ValueError('junction blocked')
   tile(centre.x,centre.y,south,'warning','plaza-junction')
 # Cut both the base and ribs away from the junction, so the surfaces never overlap.
 clip_mask=[tuple(junction+across*x+south*y) for x,y in [(-half,-half),(half,-half),(half,half),(-half,half)]]
 for group,(point,direction),length in zip(links['approaches'],anchors,[distance0,distance1]):
  start=len(tiles)
  for i in range(math.ceil((length-2.1)/.3)):
   centre=point+direction*(2.25+i*.3)
   if not tile_clear(centre.x,centre.y,direction):raise ValueError('connecting approach blocked: '+group)
   tile(centre.x,centre.y,direction,'guide','plaza-link:'+group)
  route_records.append({'id':'plaza-link:'+group,'from':group,'to':'plaza-junction','length_from_warning_centre_m':length,'rendered_tiles':len(tiles)-start})
 clip_mask=None
 start=len(tiles)
 for i in range(round(links['south_length_m']/.3)):
  centre=junction+south*(half+.15+i*.3)
  if not tile_clear(centre.x,centre.y,south):raise ValueError('south continuation blocked')
  tile(centre.x,centre.y,south,'guide','plaza-south-continuation')
 route_records.append({'id':'plaza-south-continuation','from':'plaza-junction','to':'unverified continuation endpoint','length_m':links['south_length_m'],'rendered_tiles':len(tiles)-start,'end_xy':list(junction+south*(half+links['south_length_m']))})
 junction_record={'centre_xy':list(junction),'direction_xy':list(south),'tiles':count*count,'polygon_xy':clip_mask if clip_mask else [list(junction+across*x+south*y) for x,y in [(-half,-half),(half,-half),(half,half),(-half,half)]]}
else:junction_record=None

me=bpy.data.meshes.new('street_tactile');me.from_pydata(verts,[],faces);me.update()
ob=bpy.data.objects.new('street_tactile',me);bpy.context.collection.objects.link(ob)
mat=bpy.data.materials.new('street_tactile_yellow');mat.use_nodes=True;bsdf=mat.node_tree.nodes['Principled BSDF'];bsdf.inputs['Base Color'].default_value=(*D['yellow_linear_rgb'],1);bsdf.inputs['Roughness'].default_value=.9;me.materials.append(mat)
bpy.ops.export_scene.gltf(filepath=output,export_format='GLB',export_yup=True,export_normals=True,export_materials='EXPORT')
Path(stats).write_text(json.dumps({'config':D,'groups':records,'routes':route_records,'junction':junction_record,'tiles':tiles,'contact_check':{'count':len(samples),'missing':0,'min_offset_m':min(p['offset'] for p in samples),'max_offset_m':max(p['offset'] for p in samples)},'contact_samples':samples[::max(1,len(samples)//120)],'triangles':sum(len(f)-2 for f in faces),'vertices':len(verts)},indent=1)+'\n')
print('TACTILE',len(tiles),'tiles',len(records),'approaches',sum(len(f)-2 for f in faces),'triangles')
