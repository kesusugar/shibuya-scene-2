"""B-stage west entrance block, PLATEAU shell + photo-read sections + separately exported January-2025 signs.
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
  tex=m.node_tree.nodes.new('ShaderNodeTexImage');tex.image=bpy.data.images.load(str(ROOT/'textures'/f'{texture}.png'));m.node_tree.links.new(tex.outputs['Color'],p.inputs['Base Color']);m.node_tree.links.new(tex.outputs['Color'],p.inputs['Emission Color']);p.inputs['Emission Strength'].default_value=1
 M[name]=m
for name,color in [('pharmacy',(.54,.52,.44)),('fruit',(.63,.61,.49)),('middle',(.44,.41,.34)),('corner',(.52,.035,.028))]:mat('west_wall_'+name,color)
mat('west_roof',(.33,.34,.32));mat('west_frame',(.30,.32,.29),.55,.4);mat('west_glass',(.09,.20,.16),.25,.28);mat('west_shop_glass',(.025,.06,.05),.15,.35);mat('west_awning',(.014,.19,.15));mat('west_shop_light',(.7,.63,.4));mat('west_screen_back',(.035,.035,.035),.3)
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
   if len(poly)>=3:face('west_wall_'+name,poly)
 else:face('west_roof',ring)
# Street-facing southern frontage follows the measured PLATEAU wall line; window dimensions are B-level estimates.
def south_y(x):return 21.279+(x+67.253)*(24.78-21.279)/(67.253-36.04)
angle=math.atan2(3.501,31.213);n=Vector((math.sin(angle),-math.cos(angle),0));t=Vector((math.cos(angle),math.sin(angle),0))
def panel(x,z,w,h,name,offset=.08,layer='base'):
 c=Vector((x,south_y(x),z))+n*offset
 pts=[c-t*w/2-Vector((0,0,h/2)),c+t*w/2-Vector((0,0,h/2)),c+t*w/2+Vector((0,0,h/2)),c-t*w/2+Vector((0,0,h/2))]
 face(name,pts,[(0,0),(1,0),(1,1),(0,1)],layer)
for sec,x0,x1,top in [('pharmacy',-67,-62,16.7),('fruit',-61.7,-48,20.8),('middle',-47.1,-40.8,20.8)]:
 for z in [5.0,8.8,12.6,16.4,20.0]:
  if z+1.2>top:continue
  for j in range(max(1,int((x1-x0)/1.7))):
   x=x0+.8+j*1.7;panel(x,z,1.48,2.3,'west_glass');panel(x,z-1.22,1.65,.13,'west_frame',.12)
 # visibly recessed ground shops and bright lintels, rather than another generic window tile.
 for j in range(max(1,int((x1-x0)/2.3))):
  x=x0+1.0+j*2.3;panel(x,1.55,1.9,2.55,'west_shop_glass',.12);panel(x,2.9,2.0,.17,'west_shop_light',.15)
for x in [-65,-60,-57,-54,-51,-45,-42]:
 box((x,south_y(x)-.5,3.0),(2.6,1.1,.12),'west_awning',angle)
# Red curved corner: roof height is kept below the PLATEAU main roof; dark display housings are geometry.
CX,CY,R=-38.25,27.8,3.9
start,end=map(math.radians,(-100,20))
def arc(name,z,w,h,layer='base',radius=R,center_angle=None):
 mid=(start+end)/2 if center_angle is None else center_angle;half=w/(2*radius)
 for i in range(24):
  a=mid-half+2*half*i/24;b=mid-half+2*half*(i+1)/24
  pts=[(CX+radius*math.cos(a),CY+radius*math.sin(a),z-h/2),(CX+radius*math.cos(b),CY+radius*math.sin(b),z-h/2),(CX+radius*math.cos(b),CY+radius*math.sin(b),z+h/2),(CX+radius*math.cos(a),CY+radius*math.sin(a),z+h/2)]
  face(name,pts,[(i/24,0),((i+1)/24,0),((i+1)/24,1),(i/24,1)],layer)
arc('west_wall_corner',13.8,8,27.6)
arc('west_screen_back',23.2,7.5,7.2,radius=R+.05);arc('west_screen_back',12.0,6.2,6.1,radius=R+.05)
arc('west_sign_rakuten',23.2,7.3,7.0,'signs',R+.09);arc('west_sign_dmm',12.0,6.0,5.9,'signs',R+.09)
arc('west_sign_taiseido',5.1,7.1,1.5,'signs',R+.10)
panel(-55,17.9,12.6,2.4,'west_sign_nishimura',.15,'signs');panel(-54.8,7.0,9.5,.75,'west_sign_fruit_band',.16,'signs');panel(-65.4,9.0,1.7,10.5,'west_sign_matsukiyo',.16,'signs');panel(-43.4,F.get('monja_center_height_m',15.4),2.5,11,'west_sign_monja',.16,'signs')
if F.get('monja_center_height_m',15.4)>21:
 for x in [-44.7,-42.1]:box((x,south_y(x)+.08,25.2),(.12,.12,11.4),'west_frame')
# Rooftop sign supported by an open steel frame, separate from the original roof mass.
B=Vector((-37.9,27.5,36.8));T=Vector((.7,.7,0)).normalized();N=Vector((T.y,-T.x,0))
W,H=8.6,9.1
pts=[B-T*W/2-Vector((0,0,H/2)),B+T*W/2-Vector((0,0,H/2)),B+T*W/2+Vector((0,0,H/2)),B-T*W/2+Vector((0,0,H/2))]
face('west_sign_hisamitsu',pts,[(0,0),(1,0),(1,1),(0,1)],'signs')
for u in [-W/2,0,W/2]:
 p=B+T*u-N*.18;box((p.x,p.y,35.5),(.13,.13,11.5),'west_frame')
for z in [31.0,34,37,40.5]:box((B.x-N.x*.18,B.y-N.y*.18,z),(W+.3,.13,.13),'west_frame',math.atan2(T.y,T.x))
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
stats={'source_id':D['id'],'plateau_id':D['plateau_id'],'plateau_ground_tp':D['ground_tp'],'anchor_tp':anchor,'pavement_max_tp':max(s['tp'] for s in samples),'roof_deviation_vs_plateau_m':anchor-D['ground_tp'],'frontage_samples':samples,'geometry':counts,'status':'B-stage, facade boundaries and dimensions approximate; January 2025 static ads'}
(ROOT/'data/stats.json').write_text(json.dumps(stats,indent=2)+'\n')
print('WEST',stats['anchor_tp'],counts)
