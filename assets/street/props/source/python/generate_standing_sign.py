"""Single standing notice sign, photo-inspired; CC BY-SA 4.0. Blender 4.2.3.
Run: blender -b -t 4 --python-exit-code 1 -P generate_standing_sign.py -- OUTPUT_DIR
No photo textures; blank notice deliberately omits uncertain text and emblem.
"""
import bpy, math, random, sys, json
from mathutils import Vector
from pathlib import Path
OUT=Path(sys.argv[sys.argv.index('--')+1]) if '--' in sys.argv else Path(__file__).parent
OUT.mkdir(parents=True,exist_ok=True);ID='standing_notice_sign'
assert bpy.app.version[:3]==(4,2,3)
bpy.ops.wm.read_factory_settings(use_empty=True);sc=bpy.context.scene;sc.unit_settings.system='METRIC';sc.unit_settings.scale_length=1
asset=bpy.data.collections.new('ASSET | sign only');sc.collection.children.link(asset)
studio=bpy.data.collections.new('STUDIO | never exported');sc.collection.children.link(studio)
def mat(n,c,metal=0,rough=.65):
 m=bpy.data.materials.new(n);m.diffuse_color=(*c,1);m.use_nodes=True;p=m.node_tree.nodes.get('Principled BSDF');p.inputs['Base Color'].default_value=(*c,1);p.inputs['Metallic'].default_value=metal;p.inputs['Roughness'].default_value=rough;return m
paint=mat('Paint | warm pale inferred daylight',(.69,.64,.53),.18,.64)
panel=mat('Blank notice | lettering intentionally omitted',(.79,.77,.68),.05,.73)
trim=mat('Dark inset border',(.22,.24,.22),.4,.68)
chip=mat('Exposed dark metal wear',(.15,.12,.095),.65,.74)
scuff=mat('Paint scuffs',(.46,.43,.35),.18,.8)
metal=mat('Fasteners',(.43,.44,.39),.65,.45)
def mesh(n,vs,fs,ma):
 me=bpy.data.meshes.new(n);me.from_pydata(vs,[],fs);me.materials.append(ma);me.uv_layers.new(name='UVMap');me.update();o=bpy.data.objects.new(n,me);asset.objects.link(o);return o
def box(n,loc,dim,ma,bevel=.003):
 bpy.ops.mesh.primitive_cube_add(size=1,location=loc);o=bpy.context.object;o.name=n;o.dimensions=dim;bpy.ops.object.transform_apply(location=False,rotation=False,scale=True)
 for c in list(o.users_collection):c.objects.unlink(o)
 asset.objects.link(o);o.data.materials.append(ma)
 if bevel:
  b=o.modifiers.new('Soft manufactured edges','BEVEL');b.width=bevel;b.segments=2;bpy.ops.object.modifier_apply(modifier=b.name)
 return o
def rounded(w,h,r,steps=8):
 pts=[]
 for x,z,start in [(w/2-r,h/2-r,0),(-w/2+r,h/2-r,90),(-w/2+r,-h/2+r,180),(w/2-r,-h/2+r,270)]:
  for j in range(steps+1):
   a=math.radians(start+j*90/steps);pts.append((x+r*math.cos(a),z+r*math.sin(a)))
 return pts
# Single planar perimeter, not an A frame. Tube diameter 27 mm.
path=rounded(.477,1.021,.062)
vs=[];fs=[];R=.0135;N=10
for i,(x,z) in enumerate(path):
 prev=Vector(path[(i-1)%len(path)]);nxt=Vector(path[(i+1)%len(path)]);t=(nxt-prev).normalized();normal=Vector((t.y,-t.x))
 for j in range(N):
  a=2*math.pi*j/N;vs.append((x+R*math.cos(a)*normal.x,.025+R*math.sin(a),.576+z+R*math.cos(a)*normal.y))
for i in range(len(path)):
 for j in range(N):fs.append((i*N+j,i*N+(j+1)%N,((i+1)%len(path))*N+(j+1)%N,((i+1)%len(path))*N+j))
o=mesh('Continuous rounded tubular perimeter',vs,fs,paint)
for p in o.data.polygons:p.use_smooth=True
# Slender rounded panel extrusion facing -Y.
def plate(n,w,h,r,zc,y,thick,ma):
 pts=rounded(w,h,r,5);v=[(x,yy,z+zc) for yy in [y-thick/2,y+thick/2] for x,z in pts];L=len(pts);f=[tuple(range(L-1,-1,-1)),tuple(range(L,2*L))]+[(i,(i+1)%L,(i+1)%L+L,i+L) for i in range(L)];return mesh(n,v,f,ma)
plate('Panel dark inset border',.422,.843,.037,.637,.019,.009,trim)
plate('Blank pale notice panel',.410,.831,.032,.637,.012,.004,panel)
# shallow foot with rounded outline in XY, no inferred second frame.
o=plate('Broad shallow rounded foot',.56,.29,.046,0,0,.035,paint);o.rotation_euler[0]=math.pi/2;o.location.z=.0215
# Small raised perimeter lip on the foot, visible in the reference.
pts=rounded(.519,.249,.037,5);vs=[];fs=[]
for i,(x,y) in enumerate(pts):
 prev=Vector(pts[(i-1)%len(pts)]);nxt=Vector(pts[(i+1)%len(pts)]);t=(nxt-prev).normalized();n=Vector((t.y,-t.x))
 for j in range(6):
  a=j*math.pi/3;vs.append((x+.008*math.cos(a)*n.x,y+.008*math.cos(a)*n.y,.044+.008*math.sin(a)))
for i in range(len(pts)):
 for j in range(6):fs.append((i*6+j,i*6+(j+1)%6,((i+1)%len(pts))*6+(j+1)%6,((i+1)%len(pts))*6+j))
lip=mesh('Rounded raised foot lip',vs,fs,paint)
for p in lip.data.polygons:p.use_smooth=True
# Small connection blocks.
for x in [-.195,.195]:
 box('Two foot connection blocks',(x,.024,.057),(.05,.052,.037),paint,.007)
for x in [-.183,.183]:
 for z in [.244,.57,.985]:
  box('Panel fastening tab',(x,.003,z),(.033,.012,.033),paint,.004)
  bpy.ops.mesh.primitive_cylinder_add(vertices=10,radius=.005,depth=.003,location=(x,-.0047,z),rotation=(math.pi/2,0,0));o=bpy.context.object;o.name='Small metal rivet'
  for c in list(o.users_collection):c.objects.unlink(o)
  asset.objects.link(o);o.data.materials.append(metal)
# Deterministic tiny irregular geometry flakes; no procedural shaders or bitmap cost.
rng=random.Random(122)
for i in range(45):
 if i<22:
  x=rng.choice([-.238,.238])+rng.uniform(-.005,.005);z=rng.uniform(.12,1.02);y=.0106;sx=rng.uniform(.002,.006);sz=rng.uniform(.006,.023)
 elif i<34:
  x=rng.uniform(-.17,.17);z=1.087+rng.uniform(-.003,.002);y=.011;sx=rng.uniform(.008,.021);sz=rng.uniform(.0015,.004)
 else:
  x=rng.uniform(-.22,.22);z=.008+rng.uniform(.001,.011);y=-.1451;sx=rng.uniform(.008,.03);sz=rng.uniform(.001,.004)
 mesh('Irregular paint chip',[(x-sx,y,z),(x-sx*.6,y,z+sz),(x+sx*.8,y,z+sz*.6),(x+sx,y,z-sz*.25),(x-sx*.2,y,z-sz*.6)],[(0,1,2,3,4)],chip if i%3 else scuff)
# Grounded, centered and with mesh origins all at the foot center.
bpy.context.view_layer.update();coords=[o.matrix_world@Vector(c) for o in asset.objects for c in o.bound_box];lo=Vector(tuple(min(p[i] for p in coords) for i in range(3)));hi=Vector(tuple(max(p[i] for p in coords) for i in range(3)));shift=Vector(((lo.x+hi.x)/2,(lo.y+hi.y)/2,lo.z))
for o in asset.objects:o.location-=shift
bpy.ops.object.select_all(action='DESELECT')
for o in asset.objects:o.select_set(True)
bpy.context.view_layer.objects.active=next(iter(asset.objects));sc.cursor.location=(0,0,0);bpy.ops.object.origin_set(type='ORIGIN_CURSOR');bpy.ops.object.duplicate();bpy.ops.object.join();joined=bpy.context.object;joined.name=ID
bpy.ops.export_scene.gltf(filepath=str(OUT/(ID+'.glb')),export_format='GLB',use_selection=True,export_yup=True);joined.data.calc_loop_triangles();tri=len(joined.data.loop_triangles);bpy.data.objects.remove(joined,do_unlink=True)
def move(o):
 for c in list(o.users_collection):c.objects.unlink(o)
 studio.objects.link(o)
floor=box('STUDIO floor',(0,0,-.027),(200,200,.05),mat('Studio slate',(.105,.13,.15),0,.86));move(floor)
sc.world=bpy.data.worlds.new('Studio environment');sc.world.use_nodes=True;sc.world.node_tree.nodes['Background'].inputs[0].default_value=(.55,.60,.67,1);sc.world.node_tree.nodes['Background'].inputs[1].default_value=.38
for name,loc,power,size,color in [('Key',(-2,-3,4),350,3,(1,.89,.77)),('Fill',(2,-2,2),180,2,(.78,.87,1)),('Rim',(1,2,3),400,2,(1,1,1))]:
 d=bpy.data.lights.new(name,'AREA');d.energy=power;d.shape='DISK';d.size=size;d.color=color;o=bpy.data.objects.new(name,d);studio.objects.link(o);o.location=loc;o.rotation_euler=(Vector((0,0,.55))-o.location).to_track_quat('-Z','Y').to_euler()
d=bpy.data.cameras.new('Inspection');cam=bpy.data.objects.new('Inspection',d);studio.objects.link(cam);sc.camera=cam
sc.render.engine='CYCLES';sc.cycles.samples=32;sc.cycles.use_denoising=True;sc.render.resolution_x=850;sc.render.resolution_y=1200;sc.render.resolution_percentage=100;sc.view_settings.view_transform='AgX';sc.render.image_settings.file_format='PNG'
def view(n,pos,target,ortho=None):
 cam.location=pos;cam.rotation_euler=(Vector(target)-cam.location).to_track_quat('-Z','Y').to_euler();d.type='ORTHO' if ortho else 'PERSP';d.ortho_scale=ortho or 1.3;d.lens=75;sc.render.filepath=str(OUT/(n+'.png'));bpy.ops.render.render(write_still=True)
view('view_photo_matched',(.16,-3.3,1.39),(0,0,.55))
floor.hide_render=True
view('view_front',(0,-4,.55),(0,0,.55),1.32)
view('view_side',(-4,0,.55),(0,0,.55),1.32)
floor.hide_render=False
cam.location=(.16,-3.3,1.39);cam.rotation_euler=(Vector((0,0,.55))-cam.location).to_track_quat('-Z','Y').to_euler();d.type='PERSP'
for o in studio.objects:o.hide_set(True)
bpy.ops.wm.save_as_mainfile(filepath=str(OUT/(ID+'.blend')),compress=True)
(OUT/'generation_qa.json').write_text(json.dumps({'blender':bpy.app.version_string,'triangles':tri,'dimensions_m':list(hi-lo),'asset_meshes':len(asset.objects),'front':'-Y','origin':'bottom center','camera':'Approximate only; uncalibrated','text':'Intentionally blank','placement':'NOT PLACED'},indent=2))
assert tri<=4000,tri
