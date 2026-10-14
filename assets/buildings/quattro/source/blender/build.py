"""BIG ECHO / Shibuya Heiwa 21-8, stable legacy id quattro.
Blender 4.2.3 LTS. Run from any cwd: blender -b --python-exit-code 1 -t 4 -P build.py
Optional -- /absolute/output/asset-directory for reproducibility checks.
No runtime registration and no photo pixels in architecture. Original shell coordinates unchanged.
"""
import bpy,json,math,sys
from pathlib import Path
from mathutils import Vector
ROOT=Path(__file__).resolve().parents[2]
OUT=Path(sys.argv[sys.argv.index('--')+1]) if '--' in sys.argv else ROOT
(OUT/'web').mkdir(parents=True,exist_ok=True);(OUT/'source/blend').mkdir(parents=True,exist_ok=True);(OUT/'source/data').mkdir(parents=True,exist_ok=True)
D=json.loads((ROOT/'source/data/plateau.json').read_text()); L=json.loads((ROOT/'source/data/layout.json').read_text())
bpy.ops.wm.read_factory_settings(use_empty=True)
M={};G={}
def material(name,c,metal=0,rough=.6):
 m=bpy.data.materials.new('quattro_'+name);m.use_nodes=True;p=m.node_tree.nodes['Principled BSDF'];p.inputs['Base Color'].default_value=(*c,1);p.inputs['Metallic'].default_value=metal;p.inputs['Roughness'].default_value=rough;M[name]=m;return m
material('wall',(.66,.63,.52),0,.85);material('roof',(.075,.082,.081),.15,.78)
material('silver',(.47,.51,.52),.72,.3);material('edge',(.15,.17,.18),.5,.5)
material('glass',(.12,.21,.23),.35,.28);material('glass_dim',(.075,.13,.15),.25,.34)
material('red_housing',(.48,.014,.026),.22,.4);material('sign_back',(.57,.57,.53),.45,.58)
material('shadow',(.024,.03,.031),0,.9)
material('hood_brown',(.18,.10,.085),.2,.72)
M['roof_lower_hood']=M['roof'];M['roof_upper_opening']=M['shadow']
A=Vector((-52.598,64.148,0));B=Vector((-40.974,52.901,0));T=(B-A).normalized();N=Vector((T.y,-T.x,0));Z=Vector((0,0,1));W=(B-A).length
# All detail coordinates are local frontage metres, not generic repeated floor assumptions.
def P(u,d,z):return A+T*u+N*d+Z*z
def face(mat,vs):
 v,f=G.setdefault(mat,([],[]));i=len(v);v.extend([list(p) for p in vs]);f.append(tuple(range(i,i+len(vs))))
def box(mat,u0,u1,d0,d1,z0,z1):
 p=[P(u,d,z) for z in [z0,z1] for d in [d0,d1] for u in [u0,u1]]
 for ids in [(0,2,3,1),(4,5,7,6),(0,1,5,4),(2,6,7,3),(0,4,6,2),(1,3,7,5)]:face(mat,[p[i] for i in ids])
def beam(mat,a,b,r):
 a,b=Vector(a),Vector(b);direction=(b-a).normalized();v=direction.cross(Z)
 if v.length<.01:v=direction.cross(T)
 v.normalize();w=direction.cross(v).normalized();points=[a+v*r*math.cos(i*math.tau/6)+w*r*math.sin(i*math.tau/6) for i in range(6)]+[b+v*r*math.cos(i*math.tau/6)+w*r*math.sin(i*math.tau/6) for i in range(6)]
 face(mat,list(reversed(points[:6])));face(mat,points[6:])
 for i in range(6):j=(i+1)%6;face(mat,[points[i],points[j],points[j+6],points[i+6]])
def frame(u0,u1,z0,z1,depth=.20,mat='silver',th=.065):
 box(mat,u0,u1,depth-.06,depth,z0,z0+th);box(mat,u0,u1,depth-.06,depth,z1-th,z1)
 box(mat,u0,u0+th,depth-.06,depth,z0,z1);box(mat,u1-th,u1,depth-.06,depth,z0,z1)
# Preserve every original wall/roof triangle, including old measured ground-contact skirt.
S=json.loads((ROOT/'source/data/original_shell.json').read_text())
for name,data in S.items():
 me=bpy.data.meshes.new(name);me.from_pydata(data['vertices'],[],data['faces']);me.materials.append(M['roof' if name.endswith('roof') else 'wall']);ob=bpy.data.objects.new(name,me);bpy.context.collection.objects.link(ob);ob['original_shell_unchanged']=True
# Four low-front tiers, non-uniform widths recorded as inference. No windows on the blank flanks/rear.
bays=L['frontage_bay_edges_m'];rows=L['frontage_glazing_z_m']
for ri,(z0,z1) in enumerate(rows):
 for ci,(u0,u1) in enumerate(zip(bays,bays[1:])):
  u0+=.035;u1-=.035
  box('glass_dim' if ri==0 or ci%3==0 else 'glass',u0,u1,.055,.075,z0,z1);frame(u0,u1,z0,z1)
  mid=(u0+u1)/2;box('silver',mid-.022,mid+.022,.145,.205,z0,z1)
  if ri>0:box('silver',u0,u1,.145,.205,z1-.62,z1-.58)
# Structural silver jambs, floor spandrels and shallow transom cornice.
for u in [0,.30,W-.30,W-.02]:box('silver',u,u+.045,.04,.23,.659,15.55)
for z0,z1 in [(.659,.88),(4.05,4.67),(7.94,8.47),(11.79,12.34),(15.22,15.56)]:
 box('silver',.02,W-.02,.055,.21,z0,z1)
 box('edge',.03,W-.03,.215,.23,z0,z0+.045)
# Deep dark entry recess suggested, not an invented shutter/tenant fit-out.
box('shadow',13.35,15.70,.21,.22,.82,3.85)
for u in [13.43,14.48,15.58]:box('silver',u,u+.055,.23,.27,.86,3.78)
box('glass_dim',13.49,14.48,.235,.245,.86,3.72);box('glass_dim',14.54,15.58,.235,.245,.86,3.72)
for u in [14.30,14.69]:beam('silver',P(u,.30,1.6),P(u,.30,2.2),.018)
# Blank physical sign housings. Branding is a separate, unregistered dated asset below.
for u0,u1,z0,z1 in L['front_sign_housings_m']:
 box('sign_back',u0,u1,.22,.36,z0,z1);box('red_housing',u0+.07,u1-.07,.365,.385,z0+.07,z1-.07);frame(u0,u1,z0,z1,.40,th=.055)
# Persistent recessed screen housing, blank and non-emissive; no dated screen pixels.
box('sign_back',3.10,10.73,.22,.34,4.88,7.86)
box('shadow',3.20,10.63,.345,.36,4.98,7.76)
frame(3.10,10.73,4.88,7.86,.39,mat='edge',th=.075)
# Paired projecting blades at the street edge; no NE/rear protrusions.
for u in L['blade_u_m']:
 box('sign_back',u-.12,u+.12,.12,.98,5.05,15.25)
 box('red_housing',u+.121,u+.135,.19,.92,5.12,15.18)
 for z in [5.32,9.9,14.85]:beam('edge',P(u,.05,z),P(u,.7,z),.045)
 for d in [.12,.98]:beam('silver',P(u+.14,d,5.05),P(u+.14,d,15.25),.023)
 for z in [5.05,15.25]:beam('silver',P(u+.14,.12,z),P(u+.14,.98,z),.023)
# Small non-emissive surface-mounted luminaires, a repeated type visible in view-only official image.
for u in [4.1,7.2,10.3,13.3]:
 beam('silver',P(u,.22,8.55),P(u,.66,8.78),.024);box('edge',u-.19,u+.19,.55,.83,8.77,8.84);box('silver',u-.16,u+.16,.58,.80,8.75,8.77)
# Source-matched steep roof only: fine standing seams and two cross flashings, no dormers/windows invented.
low0=Vector((-52.581,64.165,15.586));low1=Vector((-40.982,52.884,15.612));high0=Vector((-49.306,71.533,28.812));high1=Vector((-38.073,60.467,28.662))
for k in range(1,18):
 t=k/18;a=low0.lerp(low1,t);b=high0.lerp(high1,t);beam('roof',a+Z*.012,b+Z*.012,.0075)
for v in [.04,.98]:
 a=low0.lerp(high0,v)+Z*.025;b=low1.lerp(high1,v)+Z*.025;beam('edge',a,b,.018)
# Photo-supported rooftop articulation over (never replacing/cutting) the preserved steep shell.
# Width/depth are bounded visual estimates from WB01, not calibrated survey dimensions.
def RP(u,v):return low0.lerp(low1,u).lerp(high0.lerp(high1,u),v)
def roof_hood(u0,u1,v0,v1,h,roofmat,split):
 fl=RP(u0,v0)+Z*.045;fr=RP(u1,v0)+Z*.045
 bl=RP(u0,v1)+Z*.08;br=RP(u1,v1)+Z*.08
 tl=fl+Z*h;tr=fr+Z*h
 face(roofmat,[tl,tr,br,bl]);face('wall',[fl,tl,bl]);face('wall',[fr,br,tr])
 # Physical pale metal service cheek plus black inset; no tenant lettering or fabricated glazing.
 seam=fl.lerp(fr,split);seamtop=tl.lerp(tr,split)
 face('wall',[fl,seam,seamtop,tl]);face('shadow',[seam,fr,tr,seamtop])
 for a,b in [(fl,fr),(tl,tr),(fl,tl),(fr,tr),(seam,seamtop)]:beam('silver',a+N*.035,b+N*.035,.035)
 # Narrow pale lower ledge and folded dark fascia, not a solid projecting balcony.
 face('silver',[fl+N*.05,fr+N*.05,fr+N*.24,fl+N*.24]);beam('edge',tl+N*.04,tr+N*.04,.06)
roof_hood(.12,.85,.23,.49,2.35,'roof_lower_hood',.32)
roof_hood(.06,.70,.62,.81,1.85,'hood_brown',.25)
# Upper silver-framed opening / structural grille seen immediately below the crest rail.
u0,u1,v=.12,.85,.88
q0=RP(u0,v)+Z*.06;q1=RP(u1,v)+Z*.06;height=1.65
face('roof_upper_opening',[q0,q1,q1+Z*height,q0+Z*height])
for k in range(7):
 p=q0.lerp(q1,k/6)+N*.055;beam('silver',p,p+Z*height,.035)
for h in [0,.36,height]:beam('silver',q0+N*.055+Z*h,q1+N*.055+Z*h,.04)
# Two diagonal braces in the lower strip match the visible open structural character.
for k in [0,3]:
 a=q0.lerp(q1,k/6)+N*.06;b=q0.lerp(q1,(k+2)/6)+N*.06;beam('silver',a,b+Z*.36,.027)
# Pale end returns make the opening legible without inferring unseen equipment behind it.
for u in [u0,u1]:
 a=RP(u,v)+Z*.06;b=RP(u,.98)+Z*.06;face('wall',[a,a+Z*height,b])
# Roof guardrail set 0.20 m inside the high edge, below original 31.015 m maximum.
a=high0.lerp(high1,.045)+Vector((.08,.16,0));b=high0.lerp(high1,.955)+Vector((.08,.16,0))
for h in [.52,1.07]:beam('silver',a+Z*h,b+Z*h,.024)
for k in range(12):
 p=a.lerp(b,k/11);beam('silver',p,p+Z*1.09,.025)
# Sparse vertical expansion joints on the visible southeast cream flank, not window-floor repetition.
side0=Vector((-40.974,52.901,0));side1=Vector((-36.503,64.557,0));st=(side1-side0).normalized();sn=Vector((st.y,-st.x,0))
for f in [.25,.5,.75]:
 p=side0.lerp(side1,f)+sn*.018;top=min(30.85,15.60+f*17.3);beam('edge',p+Z*.85,p+Z*top,.009)
# Consolidate by material, leaving original shell objects independently auditable.
for name,(verts,faces) in G.items():
 me=bpy.data.meshes.new('quattro_'+name+'_details');me.from_pydata(verts,[],faces);me.materials.append(M[name]);ob=bpy.data.objects.new(me.name,me);bpy.context.collection.objects.link(ob)
architecture=[o for o in bpy.context.scene.objects if o.type=='MESH']
for o in architecture:o.select_set(True)
bpy.ops.export_scene.gltf(filepath=str(OUT/'web/quattro.glb'),export_format='GLB',use_selection=True,export_yup=True,export_extras=True)
# Optional January-only red blade artwork. Original Commons pixels, never view-only official pixels.
for i,u in enumerate(L['blade_u_m']):
 path=ROOT/f'source/refs/blade-{i+1}-2025-01.png'
 if not path.exists():continue
 m=material('january_blade_'+str(i),(.8,.8,.8),0,.65);m.use_backface_culling=True;n=m.node_tree.nodes.new('ShaderNodeTexImage');n.image=bpy.data.images.load(str(path));n.image.pack();m.node_tree.links.new(n.outputs['Color'],m.node_tree.nodes['Principled BSDF'].inputs['Base Color'])
 vs=[P(u+.137,.92,5.12),P(u+.137,.19,5.12),P(u+.137,.19,15.18),P(u+.137,.92,15.18)]
 me=bpy.data.meshes.new('january_blade_'+str(i));me.from_pydata(vs,[],[(0,1,2,3)]);me.materials.append(m);uv=me.uv_layers.new();
 for l,q in zip(uv.data,[(0,0),(1,0),(1,1),(0,1)]):l.uv=q
 ob=bpy.data.objects.new(me.name,me);bpy.context.collection.objects.link(ob);ob['era']='2025-01';ob['runtime_registered']=False
bpy.ops.object.select_all(action='DESELECT')
for o in bpy.context.scene.objects:
 if o.name.startswith('january_blade_'):o.select_set(True)
if bpy.context.selected_objects:bpy.ops.export_scene.gltf(filepath=str(OUT/'web/signs-2025-01.glb'),export_format='GLB',use_selection=True,export_yup=True,export_extras=True)
# Blend contains separate disabled-in-render era collection; review may explicitly enable it.
era=bpy.data.collections.new('JANUARY_2025_UNREGISTERED');bpy.context.scene.collection.children.link(era)
for o in list(bpy.context.scene.objects):
 if o.name.startswith('january_blade_'):
  for c in list(o.users_collection):c.objects.unlink(o)
  era.objects.link(o)
era.hide_render=True;era.hide_viewport=True
bpy.ops.file.pack_all();bpy.ops.wm.save_as_mainfile(filepath=str(OUT/'source/blend/quattro.blend'),compress=True)
stats={'id':'quattro','name':L['name'],'source_id':D['id'],'datum_tp_m':15,'source_ground_tp':D['ground_tp'],'source_top_tp':D['top_tp'],'roof_translation_m':0,'shell_objects_preserved':list(S),'glass_panels':len(rows)*(len(bays)-1),'frontage_tiers':4,'blank_flanks':True,'triangles':sum(sum(len(p.vertices)-2 for p in o.data.polygons) for o in architecture),'primitives':len(architecture),'era_registered':False,'runtime_files_changed':False,'status':'bounded architecture interpretation; non-surveyed frontage divisions, no claimed complete 2025 storefront'}
(OUT/'source/data/stats.json').write_text(json.dumps(stats,ensure_ascii=False,indent=2)+'\n');print(json.dumps(stats,ensure_ascii=False))
