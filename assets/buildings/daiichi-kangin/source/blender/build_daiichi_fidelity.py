"""Exact Blender 4.2.3; preserved georeferenced PLATEAU shell, corrected UC facade.
Run blender -b --python-exit-code 1 -P build_daiichi_fidelity.py
No network, no external Python dependencies. All photo-derived signs are January 2025 layer.
"""
import bpy,json,math,random
from pathlib import Path
from mathutils import Vector
assert bpy.app.version==(4,2,3)
ROOT=Path(__file__).resolve().parents[2];SRC=ROOT/'source';OUT=ROOT/'web';OUT.mkdir(exist_ok=True)
D=json.loads((SRC/'data/plateau.json').read_text());OLD=json.loads((SRC/'data/recorded_ground.json').read_text())
bpy.ops.wm.read_factory_settings(use_empty=True)
BASE=D['ground_tp']-15
M={}; G={}; UV={}; SIGN=set()
def mat(n,c,metal=0,rough=.5):
 m=bpy.data.materials.new(n);m.use_nodes=True;p=m.node_tree.nodes['Principled BSDF'];p.inputs['Base Color'].default_value=(*c,1);p.inputs['Metallic'].default_value=metal;p.inputs['Roughness'].default_value=rough;M[n]=m
for a in [('dk_wall',(.53,.52,.46),0,.72),('dk_roof',(.25,.26,.24),0,.85),('dk_aluminum',(.34,.38,.39),.65,.33),('dk_brace',(.38,.42,.42),.55,.42),('dk_reveal',(.055,.07,.07),.2,.63),('dk_joint',(.19,.2,.18),.1,.8),('dk_interior',(.19,.23,.18),0,.8),('dk_curtain',(.35,.40,.31),0,.85),('dk_shop_glass',(.025,.05,.05),.3,.28),('dk_sign_case',(.13,.15,.14),.5,.5),('dk_shop_light',(.7,.71,.63),.1,.3)]:mat(*a)
for i,c in enumerate([(.15,.22,.20),(.2,.29,.25),(.10,.16,.15),(.25,.32,.27)]):mat('dk_glass_'+str(i),c,.3,.29)
def face(n,pts,uv=None):
 vs,fs=G.setdefault(n,([],[]));start=len(vs);vs.extend([tuple(p) for p in pts]);fs.append(tuple(range(start,start+len(pts))));UV.setdefault(n,[]).append(uv)
def box(n,c,sz):
 c=Vector(c);x,y,z=[v/2 for v in sz];v=[c+Vector((a*x,b*y,d*z)) for a,b,d in [(-1,-1,-1),(1,-1,-1),(1,1,-1),(-1,1,-1),(-1,-1,1),(1,-1,1),(1,1,1),(-1,1,1)]]
 for f in [(0,3,2,1),(4,5,6,7),(0,1,5,4),(1,2,6,5),(2,3,7,6),(3,0,4,7)]:face(n,[v[i] for i in f])
def beam(n,a,b,w,d=None):
 a,b=Vector(a),Vector(b);z=(b-a).normalized();x=z.cross(Vector((0,0,1)))
 if x.length<.01:x=z.cross(Vector((1,0,0)))
 x.normalize();y=z.cross(x).normalized();d=d or w;v=[a-x*w/2-y*d/2,a+x*w/2-y*d/2,a+x*w/2+y*d/2,a-x*w/2+y*d/2,b-x*w/2-y*d/2,b+x*w/2-y*d/2,b+x*w/2+y*d/2,b-x*w/2+y*d/2]
 for f in [(0,3,2,1),(4,5,6,7),(0,1,5,4),(1,2,6,5),(2,3,7,6),(3,0,4,7)]:face(n,[v[i] for i in f])
S={'a':(-94.139,23.696),'b':(-72.944,19.98),'n':(-.1727,-.98497)}
E={'a':(-72.944,19.98),'b':(-70.034,47.56),'n':(.99448,-.10493)}
def P(f,u,z,o=0):return Vector((*f['a'],BASE)).lerp(Vector((*f['b'],BASE)),u)+Vector((*f['n'],0))*o+Vector((0,0,z))
def panel(n,f,u,z,w,h,o=.05,uv=False):
 t=(Vector(f['b'])-Vector(f['a'])).normalized();t=Vector((*t,0));c=P(f,u,z,o);v=Vector((0,0,h/2));face(n,[c-t*w/2-v,c+t*w/2-v,c+t*w/2+v,c-t*w/2+v],[(0,0),(1,0),(1,1),(0,1)] if uv else None)
def rail(n,f,u0,u1,z,w=.1,o=.5):beam(n,P(f,u0,z,o),P(f,u1,z,o),w)
def upright(n,f,u,z0,z1,w=.1,o=.5):beam(n,P(f,u,z0,o),P(f,u,z1,o),w)
# Source surfaces kept exactly, no flattened mass or shifted datum.
for s in D['surfaces']:face('dk_wall' if s['kind']=='WallSurface' else 'dk_roof',s['ring'])
# Front south: left tower, 3 braced bays across exposed right facade. Floor levels inferred.
u0,u1=.265,.975; width=21.518*(u1-u0)
# Dark reveals and green reflective glazing behind exterior seismic frame.
for floor in range(7):
 z=4.8+floor*3.75
 panel('dk_reveal',S,(u0+u1)/2,z+1.05,width,3.4,.055)
 for bay in range(12):
  u=u0+(bay+.5)*(u1-u0)/12
  panel('dk_glass_'+str((bay+floor*3)%4),S,u,z+1.10,width/12-.10,2.85,.10)
  # Narrow curtain panels; explicitly generic inferred interior, no false tenant content.
  if (bay+floor)%4==0:panel('dk_curtain',S,u,z+1.1,width/12*.25,2.65,.115)
  upright('dk_aluminum',S,u0+bay*(u1-u0)/12,z-.3,z+2.6,.065,.18)
 rail('dk_aluminum',S,u0,u1,z+1.2,.07,.20)
 # Five horizontal aluminum blades around slab edge, plainly visible in January + February.
 for j in range(5):rail('dk_aluminum',S,u0-.008,u1+.008,z-.72+j*.22,.13,.63)
 # X braces on six lower bays, highest story remains glazing.
 if floor<6:
  for bay in range(3):
   a=u0+bay*(u1-u0)/3;b=u0+(bay+1)*(u1-u0)/3
   beam('dk_brace',P(S,a+.012,z+.10,.48),P(S,b-.012,z+2.35,.48),.16,.20)
   beam('dk_brace',P(S,b-.012,z+.10,.48),P(S,a+.012,z+2.35,.48),.16,.20)
for u in [u0,u0+(u1-u0)/3,u0+2*(u1-u0)/3,u1]:upright('dk_aluminum',S,u,4.2,31.2,.28,.51)
for z in [4.1,30.8,31.15]:rail('dk_aluminum',S,u0-.02,u1+.02,z,.18,.64)
# East side: pale horizontal solid spandrels, slim continuous inset window strips, not giant display.
for floor in range(7):
 z=5.0+floor*3.75
 panel('dk_reveal',E,.5,z+1.55,27.25,1.05,.045)
 for bay in range(13):
  u=(bay+.5)/13
  panel('dk_glass_'+str((bay+floor)%4),E,u,z+1.55,27.73/13-.08,.92,.065)
  upright('dk_aluminum',E,bay/13,z+1.08,z+2.05,.055,.11)
 rail('dk_joint',E,.01,.99,z+.95,.045,.12)
for u in [.025,.24,.48,.72,.97]:upright('dk_joint',E,u,4.3,30.9,.025,.09)
# Corner cladding joints and wrapping ends of front slats.
for z in [5,8.75,12.5,16.25,20,23.75,27.5,31.0]:rail('dk_joint',S,.0,u0,z,.035,.04)
for floor in range(7):
 for j in range(5):rail('dk_aluminum',E,0,.012,4.8+floor*3.75-.72+j*.22,.13,.53)
# Ground storefront rhythm beneath bracing; silhouette and metal canopy observed, details estimated.
for bay in range(5):
 u=u0+(bay+.5)*(u1-u0)/5;panel('dk_shop_glass',S,u,2.05,width/5-.16,3.5,.08);upright('dk_aluminum',S,u0+bay*(u1-u0)/5,.25,4,.11,.24)
rail('dk_sign_case',S,u0,u1,3.65,.3,.6);rail('dk_shop_light',S,u0,u1,3.48,.07,.64)
# UC tower corrugated architecture; no advertising in base layer.
T={'a':(-88.478,22.708),'b':(-87.041,33.024),'n':(.9905,-.138)}
TS={'a':(-94.139,23.702),'b':(-88.478,22.708),'n':(-.173,-.985)}
for f,count in [(T,74),(TS,42)]:
 for j in range(count+1):upright('dk_aluminum',f,j/count,32.0,51.70,.035,.07)
 for z in [32,38,51.8]:rail('dk_aluminum',f,0,1,z,.10,.12)
# Roof perimeter railing, deck services, not advertising tower support hallucination.
for f in [S,E]:
 for z in [31.9,32.5]:rail('dk_aluminum',f,.03,.97,z,.045,-.12)
 for j in range(15):upright('dk_aluminum',f,.03+.94*j/14,31.4,32.55,.045,-.12)
# Visible tower maintenance opening and projecting floodlights, read from Jan photo.
panel('dk_reveal',T,.40,34.9,6.4,3.8,.11)
for j in range(17):rail('dk_glass_1',T,.10,.70,33.2+j*.20,.08,.19)
for j in range(7):upright('dk_aluminum',T,.10+j*.10,33.0,36.9,.08,.22)
for u in [.12,.31,.50,.69]:
 beam('dk_aluminum',P(T,u,37.1,.1),P(T,u,37.35,1.05),.055)
 panel('dk_shop_light',T,u,37.36,.28,.17,1.06)
# Rooftop service boxes observed as a repeated low row in Jan photo; dimensions inferred.
for j in range(8):
 u=.12+j*.095;c=P(E,u,32.15,-1.5);box('dk_wall',c,(1.25,1.65,1.10))
 for k in range(6):panel('dk_joint',E,u,31.85+k*.10,1.10,.025,-.65)
# January photograph shows a diagonal rooftop billboard on an open braced steel stand.
# The estimated stand is inside the existing footprint; it is not a replacement of source shell.
R={'a':(-83.5,39.35),'b':(-72.42,50.55),'n':(.711,-.703)}
RW=(Vector(R['b'])-Vector(R['a'])).length
panel('dk_sign_case',R,.5,41.0,RW+.25,9.35,.0)
for j in range(5):
 u=j/4
 upright('dk_aluminum',R,u,31.8,45.8,.18,-.25)
 upright('dk_aluminum',R,u,31.8,36.5,.18,-2.8)
 beam('dk_brace',P(R,u,32,-2.8),P(R,u,39,-.25),.15)
 if j<4:
  beam('dk_brace',P(R,u,32,-.25),P(R,u+.25,36.5,-.25),.13)
  beam('dk_brace',P(R,u+.25,32,-.25),P(R,u,36.5,-.25),.13)
for z in [32,34.2,36.5,45.75]:rail('dk_aluminum',R,0,1,z,.13,-.25)
# Feet meet retained PLATEAU roof at each XY. Lower rear annex roof is not the main deck.
# Heights below are ray intersections with source RoofSurface polygons, not surveyed new positions.
front_roof=[31.204,34.439,34.439,31.8,16.785]
rear_roof=[31.204,34.439,31.204,16.785,18.0]
for j in range(5):
 for offset,zroof in [(-.25,front_roof[j]),(-2.8,rear_roof[j])]:
  if zroof-BASE<31.8:upright('dk_aluminum',R,j/4,zroof-BASE,31.8,.18,offset)

# Small floodlight arms visible above the sign. Lens planes only, no fake emission at day.
for u in [.05,.5,.95]:
 beam('dk_aluminum',P(R,u,45.8,0),P(R,u,46.1,.60),.055)
 panel('dk_shop_light',R,u,46.05,.3,.19,.62)
# Existing measured skirt, unchanged recorded ground samples. No new survey claimed.
for f,name in [(S,'south'),(E,'east')]:
 hits=[s for s in OLD['pavement_samples'] if s['facade']==name]
 for i in range(30):
  a,b=i/30,(i+1)/30;pa,pb=P(f,a,.05,.025),P(f,b,.05,.025)
  za=min(hits,key=lambda s:abs(s['u']-a))['tp']-15-.03;zb=min(hits,key=lambda s:abs(s['u']-b))['tp']-15-.03
  face('dk_wall',[pa,pb,(pb.x,pb.y,zb),(pa.x,pa.y,za)])
# Explicit Jan31 snapshot, separate active-era GLB.
def texture(n,file):
 mat(n,(1,1,1),0,.65);m=M[n];p=m.node_tree.nodes['Principled BSDF'];t=m.node_tree.nodes.new('ShaderNodeTexImage');t.image=bpy.data.images.load(str(SRC/'textures'/file));m.node_tree.links.new(t.outputs['Color'],p.inputs['Base Color']);SIGN.add(n)
for n in ['uc_east','uc_south','vanguard','mizuho','roof_campaign']:texture('dk_sign_jan_'+n,n+'.png')
panel('dk_sign_jan_roof_campaign',R,.5,41.0,RW,9.1,.05,True)
panel('dk_sign_jan_uc_east',T,.5,44.8,10.35,13.5,.14,True)
panel('dk_sign_jan_uc_south',TS,.5,44.8,5.72,13.5,.14,True)
# Corner east facade banner and south bank blade observed Jan31; source pixels only.
panel('dk_sign_case',E,.055,23.5,2.5,9.9,.26)
panel('dk_sign_jan_vanguard',E,.055,23.5,2.30,9.65,.29,True)
panel('dk_sign_case',S,.945,5.8,1.25,5.8,.80)
panel('dk_sign_jan_mizuho',S,.945,5.8,1.1,5.65,.83,True)
counts={}
for n,(vs,fs) in G.items():
 me=bpy.data.meshes.new(n);me.from_pydata(vs,[],fs);me.update();me.materials.append(M[n]);ob=bpy.data.objects.new(n,me);bpy.context.collection.objects.link(ob)
 if n in SIGN:
  uv=me.uv_layers.new(name='UVMap')
  for poly,coords in zip(me.polygons,UV[n]):
   for li,coord in zip(poly.loop_indices,coords):uv.data[li].uv=coord
 me.calc_loop_triangles();counts[n]=len(me.loop_triangles)
for era in ['base','2025-01']:
 for o in bpy.context.scene.objects:o.select_set((o.name in SIGN)==(era!='base'))
 bpy.ops.export_scene.gltf(filepath=str(OUT/('daiichi-kangin.glb' if era=='base' else 'signs-2025-01.glb')),export_format='GLB',use_selection=True,export_yup=True)
for o in bpy.context.scene.objects:o.select_set(True)
bpy.ops.file.pack_all()
bpy.ops.wm.save_as_mainfile(filepath=str(SRC/'blender/daiichi-kangin.blend'))
(OUT/'viewer.json').write_text(json.dumps({'groundElevationTP':15,'planBounds':[-94.139,19.98,-69.593,54.732],'sun':{'azimuth_deg':207,'elevation_deg':57}},indent=2))
for mode in ['day','night']:(OUT/f'emissive_{mode}.json').write_text(json.dumps({'dk_shop_light':{'kind':'interior','emit':[1,.95,.8],'estr':.6 if mode=='night' else 0}},indent=2))
stat={'source_id':D['id'],'plateau_id':D['plateau_id'],'triangles':sum(counts.values()),'primitives':len(counts),'materials':counts,'datum_tp_m':15,'roof_deviation_m':0,'pavement_samples':OLD['pavement_samples'],'geometry_status':'Identity-corrected prototype, estimated facade dimensions; retained original shell','sign_era':'2025-01-31 only, not October'}
(SRC/'data/stats.json').write_text(json.dumps(stat,indent=2));print('COMPLETE',stat['triangles'],stat['primitives'])
