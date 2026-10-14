"""West-block photographic-fidelity revision; PLATEAU shell + inferred detailed facade + January-2025 signs.
blender -b --python-exit-code 1 -t 4 -P build_west.py -- plateau.json facades.json ground.glb outdir
"""
import bpy, bmesh, json, math, sys
from pathlib import Path
from mathutils import Vector
from mathutils.bvhtree import BVHTree
plateau, facade, ground, output = sys.argv[sys.argv.index('--')+1:][:4]
assert bpy.app.version == (4,2,3)
D=json.loads(Path(plateau).read_text());F=json.loads(Path(facade).read_text());OUT=Path(output);OUT.mkdir(parents=True,exist_ok=True)
ROOT=Path(facade).parent.parent
bpy.ops.wm.read_factory_settings(use_empty=True)
# Cached survey path reproduces the original 82 ground samples when the full ground GLB is unavailable.
if ground == 'cached':
 S=json.loads((ROOT/'data/ground_measurements.json').read_text());samples=S['frontage_samples'];anchor=S['anchor_tp'];BASE=D['ground_tp']-15
else:
 bpy.ops.import_scene.gltf(filepath=ground)
 bm=bmesh.new()
 for ob in list(bpy.context.scene.objects):
  if ob.type=='MESH' and ob.name.startswith(('ground_road','ground_intersection','ground_sidewalk','ground_fill')):
   me=ob.data.copy();me.transform(ob.matrix_world);bm.from_mesh(me);bpy.data.meshes.remove(me)
 bvh=BVHTree.FromBMesh(bm);bm.free()
 samples=[]
 for A,B in [((-67.253,21.279),(-36.04,24.78)),((-36.04,24.78),(-34.818,30.463))]:
  a,b=Vector(A),Vector(B);t=(b-a).normalized();n=Vector((t.y,-t.x))
  for i in range(41):
   p=a.lerp(b,i/40)+n*.4;hit=bvh.ray_cast(Vector((p.x,p.y,50)),Vector((0,0,-1)))[0]
   if hit:samples.append({'x':round(p.x,3),'y':round(p.y,3),'tp':round(hit.z+15,3)})
 assert samples,'No measured frontage ground'
 anchor=min(p['tp'] for p in samples);BASE=D['ground_tp']-15
 for ob in list(bpy.context.scene.objects):bpy.data.objects.remove(ob,do_unlink=True)
M={};GROUP={}
def mat(name,color,metal=0,rough=.65,texture=None):
 m=bpy.data.materials.new(name);m.use_nodes=True;p=m.node_tree.nodes['Principled BSDF'];p.inputs['Base Color'].default_value=(*color,1);p.inputs['Metallic'].default_value=metal;p.inputs['Roughness'].default_value=rough
 if texture:
  tex=m.node_tree.nodes.new('ShaderNodeTexImage');tex.image=bpy.data.images.load(str(ROOT/'textures'/f'{texture}.jpg'));m.node_tree.links.new(tex.outputs['Color'],p.inputs['Base Color']);m.node_tree.links.new(tex.outputs['Color'],p.inputs['Emission Color']);p.inputs['Emission Strength'].default_value=0
 M[name]=m
for name,color in [('pharmacy',(.54,.52,.44)),('fruit',(.63,.61,.49)),('middle',(.44,.41,.34)),('corner',(.52,.035,.028))]:mat('west_wall_'+name,color)
# Claude review 2026-10-14: the Daiseido corner body is grey metal cladding in Jan/Feb/Nov 2025 (WB01-03); only the
# narrow flank (クスリ) and its awning are red. The red is kept for those; the corner body gets its own material.
mat('west_wall_corner_body',(.50,.51,.50),.35,.45)
mat('west_roof',(.33,.34,.32));mat('west_frame',(.30,.32,.29),.55,.4);mat('west_glass',(.09,.20,.16),.25,.28);mat('west_shop_glass',(.025,.06,.05),.15,.35);mat('west_awning',(.014,.19,.15));mat('west_shop_light',(.7,.63,.4));mat('west_screen_back',(.035,.035,.035),.3)
mat('west_fruit_glass',(.30,.45,.38),.2,.38);mat('west_tile_trim',(.78,.77,.68));mat('west_recess',(.012,.022,.018));mat('west_pharmacy_awning',(.72,.47,.025));mat('west_book_awning',(.018,.22,.46))
for tex in F['textures']:mat('west_sign_'+tex,(1,1,1),0,.8,tex)
def face(name,pts,uv=None,layer='base'):
 bm=GROUP.setdefault((layer,name),bmesh.new());lay=bm.loops.layers.uv.verify() if uv else None
 f=bm.faces.new([bm.verts.new(p) for p in pts]);f.normal_update()
 if uv:
  for l,q in zip(f.loops,uv):l[lay].uv=q
def box(center,size,name,angle=0,layer='base'):
 x,y,z=center;w,d,h=size;c,s=math.cos(angle),math.sin(angle)
 pts=[Vector((x+c*a-s*b,y+s*a+c*b,z+k)) for a,b,k in [(-w/2,-d/2,-h/2),(w/2,-d/2,-h/2),(w/2,d/2,-h/2),(-w/2,d/2,-h/2),(-w/2,-d/2,h/2),(w/2,-d/2,h/2),(w/2,d/2,h/2),(-w/2,d/2,h/2)]]
 for ix in [(0,3,2,1),(4,5,6,7),(0,1,5,4),(1,2,6,5),(2,3,7,6),(3,0,4,7)]:face(name,[pts[i] for i in ix],layer=layer)
def section(x):return 'pharmacy' if x<-61.911 else 'fruit' if x<-47.347 else 'middle' if x<-40.561 else 'corner'
def clip_x(poly, boundary, keep_right):
 out=[]
 for a,b in zip(poly,poly[1:]+poly[:1]):
  ain=(a.x>=boundary) if keep_right else (a.x<=boundary)
  bin=(b.x>=boundary) if keep_right else (b.x<=boundary)
  if ain:out.append(a)
  if ain!=bin:out.append(a.lerp(b,(boundary-a.x)/(b.x-a.x)))
 clean=[]
 for p in out:
  if not clean or (p-clean[-1]).length>1e-6:clean.append(p)
 if len(clean)>1 and (clean[0]-clean[-1]).length<1e-6:clean.pop()
 return clean
for s in D['surfaces']:
 ring=[Vector((p[0],p[1],p[2]-BASE)) for p in s['ring']]
 if (ring[0]-ring[-1]).length<.001:ring=ring[:-1]
 if s['kind']=='WallSurface':
  for name,x0,x1 in [('pharmacy',-100,-61.911),('fruit',-61.911,-47.347),('middle',-47.347,-40.561),('corner',-40.561,100)]:
   poly=clip_x(clip_x(ring,x0,True),x1,False)
   # The coarse PLATEAU front/east corner planes would hide the B curved face.
   # Replace only these street-facing corner planes; keep rear walls and original roof.
   replaced=name=='corner' and len(poly)>=3 and max(p.y for p in poly)<31
   street_front = len(poly)>=3 and all(abs(p.y-(21.279+(p.x+67.253)*3.501/31.213))<.07 for p in poly)
   if len(poly)>=3 and not replaced and not street_front:face('west_wall_'+('corner_body' if name=='corner' else name),poly)
 else:face('west_roof',ring)
# Street-facing southern frontage follows the measured PLATEAU wall line; window dimensions are B-level estimates.
def south_y(x):return 21.279+(x+67.253)*(24.78-21.279)/(67.253-36.04)
angle=math.atan2(3.501,31.213);n=Vector((math.sin(angle),-math.cos(angle),0));t=Vector((math.cos(angle),math.sin(angle),0))
def panel(x,z,w,h,name,offset=.08,layer='base'):
 c=Vector((x,south_y(x),z))+n*offset
 pts=[c-t*w/2-Vector((0,0,h/2)),c+t*w/2-Vector((0,0,h/2)),c+t*w/2+Vector((0,0,h/2)),c-t*w/2+Vector((0,0,h/2))]
 face(name,pts,[(0,0),(1,0),(1,1),(0,1)],layer)
# Detailed street elevation is built as open bays, not laid over the removed PLATEAU plane.
exec(compile((Path(__file__).parent/'facade_fidelity.py').read_text(),str(Path(__file__).parent/'facade_fidelity.py'),'exec'))
# Red curved corner: roof height is kept below the PLATEAU main roof; dark display housings are geometry.
corner=F['corner'];CX,CY=corner['center_m'];R=corner['radius_m'];MID=corner['center_angle_rad']
start,end=map(math.radians,(-100,20))
def arc(name,z,w,h,layer='base',radius=R,center_angle=None):
 mid=MID if center_angle is None else center_angle;half=w/(2*radius)
 for i in range(24):
  a=mid-half+2*half*i/24;b=mid-half+2*half*(i+1)/24
  pts=[(CX+radius*math.cos(a),CY+radius*math.sin(a),z-h/2),(CX+radius*math.cos(b),CY+radius*math.sin(b),z-h/2),(CX+radius*math.cos(b),CY+radius*math.sin(b),z+h/2),(CX+radius*math.cos(a),CY+radius*math.sin(a),z+h/2)]
  face(name,pts,[(i/24,0),((i+1)/24,0),((i+1)/24,1),(i/24,1)],layer)
body=corner['body_height_m'];ws,hs=corner['width_scale'],corner['height_scale']
# Cut out true planar bookshop/DMM casings; curved body cannot remain in front of their facets.
for bottom,top in [(0,2.14),(3.86,4.49),(11.51,body)]:
 arc('west_wall_corner_body',(bottom+top)/2,8*ws,top-bottom)
# Horizontal louvres of the grey band between the Rakuten and DMM screens (WB01/WB02), drawn just proud of the body.
sc=corner['screen_centers_m'];lo=sc['dmm']+corner['dmm_height_m']/2+.15;hi=sc['rakuten']-corner['rakuten_height_m']/2-.15
z=lo
while z<hi:
 arc('west_frame',z,8*ws-.3,.06,radius=R+.04);z+=.45
# Claude review R2: the part above the Rakuten screen is a grey box (screen housing) in WB01-03, not the top of a
# cylinder. Two flat faces meet at the corner; the back is closed against the building. Height unchanged (to 27.98).
mat('west_housing',(.20,.21,.22),.4,.55)
half=8*ws/(2*R)
a0,a1=MID-half,MID+half
def on_arc(a,r):return Vector((CX+r*math.cos(a),CY+r*math.sin(a),0))
# corner point where the two flat faces meet, pulled in so the box stays within 1.0 m of the arc (not the far tangent apex)
cm=on_arc(corner.get("facet_apex_angle_rad",MID),R+1.0)
foot=[on_arc(a0,R+.15),cm,on_arc(a1,R+.15),on_arc(a1,R*.25),on_arc(a0,R*.25)]
zb,zt=body,corner.get('housing_top_m',27.98)
for p,q in zip(foot,foot[1:]+foot[:1]):face('west_housing',[Vector((p.x,p.y,zb)),Vector((q.x,q.y,zb)),Vector((q.x,q.y,zt)),Vector((p.x,p.y,zt))])
face('west_housing',[Vector((p.x,p.y,zt)) for p in foot]);face('west_housing',[Vector((p.x,p.y,zb)) for p in reversed(foot)])
for p,q in [(foot[0],foot[1]),(foot[1],foot[2])]:
 for z in (zb+.35,zt-.25):
  d=(q-p);n2=Vector((d.y,-d.x,0)).normalized()*.03
  face('west_frame',[Vector((p.x,p.y,z-.04))+n2,Vector((q.x,q.y,z-.04))+n2,Vector((q.x,q.y,z+.04))+n2,Vector((p.x,p.y,z+.04))+n2])
for name,z,w,h in [('rakuten',corner['screen_centers_m']['rakuten'],7.7,corner['rakuten_height_m']/hs)]:
 arc('west_screen_back',z,w*ws+.2,h*hs+.2,radius=R+.05)
 arc('west_sign_'+name,z,w*ws,h*hs,'signs',R+.10)
# DMM: a flat screen in a dark box frame on the corner (WB01-03 show a flat panel, unlike the curved Rakuten screen).
zd,wd,hd=corner['screen_centers_m']['dmm'],6*ws,corner['dmm_height_m']
# DMM has two distinct planar faces: dark left return and January image on the right plane.
# Split image at the photographed corner; do not stretch its dark photographed side over the front.
dleft=on_arc(MID-half,R+.12);dhinge=on_arc(corner.get("facet_apex_angle_rad",MID),R+.65);dright=on_arc(MID+half,R+.12)
for pa,pb,material,uv in [(dleft,dhinge,'west_screen_back',None),(dhinge,dright,'west_sign_dmm',[(0,0),(1,0),(1,1),(0,1)])]:
 pts=[pa+Vector((0,0,zd-hd/2)),pb+Vector((0,0,zd-hd/2)),pb+Vector((0,0,zd+hd/2)),pa+Vector((0,0,zd+hd/2))]
 face(material,pts,uv,'signs' if uv else 'base')
 for z in [zd-hd/2-.12,zd+hd/2+.12]:
  d=pb-pa;ang=math.atan2(d.y,d.x);q=(pa+pb)/2;box((q.x,q.y,z),(d.length+.16,.18,.18),'west_metal_edge',ang)
for zz in [zd-hd/2,zd+hd/2]:
 face('west_screen_back',[Vector((p.x,p.y,zz)) for p in [dleft,dhinge,dright,Vector((CX,CY,0))]])
for pp in [dleft,dhinge,dright]:box((pp.x,pp.y,zd),(.12,.12,hd+.4),'west_metal_edge')
flank=corner['flat_flank']
# Flat flank is independently visible in January and February; it follows the southern wall.
panel(flank['x_m'],flank['center_height_m'],flank['width_m'],flank['height_m'],'west_sign_asbi_flank',.2,'signs')
header=fruit['header'];panel(header['x_m'],header['center_height_m'],header['width_m'],header['height_m'],'west_sign_nishimura',.15,'signs');panel(-64.65,9.5,4.65,11.25,'west_sign_matsukiyo',.26,'signs');panel(F['monja_x_m'],F['monja_center_height_m'],F['monja_width_m'],F['monja_height_m'],'west_sign_monja',.16,'signs')
if F.get('monja_center_height_m',15.4)>21:
 for x in [-46.06,-42.94]:box((x,south_y(x)+.08,23.0),(.12,.12,10.2),'west_frame')
awning(flank['x_m'],flank['width_m'],'west_wall_corner',1.0)
# Bookshop blue awnings follow the two true corner planes below.
# Rooftop sign supported by an open steel frame, separate from the original roof mass.
roof=F['rooftop_sign'];B=Vector(roof['center_m']);yaw=roof['yaw_rad'];T=Vector((math.cos(yaw),math.sin(yaw),0));N=Vector((T.y,-T.x,0))
W,H=roof['width_m'],roof['height_m']
pts=[B-T*W/2-Vector((0,0,H/2)),B+T*W/2-Vector((0,0,H/2)),B+T*W/2+Vector((0,0,H/2)),B-T*W/2+Vector((0,0,H/2))]
face('west_sign_hisamitsu',pts,[(0,0),(1,0),(1,1),(0,1)],'signs')
# All supports follow the same sign transform, rather than retaining the old frame.
bottom=roof['support_base_height_m'];top=B.z+H/2+.15
for u in [-W/2,0,W/2]:
 p=B+T*u-N*.18;box((p.x,p.y,(bottom+top)/2),(.13,.13,top-bottom),'west_frame')
for z in [B.z-H/2,B.z,B.z+H/2]:box((B.x-N.x*.18,B.y-N.y*.18,z),(W+.3,.13,.13),'west_frame',yaw)
# Open lattice under the sign (WB01/WB03 show a braced steel frame, not three bare posts): a second post line 1.6 m
# behind, horizontal ties and X-bracing in both planes from the roof to the sign bottom. Member sizes estimated.
def strut(a,b,r=.05):
 d=b-a;mid=(a+b)/2;ang=math.atan2(d.y,d.x);hz=math.hypot(d.x,d.y);tilt=math.atan2(hz,d.z)
 bmx=GROUP.setdefault(('base','west_frame'),bmesh.new());m=bmesh.ops.create_cone(bmx,cap_ends=True,segments=6,radius1=r,radius2=r,depth=d.length)
 q=d.to_track_quat('Z','Y')
 for v in m['verts']:v.co.rotate(q);v.co+=mid
lo_z,hi_z=bottom,B.z-H/2
for depth in (-.18,-1.78):
 cols=[B+T*u+N*depth for u in (-W/2,0,W/2)]
 if depth<-1:
  for c in cols:box((c.x,c.y,(lo_z+B.z+H/2)/2),(.13,.13,B.z+H/2-lo_z),'west_frame')
 for a,b in zip(cols,cols[1:]):
  strut(Vector((a.x,a.y,lo_z)),Vector((b.x,b.y,hi_z)));strut(Vector((b.x,b.y,lo_z)),Vector((a.x,a.y,hi_z)))
for u in (-W/2,0,W/2):
 f=B+T*u-N*.18;r=B+T*u-N*1.78
 for z in (lo_z+.2,hi_z,B.z+H/2):strut(Vector((f.x,f.y,z)),Vector((r.x,r.y,z)),.045)
 strut(Vector((f.x,f.y,lo_z)),Vector((r.x,r.y,hi_z)),.04)
exec(compile((Path(__file__).parent/'corner_fidelity.py').read_text(),str(Path(__file__).parent/'corner_fidelity.py'),'exec'))
objects=[]
for (layer,name),bm in GROUP.items():
 bmesh.ops.triangulate(bm,faces=bm.faces[:]);me=bpy.data.meshes.new(name);bm.to_mesh(me);bm.free();me.materials.append(M[name]);me.calc_loop_triangles();ob=bpy.data.objects.new(name,me);bpy.context.collection.objects.link(ob);objects.append((layer,ob))
counts={}
for layer,file in [('base','west-block.glb'),('signs','signs-2025-01.glb')]:
 bpy.ops.object.select_all(action='DESELECT')
 for kind,ob in objects:ob.select_set(kind==layer)
 bpy.ops.export_scene.gltf(filepath=str(OUT/file),export_format='GLB',use_selection=True,export_yup=True)
 counts[layer]={'meshes':sum(k==layer for k,o in objects),'triangles':sum(len(o.data.loop_triangles) for k,o in objects if k==layer)}
pts=[p for s in D['surfaces'] for p in s['ring']]
hints={'planBounds':[min(p[0] for p in pts),min(p[1] for p in pts),max(p[0] for p in pts),max(p[1] for p in pts)],'sun':{'azimuth_deg':207,'elevation_deg':57},'groundElevationTP':anchor,'layers':{'signs':'signs-2025-01.glb'}}
(OUT/'viewer.json').write_text(json.dumps(hints,indent=2)+'\n')
for mode in ['day','night']:
 rows={name:{'kind':'led' if name.startswith('west_sign_') else 'interior','emit':[1,.85,.65],'estr':(1.2 if name in ['west_sign_rakuten','west_sign_dmm'] else .55 if name.startswith('west_sign_') else .4) if mode=='night' else 0} for name in M if name.startswith('west_sign_') or name in ['west_shop_light','west_shop_glass']}
 (OUT/f'emissive_{mode}.json').write_text(json.dumps(rows,indent=2)+'\n')
stats={'source_id':D['id'],'plateau_id':D['plateau_id'],'plateau_ground_tp':D['ground_tp'],'anchor_tp':anchor,'pavement_max_tp':max(s['tp'] for s in samples),'roof_deviation_vs_plateau_m':anchor-D['ground_tp'],'frontage_samples':samples,'geometry':counts,'status':'Photo-fidelity work in progress; facade and overhang dimensions inferred; original PLATEAU shell/ground anchor retained; January 2025 static ads'}
(ROOT/'data/stats.json').write_text(json.dumps(stats,indent=2)+'\n')
bpy.context.scene.unit_settings.system='METRIC'
bpy.context.scene.unit_settings.scale_length=1.0
bpy.ops.file.pack_all()
blend_path=OUT.parent/'source/blender/west-block.blend'
blend_path.parent.mkdir(parents=True,exist_ok=True)
bpy.ops.wm.save_as_mainfile(filepath=str(blend_path))
print('WEST',stats['anchor_tp'],counts)

