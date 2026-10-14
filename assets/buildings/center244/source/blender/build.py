"""Center244 photo-derived architecture, Blender 4.2.3 only.
No network or dependencies. Run without arguments. Coordinates: metres, X east, Y north,
Z = TP - 15 m; origin lat 35.6595 lon 139.7005. Raw PLATEAU is read-only.
"""
import bpy, bmesh, json, math, hashlib
from pathlib import Path
from mathutils import Vector
assert bpy.app.version == (4,2,3), bpy.app.version_string
ROOT=Path(__file__).resolve().parents[2]; S=ROOT/'source'; OUT=ROOT/'web'; OUT.mkdir(exist_ok=True)
D=json.loads((S/'data/plateau.json').read_text()); OLD=json.loads((S/'data/recorded_ground.json').read_text())
bpy.ops.wm.read_factory_settings(use_empty=True)
M={};G={};UV={};ERA=set();LOG=[]
def mat(n,c,metal=0,rough=.7):
 m=bpy.data.materials.new('c244_'+n);m.use_nodes=True;p=m.node_tree.nodes['Principled BSDF'];p.inputs['Base Color'].default_value=(*c,1);p.inputs['Metallic'].default_value=metal;p.inputs['Roughness'].default_value=rough;M[n]=m
for n,c,metal,r in [('stone',(.61,.58,.49),0,.79),('stone_light',(.62,.59,.50),0,.79),('stone_dark',(.60,.57,.48),0,.82),('joint',(.27,.27,.24),0,.85),('roof',(.33,.35,.33),0,.8),('frame',(.37,.43,.42),.55,.35),('reveal',(.055,.07,.068),.1,.7),('glass',(.17,.30,.28),.25,.3),('blind',(.43,.56,.48),.1,.75),('glass_dark',(.045,.075,.068),.25,.33),('gold',(.54,.35,.09),.55,.4),('gold_glass',(.57,.40,.14),.15,.37),('steel',(.32,.38,.35),.65,.42),('screen_back',(.08,.12,.10),.15,.7),('lamp',(.64,.66,.59),.2,.4)]:mat(n,c,metal,r)
def face(n,pts,uv=None):
 pts=[tuple(p) for p in pts]
 if len(pts)>1 and pts[0]==pts[-1]:pts.pop()
 if len(pts)<3:return
 v,f=G.setdefault(n,([],[]));j=len(v);v.extend(pts);f.append(tuple(range(j,j+len(pts))));UV.setdefault(n,[]).append(uv)
def beam(n,a,b,w,d=None):
 a,b=Vector(a),Vector(b);z=(b-a).normalized();x=z.cross(Vector((0,0,1)))
 if x.length<.01:x=z.cross(Vector((1,0,0)))
 x.normalize();y=z.cross(x).normalized();d=d or w
 p=[a-x*w/2-y*d/2,a+x*w/2-y*d/2,a+x*w/2+y*d/2,a-x*w/2+y*d/2,b-x*w/2-y*d/2,b+x*w/2-y*d/2,b+x*w/2+y*d/2,b-x*w/2+y*d/2]
 for f in [(0,3,2,1),(4,5,6,7),(0,1,5,4),(1,2,6,5),(2,3,7,6),(3,0,4,7)]:face(n,[p[i] for i in f])
def frame(a,b):
 a=Vector((*a,0));b=Vector((*b,0));t=(b-a).normalized();n=Vector((t.y,-t.x,0));return a,b,t,n,(b-a).length
def P(f,u,z,o=0):return f[0]+f[2]*u+Vector((0,0,z))+f[3]*o
def rect(n,f,u0,u1,z0,z1,o=0,uv=None):face(n,[P(f,u0,z0,o),P(f,u1,z0,o),P(f,u1,z1,o),P(f,u0,z1,o)],uv)
def line(n,f,u0,z0,u1,z1,w=.04,o=.04):beam(n,P(f,u0,z0,o),P(f,u1,z1,o),w)
# Front faceting uses source edges, not a rectangular replacement box.
F={16:frame((-73.141,71.297),(-69.497,70.742)),18:frame((-69.497,70.742),(-66.643,72.26)),31:frame((-66.643,72.26),(-62.747,79.701)),30:frame((-72.261,73.937),(-73.141,71.297))}
# Exact photographic ratios, not uniform 9-floor division; all heights inferred except shell roof.
OPEN={
16:[(.16,.91,1.72,4.30,'shop'),(.22,.94,7.6,10.05,'window'),(.20,.94,10.7,12.8,'window'),(.18,.94,13.6,16.10,'window'),(.56,.86,18.7,19.8,'small')],
18:[(.14,.92,1.72,4.30,'shop'),(.14,.92,4.75,7.20,'blank'),(.14,.92,7.55,10.05,'window'),(.14,.92,10.70,12.80,'window'),(.14,.92,13.60,16.10,'window'),(.27,.76,16.75,21.55,'fan_strip')],
31:[(.08,.90,1.72,4.30,'shop'),(.12,.77,7.55,10.05,'window'),(.12,.77,10.70,13.05,'window'),(.12,.77,13.85,16.10,'window'),(.86,.95,18.60,19.65,'small'),(.84,.96,11.15,12.25,'small')],
30:[(.18,.88,1.72,4.25,'shop'),(.18,.88,7.6,10.05,'window'),(.18,.88,10.7,12.8,'window'),(.18,.88,13.6,16.1,'window')]}
# Keep all low original roof faces. Tall solid is classified explicitly below.
UPPER={1,3,4,5,7,14,27,32,33,25,26}
for i,s in enumerate(D['surfaces']):
 if i in F or (i in UPPER and i not in [25,26]):continue
 ring=s['ring']
 if i in [17,29,25,26]:
  # Retain unseen rear wall below parapet. Upper presentation is braced envelope, not invented rooms.
  def clip(poly,z):
   out=[]
   for a,b in zip(poly,poly[1:]+poly[:1]):
    ia=a[2]<=z;ib=b[2]<=z
    if ia:out.append(a)
    if ia!=ib:
     t=(z-a[2])/(b[2]-a[2]);out.append([a[k]+t*(b[k]-a[k]) for k in range(3)])
   return out
  ring=clip(ring[:-1],21.635)
 face('roof' if s['kind']=='RoofSurface' else 'stone_dark',ring)
# Wall tessellation at all opening edges ensures true holes, with recessed glass and solid reveals.
for si,f in F.items():
 W=f[4];opens=[(a*W,b*W,c,d,k) for a,b,c,d,k in OPEN[si]]
 us=sorted(set([0,W]+[j*W/max(1,round(W/.76)) for j in range(1,round(W/.76))]+[v for a,b,c,d,k in opens for v in [a,b]]))
 zs=sorted(set([1.59,21.635]+[1.59+j*.87 for j in range(1,24) if 1.59+j*.87<21.635]+[v for a,b,c,d,k in opens for v in [c,d]]))
 for ui,(a,b) in enumerate(zip(us,us[1:])):
  for zi,(c,d) in enumerate(zip(zs,zs[1:])):
   if any(x<(a+b)/2<y and z<(c+d)/2<t for x,y,z,t,k in opens):continue
   rect('joint',f,a,b,c,d,-.018)
   tu=int((a+b)/2/(W/round(W/.76)));tz=int(((c+d)/2-1.59)/.87)
   n=['stone','stone','stone_light','stone','stone_dark'][(tu*13+tz*7+si)%5]
   du=lambda x: .007 if abs(x/(W/round(W/.76))-round(x/(W/round(W/.76))))<1e-5 else 0
   dz=lambda x: .007 if abs((x-1.59)/.87-round((x-1.59)/.87))<1e-5 else 0
   rect(n,f,a+du(a),b-du(b),c+dz(c),d-dz(d),0)
 for oi,(a,b,c,d,k) in enumerate(opens):
  depth=.16 if k!='shop' else .28
  for aa,bb,cc,dd in [(a,b,c,c),(a,b,d,d),(a,a,c,d),(b,b,c,d)]:
   if aa==bb:face('stone_dark',[P(f,aa,cc),P(f,aa,dd),P(f,aa,dd,-depth),P(f,aa,cc,-depth)])
   else:face('stone_dark',[P(f,aa,cc),P(f,bb,dd),P(f,bb,dd,-depth),P(f,aa,cc,-depth)])
  rect('reveal',f,a,b,c,d,-depth-.02)
  n='glass_dark' if k in ['shop','small'] else 'glass' if k=='fan_strip' else 'blind' if si==31 and oi>=3 else 'glass'
  if k=='blank':n='stone_light'
  rect(n,f,a+.045,b-.045,c+.045,d-.045,-depth)
  for x in [a+.035,b-.035]:line('frame',f,x,c,x,d,.045,-depth+.025)
  for z in [c+.035,d-.035]:line('frame',f,a,z,b,z,.045,-depth+.025)
  if k in ['window','shop']:
   count=max(2,round((b-a)/1.1))
   for j in range(1,count):line('frame',f,a+(b-a)*j/count,c,a+(b-a)*j/count,d,.045,-depth+.025)
   line('frame',f,a,c+(d-c)*.30,b,c+(d-c)*.30,.045,-depth+.025)
   if k=='window' and si==31:
    # Narrow left operable pane, broad irregular rest of glazing; no repetitive 1.8m bay grid.
    line('frame',f,a+.48,c,a+.48,d,.06,-depth+.025)
    for j in range(1,17):rect('blind',f,a+.52,b-.07,c+.12+j*(d-c-.25)/17,c+.132+j*(d-c-.25)/17,-depth+.004)
  if k=='fan_strip':
   for j in range(1,8):line('frame',f,a,c+j*(d-c)/8,b,c+j*(d-c)/8,.045,-depth+.03)
 # Dark horizontal crown separator and lower brass trims wrap coherently across facets.
 rect('reveal',f,0,W,16.32,16.55,.035)
 for z in [4.38,4.49,4.65]:rect('gold',f,0,W,z,z+.045,.04)
 line('frame',f,0,21.635,W,21.635,.055,.015)
# Gold radial fan and concentric ribs, centered over chamfer strip. Not an ad.
f=F[18];mid=f[4]*.515;rad=f[4]*.245;base=21.635
for i in range(24):
 a=i*math.pi/24;b=(i+1)*math.pi/24
 face('gold_glass',[P(f,mid,base,.02),P(f,mid+rad*math.cos(a),base+rad*math.sin(a),.02),P(f,mid+rad*math.cos(b),base+rad*math.sin(b),.02)])
 for rr in [rad,rad*.50]:beam('frame',P(f,mid+rr*math.cos(a),base+rr*math.sin(a),.05),P(f,mid+rr*math.cos(b),base+rr*math.sin(b),.05),.035)
for i in range(7):
 a=i*math.pi/6;beam('frame',P(f,mid,base,.05),P(f,mid+rad*math.cos(a),base+rad*math.sin(a),.05),.04)
# Billboard framework matches the upper source envelope; no occupied glass bands.
# Envelope corners and top remain exact; internal braces and board lower edge are photograph-inferred.
C=[Vector((-73.685,76.844,20.153)),Vector((-69.767,75.027,20.153)),Vector((-65.264,80.842,20.153)),Vector((-70.622,83.268,20.153))]
for i,a in enumerate(C):
 b=C[(i+1)%4]
 for z in [21.635,24.4,27.6,31.2,34.783]:beam('steel',(a.x,a.y,z),(b.x,b.y,z),.12)
 for u in [0,.5,1]:
  p=a.lerp(b,u);beam('steel',(p.x,p.y,20.153),(p.x,p.y,34.783),.12)
 for z0,z1 in [(21.635,24.4),(24.4,27.6),(27.6,31.2),(31.2,34.78)]:
  for u0,u1 in [(0,.5),(.5,1)]:
   p=a.lerp(b,u0);q=a.lerp(b,u1);beam('steel',(p.x,p.y,z0),(q.x,q.y,z1),.065)
# Display front aligned with upper east source wall26, inset .10 m to retain plan envelope.
B=frame((-69.767,75.027),(-65.264,80.842));W=B[4]
rect('screen_back',B,-1.55,W+.15,25.1,34.843,.10)
for u in [-1.52,W+.12]:line('frame',B,u,25.1,u,34.843,.07,.14)
for z in [25.1,34.80]:line('frame',B,-1.55,z,W+.15,z,.07,.14)
# Five braces and floodlight housings below sign, visible in Jan photograph.
for j in range(5):
 u=.35+j*(W-.7)/4
 beam('steel',P(B,u,21.70,-1.2),P(B,u,25.10,-.12),.10)
 beam('steel',P(B,u,23.65,-.15),P(B,u,23.65,.48),.07)
 rect('lamp',B,u-.18,u+.18,23.64,23.86,.48)
# Low equipment and guard rails inside lower roof, never blanket-filled to billboard height.
for edge in [F[16],F[31]]:
 for z in [21.75,22.30]:line('steel',edge,.1,z,edge[4]-.1,z,.035,-.18)
 for j in range(1,max(2,round(edge[4]/.6))):
  u=edge[4]*j/round(edge[4]/.6);line('steel',edge,u,21.635,u,22.30,.035,-.18)
# Reuse verified historical pavement samples for skirt only; do not rerun unavailable terrain.
for si,f in F.items():
 for j in range(8):
  u=f[4]*j/8;v=f[4]*(j+1)/8;p=P(f,(u+v)/2,0,.02)
  q=min(OLD['pavement_samples'],key=lambda q:(q['xy'][0]-p.x)**2+(q['xy'][1]-p.y)**2)
  rect('stone_dark',f,u,v,q['tp']-15-.02,1.60,.018)
# January photo pixels ONLY on billboard, independent era layer. No full-facade photo projection.
tex=S/'refs/billboard-2025-01.png'
if tex.exists():
 mat('ad_2025_01',(1,1,1),0,.7);m=M['ad_2025_01'];p=m.node_tree.nodes['Principled BSDF'];im=bpy.data.images.load(str(tex));im.pack();n=m.node_tree.nodes.new('ShaderNodeTexImage');n.image=im;m.node_tree.links.new(n.outputs['Color'],p.inputs['Base Color']);m.node_tree.links.new(n.outputs['Alpha'],p.inputs['Alpha']);m.surface_render_method='DITHERED';ERA.add('ad_2025_01')
 rect('ad_2025_01',B,-1.50,W+.10,25.15,34.78,.12,[(0,0),(1,0),(1,1),(0,1)])
tex=S/'refs/davinci-2025-01.png'
if tex.exists():
 mat('davinci_2025_01',(1,1,1),0,.75);m=M['davinci_2025_01'];p=m.node_tree.nodes['Principled BSDF'];im=bpy.data.images.load(str(tex));im.pack();n=m.node_tree.nodes.new('ShaderNodeTexImage');n.image=im;m.node_tree.links.new(n.outputs['Color'],p.inputs['Base Color']);ERA.add('davinci_2025_01')
 f=F[18];rect('screen_back',f,f[4]*.14,f[4]*.92,10.70,12.80,.055);rect('davinci_2025_01',f,f[4]*.50,f[4]*.92,10.70,12.80,.065,[(0,0),(1,0),(1,1),(0,1)])
counts={};objects=[]
for n,(v,f) in G.items():
 me=bpy.data.meshes.new('c244_'+n);me.from_pydata(v,[],f);me.update()
 if any(UV[n]):
  layer=me.uv_layers.new(name='UVMap')
  for poly,uv in zip(me.polygons,UV[n]):
   if uv:
    for li,co in zip(poly.loop_indices,uv):layer.data[li].uv=co
 bm=bmesh.new();bm.from_mesh(me);bmesh.ops.triangulate(bm,faces=bm.faces[:]);bmesh.ops.recalc_face_normals(bm,faces=bm.faces[:]);bm.to_mesh(me);bm.free();me.materials.append(M[n]);o=bpy.data.objects.new('c244_'+n,me);bpy.context.collection.objects.link(o);objects.append(o);counts[n]=len(me.polygons)
for era,path in [(False,'center244.glb'),(True,'signs-2025-01.glb')]:
 bpy.ops.object.select_all(action='DESELECT')
 selected=[o for o in objects if (o.name.removeprefix('c244_') in ERA)==era]
 if not selected:continue
 for o in selected:o.select_set(True)
 bpy.ops.export_scene.gltf(filepath=str(OUT/path),export_format='GLB',use_selection=True,export_yup=True,export_extras=True)
# Preserve the complete original solid as hidden provenance mesh, never exported to runtime.
ref=bpy.data.collections.new('REFERENCE_RAW_PLATEAU_DO_NOT_EXPORT');bpy.context.scene.collection.children.link(ref)
v=[];fs=[]
for surface in D['surfaces']:
 r=surface['ring'][:-1];j=len(v);v.extend(r);fs.append(tuple(range(j,j+len(r))))
me=bpy.data.meshes.new('raw_plateau_exact_rings');me.from_pydata(v,[],fs);me.update();ob=bpy.data.objects.new('raw_plateau_exact_rings',me);ref.objects.link(ob);ob.hide_render=True;ob.hide_viewport=True;ref.hide_render=True;ref.hide_viewport=True
bpy.ops.object.select_all(action='SELECT');bpy.ops.wm.save_as_mainfile(filepath=str(S/'blender/center244.blend'))
viewer={'groundElevationTP':15,'planBounds':[-74.690,70.742,-62.747,83.268],'sun':{'azimuth_deg':207,'elevation_deg':57}}
(OUT/'viewer.json').write_text(json.dumps(viewer,indent=2)+'\n')
for time in ['day','night']:(OUT/('emissive_'+time+'.json')).write_text('{}\n')
stats={'id':'center244','source_id':D['id'],'blender_version':bpy.app.version_string,'datum_tp_m':15,'source_ground_tp':D['ground_tp'],'source_top_tp':D['top_tp'],'roof_translation_m':0,'triangles':sum(counts.values()),'primitives':len(counts),'by_material':counts,'source_sha256':hashlib.sha256((S/'data/plateau.json').read_bytes()).hexdigest(),'pavement_samples':OLD['pavement_samples'],'missing_pavement_samples':OLD['missing_pavement_samples'],'ground_note':'Unchanged recorded baseline samples, not a new ground measurement','upper_reinterpreted_indices':sorted(UPPER|{17,29}),'billboard_inferred_width_m':W+1.6,'billboard_inferred_bottom_z_m':25.15,'billboard_source_face':26,'upper_original_visible_mesh_preserved':False,'upper_original_hidden_provenance_preserved':True,'status':'photo-derived architectural reconstruction; dimensions inferred; upper billboard is documented presentation proxy; rear and lower-left unresolved'}
(S/'data/stats.json').write_text(json.dumps(stats,indent=2)+'\n');print(json.dumps(stats))
