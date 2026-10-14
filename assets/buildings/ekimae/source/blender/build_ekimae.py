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
RECORDED='--recorded-ground' in sys.argv
if not SIGN_ONLY and not RECORDED: bpy.ops.import_scene.gltf(filepath=ground)
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
if SIGN_ONLY or RECORDED:
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
# Photo-led full facade replacement, separate from original PLATEAU shell.
sys.path.insert(0,str(Path(__file__).parent))
from facade_detail import build
build(globals())
objects=[]
for (layer,name),bm in GROUP.items():
 bmesh.ops.triangulate(bm,faces=bm.faces[:]);me=bpy.data.meshes.new(name);bm.to_mesh(me);bm.free();me.materials.append(M[name]);me.calc_loop_triangles();ob=bpy.data.objects.new(name,me);bpy.context.collection.objects.link(ob);objects.append((layer,ob))
counts={}
for layer,file in [('base','ekimae.glb'),('signs','signs-2025-11.glb')]:
 if SIGN_ONLY and layer=='base':continue
 bpy.ops.object.select_all(action='DESELECT')
 for kind,ob in objects:ob.select_set(kind==layer)
 bpy.ops.export_scene.gltf(filepath=str(OUT/file),export_format='GLB',use_selection=True,export_yup=True,export_image_format='JPEG',export_jpeg_quality=90)
 counts[layer]={'meshes':sum(k==layer for k,o in objects),'triangles':sum(len(o.data.loop_triangles) for k,o in objects if k==layer)}
if SIGN_ONLY:
 print('EKIMAE signs-only: base, anchor, viewer and stats preserved',counts);sys.exit(0)
points=[p for s in D['surfaces'] for p in s['ring']]
(OUT/'viewer.json').write_text(json.dumps({'planBounds':[min(p[0] for p in points),min(p[1] for p in points),max(p[0] for p in points),max(p[1] for p in points)],'groundElevationTP':anchor,'layers':{'signs':'signs-2025-11.glb'}},indent=2)+'\n')
for mode in ['day','night']:
 rows={name:{'kind':'led' if name.startswith('ek_sign_') else 'interior','emit':[1,.9,.75],'estr':(1.2 if name in ['ek_sign_samsung','ek_sign_hit_sky'] else .5 if name.startswith('ek_sign_') else .4) if mode=='night' else 0} for name in M if name.startswith('ek_sign_') or name in ['ek_shop_glass','ek_shop_light']}
 (OUT/f'emissive_{mode}.json').write_text(json.dumps(rows,indent=2)+'\n')
(ROOT/'data/stats.json').write_text(json.dumps({'source_id':D['id'],'plateau_id':D['plateau_id'],'anchor_tp':anchor,'plateau_ground_tp':D['ground_tp'],'roof_deviation_vs_plateau_m':anchor-D['ground_tp'],'frontage_samples':samples,'replaced_corner_faces':removed,'geometry':counts,'status':'Photo-led revision; interior and unseen surfaces inferred; November 2025 signs CC BY-SA 4.0', 'ground_sample_mode':'recorded reuse' if RECORDED else 'fresh raycast'},indent=2)+'\n')
bpy.context.scene.unit_settings.system='METRIC'
bpy.context.scene.unit_settings.scale_length=1
bpy.ops.file.pack_all()
bpy.ops.wm.save_as_mainfile(filepath=str(Path(__file__).parent/'ekimae-fidelity.blend'),compress=True)
print('EKIMAE',anchor,counts,'replaced wall faces',removed)
