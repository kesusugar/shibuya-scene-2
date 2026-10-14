"""Ekimae B: original PLATEAU roof/back, rounded corner, dated November-2025 signage.
blender -b --python-exit-code 1 -t 4 -P build_ekimae.py -- plateau.json facade.json ground.glb outdir
"""
import bpy,bmesh,json,math,sys
from pathlib import Path
from mathutils import Vector
from mathutils.bvhtree import BVHTree
src,config,ground,out=sys.argv[sys.argv.index('--')+1:][:4]
assert bpy.app.version==(4,2,3)
D=json.loads(Path(src).read_text());F=json.loads(Path(config).read_text());ROOT=Path(config).parent.parent;OUT=Path(out);OUT.mkdir(parents=True,exist_ok=True)
bpy.ops.wm.read_factory_settings(use_empty=True)
SIGN_ONLY='--signs-only' in sys.argv
if not SIGN_ONLY: bpy.ops.import_scene.gltf(filepath=ground)
bm=bmesh.new()
for ob in list(bpy.context.scene.objects):
 if ob.type=='MESH' and ob.name.startswith(('ground_road','ground_sidewalk','ground_intersection','ground_fill')):
  me=ob.data.copy();me.transform(ob.matrix_world);bm.from_mesh(me);bpy.data.meshes.remove(me)
bvh=BVHTree.FromBMesh(bm);bm.free()
A=Vector((-62.416,-10.01,0));B=Vector((-46.78,-10.647,0));T=(B-A).normalized();N=Vector((-T.y,T.x,0));L=(B-A).length
CX,CY,R=-47.25,-19.25,8.72;START,END=math.radians(90),math.radians(-8)
front=[]
for i in range(41):
 p=A.lerp(B,i/40)+N*.4;front.append(p)
for i in range(41):
 angle=START+(END-START)*i/40;front.append(Vector((CX+(R+.4)*math.cos(angle),CY+(R+.4)*math.sin(angle),0)))
samples=[]
for p in front:
 hit=bvh.ray_cast(Vector((p.x,p.y,60)),Vector((0,0,-1)))[0]
 if hit:samples.append({'x':round(p.x,3),'y':round(p.y,3),'tp':round(hit.z+15,3)})
if SIGN_ONLY:
 saved=json.loads((ROOT/'data/stats.json').read_text());samples=saved['frontage_samples']
assert samples,'No frontage ground samples';anchor=min(p['tp'] for p in samples);BASE=D['ground_tp']-15
for ob in list(bpy.context.scene.objects):bpy.data.objects.remove(ob,do_unlink=True)
M={};GROUP={}
def mat(name,rgb,rough=.65,metal=0,texture=None):
 m=bpy.data.materials.new(name);m.use_nodes=True;p=m.node_tree.nodes['Principled BSDF'];p.inputs['Base Color'].default_value=(*rgb,1);p.inputs['Roughness'].default_value=rough;p.inputs['Metallic'].default_value=metal
 if texture:
  node=m.node_tree.nodes.new('ShaderNodeTexImage');node.image=bpy.data.images.load(str(ROOT/'textures'/f'{texture}.png'));m.node_tree.links.new(node.outputs['Color'],p.inputs['Base Color']);m.node_tree.links.new(node.outputs['Color'],p.inputs['Emission Color']);p.inputs['Emission Strength'].default_value=1
 M[name]=m
for name,rgb in [('wall',(.43,.45,.44)),('roof',(.25,.26,.25)),('band',(.74,.75,.72)),('red_frame',(.36,.015,.02)),('gold',(.78,.5,.035)),('yellow',(.9,.58,.025)),('steel',(.29,.3,.31)),('glass',(.05,.08,.07)),('shop_glass',(.018,.025,.018)),('shop_light',(.73,.66,.46)),('screen_back',(.014,.014,.018))]:mat('ek_'+name,rgb,.3 if 'glass' in name else .65,.25 if name in ['glass','steel'] else 0)
for name in F['textures']:mat('ek_sign_'+name,(1,1,1),.8,0,name)
def face(name,pts,uv=None,layer='base'):
 bm=GROUP.setdefault((layer,name),bmesh.new());lay=bm.loops.layers.uv.verify() if uv else None;f=bm.faces.new([bm.verts.new(p) for p in pts]);f.normal_update()
 if uv:
  for loop,coord in zip(f.loops,uv):loop[lay].uv=coord
def box(center,size,name):
 x,y,z=center;w,d,h=size;p=[(x+a,y+b,z+c) for a,b,c in [(-w/2,-d/2,-h/2),(w/2,-d/2,-h/2),(w/2,d/2,-h/2),(-w/2,d/2,-h/2),(-w/2,-d/2,h/2),(w/2,-d/2,h/2),(w/2,d/2,h/2),(-w/2,d/2,h/2)]]
 for ids in [(0,3,2,1),(4,5,6,7),(0,1,5,4),(1,2,6,5),(2,3,7,6),(3,0,4,7)]:face(name,[p[i] for i in ids])
def panel(u,z,w,h,name,offset=.12,layer='base'):
 c=A+T*u+N*offset+Vector((0,0,z));pts=[c-T*w/2-Vector((0,0,h/2)),c-T*w/2+Vector((0,0,h/2)),c+T*w/2+Vector((0,0,h/2)),c+T*w/2-Vector((0,0,h/2))];face(name,pts,[(1,0),(1,1),(0,1),(0,0)] if layer=='signs' else [(0,0),(0,1),(1,1),(1,0)],layer)
E=Vector((-38.316,-20.562,0));ET=(Vector((-45.003,-54.21,0))-E).normalized();EN=Vector((-ET.y,ET.x,0));EL=34.305
# Long east frontage is the dominant side in the Stream view; texture horizontal axes run south to north.
def east_panel(u,z,w,h,name,offset=.12,layer='base',uv_span=None):
 c=E+ET*u+EN*offset+Vector((0,0,z));pts=[c-ET*w/2-Vector((0,0,h/2)),c-ET*w/2+Vector((0,0,h/2)),c+ET*w/2+Vector((0,0,h/2)),c+ET*w/2-Vector((0,0,h/2))]
 lo,hi=uv_span if uv_span is not None else (1,0)
 face(name,pts,[(lo,0),(lo,1),(hi,1),(hi,0)],layer)
def arc(z,h,name,offset=0,layer='base',start=START,end=END,uv_span=None):
 if uv_span is None:uv_span=(1,0) if layer=='signs' else (0,1)
 for i in range(28):
  a=start+(end-start)*i/28;b=start+(end-start)*(i+1)/28;r=R+offset
  pts=[(CX+r*math.cos(a),CY+r*math.sin(a),z-h/2),(CX+r*math.cos(a),CY+r*math.sin(a),z+h/2),(CX+r*math.cos(b),CY+r*math.sin(b),z+h/2),(CX+r*math.cos(b),CY+r*math.sin(b),z-h/2)]
  u0=uv_span[0]+(uv_span[1]-uv_span[0])*i/28;u1=uv_span[0]+(uv_span[1]-uv_span[0])*(i+1)/28
  face(name,pts,[(u0,0),(u0,1),(u1,1),(u1,0)],layer)
# Replace only the diagonal NE street wall with a curve. Keep original roof and remaining wall faces.
removed=0
for surface in D['surfaces']:
 ring=[Vector((p[0],p[1],p[2]-BASE)) for p in surface['ring']]
 if (ring[0]-ring[-1]).length<.001:ring=ring[:-1]
 if surface['kind']=='WallSurface' and all(p.x>-47 for p in ring) and all(p.y>-21 for p in ring):removed+=1;continue
 face('ek_wall' if surface['kind']=='WallSurface' else 'ek_roof',ring)
H=D['top_tp']-D['ground_tp'];arc(H/2,H,'ek_wall')
# North face: narrow square windows with red surrounds and horizontal ceramic/metal bands.
for z in [5.1,8.5,11.9,15.3,18.7,22.1,25.5,28.9]:
 for u in [1.2,3.4,5.6,7.8,10,12.2,14.4]:
  panel(u,z,1.7,2.6,'ek_red_frame');panel(u,z+.03,1.42,2.25,'ek_glass',.15)
 panel(L/2,z-1.55,L,.23,'ek_band',.18)
# Rounded face: lower cafes and upper ribbon windows/restaurant bands.
for z in [5.1,8.5,11.9,15.3,18.7]:
 arc(z,2.5,'ek_glass',.08);arc(z-1.45,.26,'ek_band',.17)
 for i in range(13):
  a=START+(END-START)*i/12;arc(z,2.7,'ek_band',.15,start=a-.006,end=a+.006)
for z in [4.0,7.2,10.4]:arc(z,.1,'ek_gold',.21)
arc(1.6,3.2,'ek_yellow',.04)
for i in range(5):
 a=START+(END-START)*(i+.5)/5;arc(1.5,2.4,'ek_shop_glass',.10,start=a+.115,end=a-.115)
arc(3.0,.14,'ek_shop_light',.19)
for u in [2,6,10,14]:panel(u,1.5,3.3,2.7,'ek_shop_glass',.14)
# Correct the initially missing long east frontage as one facade item.
for z in [5.1,8.5,11.9,15.3,18.7,22.1,25.5,28.9]:
 for i in range(15):
  u=1.15+2.2*i;east_panel(u,z,1.75,2.65,'ek_red_frame');east_panel(u,z+.03,1.42,2.25,'ek_glass',.16)
 east_panel(EL/2,z-1.5,EL,.22,'ek_band',.19)
for z in [5.1,8.5,11.9,15.3,18.7]:
 east_panel(6.5,z,12.9,2.65,'ek_glass',.2)
 for i in range(8):east_panel(.2+1.85*i,z,.07,2.7,'ek_band',.24)
 east_panel(6.5,z-1.5,13.0,.22,'ek_band',.26)
east_panel(6.5,1.6,13.0,3.2,'ek_yellow',.22)
for u in [2,5,8,11]:east_panel(u,1.5,2.4,2.6,'ek_shop_glass',.25)
east_panel(6.5,3.0,13,.16,'ek_shop_light',.28)
for z in [4,7.2,10.4]:east_panel(6.5,z,13,.10,'ek_gold',.27)
# EK01: each crop spans both the curved corner and east return; never repeat it.
SIGN_SPLIT=(R*(START-END))/(R*(START-END)+13.0)
for name,z,h in [('shabu',29.4,2.65),('francais',26.1,3.1),('gusto',22.75,3.2)]:east_panel(6.5,z,13,h,'ek_sign_'+name,.29,'signs',uv_span=(1-SIGN_SPLIT,0))
east_panel(15,17.2,2.8,22,'ek_sign_eyecity',.25,'signs')
east_panel(6.5,7.0,7.5,1.5,'ek_sign_loccitane',.30,'signs')
# Restaurant and vertical tenant signs: photographed November 1, 2025, not a February campaign.
for name,z,h in [('shabu',29.4,2.65),('francais',26.1,3.1),('gusto',22.75,3.2)]:arc(z,h,'ek_sign_'+name,.23,'signs',uv_span=(1,1-SIGN_SPLIT))
for z in [20.9,24.35,27.7,30.9]:arc(z,.22,'ek_band',.26)
panel(10.8,17.2,2.8,22,'ek_sign_eyecity',.23,'signs')
# L'OCCITANE store silhouette and green awning are photo-confirmed; branches conceal precise entrance count.
arc(7.0,1.5,'ek_sign_loccitane',.24,'signs',math.radians(70),math.radians(15))
for i in range(16):
 a=START+(END-START)*i/16;b=START+(END-START)*(i+1)/16
 face('ek_glass',[(CX+(R+.1)*math.cos(a),CY+(R+.1)*math.sin(a),3.35),(CX+(R+.1)*math.cos(b),CY+(R+.1)*math.sin(b),3.35),(CX+(R+1.0)*math.cos(b),CY+(R+1.0)*math.sin(b),2.75),(CX+(R+1.0)*math.cos(a),CY+(R+1.0)*math.sin(a),2.75)])
# Rooftop billboards, support steel and backings. Height revised independently after the first comparison.
roof=F['rooftop'];z,h=roof['center_height_m'],roof['height_m']
arc(z,h+.25,'ek_screen_back',.20);east_panel(6.5,z,13.2,h+.25,'ek_screen_back',.20);arc(z,h,'ek_sign_samsung',.24,'signs',uv_span=(1,1-SIGN_SPLIT));east_panel(6.5,z,13,h,'ek_sign_samsung',.25,'signs',uv_span=(1-SIGN_SPLIT,0))
panel(L/2,z,L,h,'ek_screen_back',.2);panel(L/2,z,L-.15,h-.15,'ek_sign_hit_sky',.24,'signs')
for i in range(7):
 a=START+(END-START)*i/6;p=Vector((CX+(R-.18)*math.cos(a),CY+(R-.18)*math.sin(a),0));box((p.x,p.y,(31.36+z+h/2)/2),(.12,.12,z+h/2-31.36),'ek_steel')
for u in [0,L/3,2*L/3,L]:
 p=A+T*u-N*.16;box((p.x,p.y,(31.36+z+h/2)/2),(.12,.12,z+h/2-31.36),'ek_steel')
for zz in [z-h/2,z,z+h/2]:arc(zz,.12,'ek_steel',-.2)
objects=[]
for (layer,name),bm in GROUP.items():
 bmesh.ops.triangulate(bm,faces=bm.faces[:]);me=bpy.data.meshes.new(name);bm.to_mesh(me);bm.free();me.materials.append(M[name]);me.calc_loop_triangles();ob=bpy.data.objects.new(name,me);bpy.context.collection.objects.link(ob);objects.append((layer,ob))
counts={}
for layer,file in [('base','ekimae.glb'),('signs','signs-2025-11.glb')]:
 if SIGN_ONLY and layer=='base':continue
 bpy.ops.object.select_all(action='DESELECT')
 for kind,ob in objects:ob.select_set(kind==layer)
 bpy.ops.export_scene.gltf(filepath=str(OUT/file),export_format='GLB',use_selection=True,export_yup=True)
 counts[layer]={'meshes':sum(k==layer for k,o in objects),'triangles':sum(len(o.data.loop_triangles) for k,o in objects if k==layer)}
if SIGN_ONLY:
 print('EKIMAE signs-only: base, anchor, viewer and stats preserved',counts);sys.exit(0)
points=[p for s in D['surfaces'] for p in s['ring']]
(OUT/'viewer.json').write_text(json.dumps({'planBounds':[min(p[0] for p in points),min(p[1] for p in points),max(p[0] for p in points),max(p[1] for p in points)],'groundElevationTP':anchor,'layers':{'signs':'signs-2025-11.glb'}},indent=2)+'\n')
for mode in ['day','night']:
 rows={name:{'kind':'led' if name.startswith('ek_sign_') else 'interior','emit':[1,.9,.75],'estr':(1.2 if name in ['ek_sign_samsung','ek_sign_hit_sky'] else .5 if name.startswith('ek_sign_') else .4) if mode=='night' else 0} for name in M if name.startswith('ek_sign_') or name in ['ek_shop_glass','ek_shop_light']}
 (OUT/f'emissive_{mode}.json').write_text(json.dumps(rows,indent=2)+'\n')
(ROOT/'data/stats.json').write_text(json.dumps({'source_id':D['id'],'plateau_id':D['plateau_id'],'anchor_tp':anchor,'plateau_ground_tp':D['ground_tp'],'roof_deviation_vs_plateau_m':anchor-D['ground_tp'],'frontage_samples':samples,'replaced_corner_faces':removed,'geometry':counts,'status':'B prototype; facade/entrances estimated; rooftop/tenant images November 2025 CC BY-SA 4.0'},indent=2)+'\n')
print('EKIMAE',anchor,counts,'replaced wall faces',removed)
