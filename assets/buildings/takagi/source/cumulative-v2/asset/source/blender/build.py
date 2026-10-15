"""Portable surgical billboard reconstruction. Blender 4.2.3, no external Python dependencies."""
import bpy,bmesh,json,math,sys,hashlib,struct
from pathlib import Path
from mathutils import Vector
from mathutils.geometry import tessellate_polygon,intersect_ray_tri
R=Path(__file__).resolve().parents[2];E=Path(sys.argv[sys.argv.index('--evidence-dir')+1]) if '--evidence-dir' in sys.argv else R/'source/evidence';E.mkdir(parents=True,exist_ok=True)
assert bpy.app.version[:3]==(4,2,3)
assert hashlib.sha256((R/'source/data/baseline.glb').read_bytes()).hexdigest()=='d081d33fe9b358769264f0277962248f369f276a04dffd91e22214445f93609f'
assert hashlib.sha256((R/'source/data/plateau.json').read_bytes()).hexdigest()=='91168e63a0f5dfdee3c203fe2d83431b8f059ef5a1f61d017c9e09f99f38e42f'
bpy.ops.wm.read_factory_settings(use_empty=True);bpy.ops.import_scene.gltf(filepath=str(R/'source/data/baseline.glb'))
base=list(bpy.context.scene.objects);A=Vector((-59.952,89.353,0));t=Vector((7.496,17.711,0)).normalized();n=Vector((t.y,-t.x,0))
def P(u,d,z):return A+t*u-n*d+Vector((0,0,z))
def key(ps):return tuple(sorted(tuple(round(float(c),5) for c in p) for p in ps))
owned=json.loads((R/'source/refs/original_sign_triangle_ownership.json').read_text());wanted={(x['material'],key(x['vertices'])) for x in owned};removed=[]
# Preserve original mesh vertices and face attributes; delete only positively matched triangles.
for o in base:
 if o.type!='MESH':continue
 bm=bmesh.new();bm.from_mesh(o.data);dead=[]
 for f in bm.faces:
  k=(o.data.materials[f.material_index].name,key([o.matrix_world@v.co for v in f.verts]))
  if k in wanted:dead.append(f);removed.append(k)
 bmesh.ops.delete(bm,geom=dead,context='FACES_ONLY');bm.to_mesh(o.data);bm.free()
assert len(removed)==24 and set(removed)==wanted
# Same presentation as frozen facade stage; no runtime/exposure changes.
scene=bpy.context.scene;scene.render.engine='CYCLES';scene.cycles.samples=24;scene.render.resolution_x=1000;scene.render.resolution_y=1000;scene.render.resolution_percentage=100
scene.world=bpy.data.worlds.new('Inspection studio');scene.world.color=(.65,.65,.65);scene.view_settings.view_transform='Standard';scene.view_settings.look='Medium High Contrast';scene.render.image_settings.file_format='PNG'
bpy.ops.object.light_add(type='AREA',location=(-10,35,95));bpy.context.object.data.energy=170000;bpy.context.object.data.shape='DISK';bpy.context.object.data.size=70
bpy.ops.object.camera_add(location=(-2,20,52));cam=bpy.context.object;cam.data.type='ORTHO';scene.camera=cam

def render(name,normal=False):
 target=P(9.616,5.8,43.8) if normal else Vector((-69,98,25));cam.location=target+n*85 if normal else Vector((-2,20,52));cam.rotation_euler=(target-cam.location).to_track_quat('-Z','Y').to_euler();cam.data.ortho_scale=24 if normal else 61;scene.render.filepath=str(E/(name+'.png'));bpy.ops.render.render(write_still=True)
def mat(name,h):
 rgb=[int(h[i:i+2],16)/255 for i in (0,2,4)];rgb=[v/12.92 if v<=.04045 else ((v+.055)/1.055)**2.4 for v in rgb];m=bpy.data.materials.new(name);m.use_nodes=True;m.diffuse_color=(*rgb,1);p=m.node_tree.nodes['Principled BSDF'];p.inputs['Base Color'].default_value=(*rgb,1);p.inputs['Roughness'].default_value=.6;return m
white=mat('takagi_billboard_white','E9EDEB');blue=mat('takagi_billboard_blue','005DA6');yellow=mat('takagi_billboard_yellow','FFDC0A');support=mat('takagi_billboard_support','AFB6B5')
G={}
def face(vs,m):
 # Caller supplies outward-wound polygon. Tessellation maintains orientation.
 vv,ff=G.setdefault(m.name,([],[]));ring=[Vector(v) for v in vs]
 for tr in tessellate_polygon([ring]):
  ps=[ring[i] for i in tr] if isinstance(tr[0],int) else list(tr)
  if (ps[1]-ps[0]).cross(ps[2]-ps[0]).length<1e-9:continue
  st=len(vv);vv.extend(ps);ff.append([st,st+1,st+2])
def poly(points,d,m):
 ps=[P(u,d,z) for u,z in points]
 if (ps[1]-ps[0]).cross(ps[2]-ps[0]).dot(n)<0:ps.reverse()
 face(ps,m)
def rect(u0,u1,z0,z1,d,m):poly([(u0,z0),(u1,z0),(u1,z1),(u0,z1)],d,m)
def box(u0,u1,d0,d1,z0,z1,m):
 vs=[P(u,d,z) for z in [z0,z1] for d in [d0,d1] for u in [u0,u1]]
 for ids in [(0,1,5,4),(3,2,6,7),(2,0,4,6),(1,3,7,5),(4,5,7,6),(2,3,1,0)]:face([vs[i] for i in ids],m)
# white housing with actual shallow thickness 0.25 m.
box(.616,18.616,5.8,6.05,39.5,52,white)
fieldw=18*.95;fieldh=12.5*.57;cz=39.5+12.5*.51
rect(9.616-fieldw/2,9.616+fieldw/2,cz-fieldh/2,cz+fieldh/2,5.785,blue)
ow=fieldw*.96;oh=fieldh*.89
poly([(9.616+ow/2*math.cos(i*2*math.pi/64),cz+oh/2*math.sin(i*2*math.pi/64)) for i in range(64)],5.770,yellow)
# Authored broad block glyph polygons, not a font or official supplied logo.
wordw=ow*.83;cap=oh*.445;unit=wordw/4.5;left=9.616-wordw/2;bottom=cz-cap/2
I=[(0,0),(.52,0),(.52,1),(0,1)]
K=[(0,0),(.43,0),(.43,.42),(.76,0),(1.28,0),(.77,.55),(1.22,1),(.70,1),(.43,.59),(.43,1),(0,1)]
EE=[(0,0),(1.06,0),(1.06,.27),(.48,.27),(.48,.39),(.96,.39),(.96,.64),(.48,.64),(.48,.76),(1.06,.76),(1.06,1),(0,1)]
def glyph(points,x):poly([(left+(x+a)*unit,bottom+b*cap) for a,b in points],5.755,blue)
glyph(I,0);glyph(K,.77);glyph(EE,2.20)
# A built from a nonoverlapping planar partition; triangular open counter .36-.68.
x=3.51;w=.99
for points in [[(0,0),(.35,0),(.39,.18),(.045,.18)],[(.65,0),(1,0),(.955,.18),(.61,.18)],[(.045,.18),(.955,.18),(.91,.36),(.075,.36)],[(.075,.36),(.42,.36),(.5,.68),(.17,.68)],[(.58,.36),(.91,.36),(.83,.68),(.5,.68)],[(.17,.68),(.83,.68),(.75,1),(.25,1)]]:glyph([(a*w,b) for a,b in points],x)
# Source roof and actual existing rib ray intersections; avoid ribs by small d refinement.
D=json.loads((R/'source/data/plateau.json').read_text());roof=[]
for i,s in enumerate(D['surfaces']):
 if s['kind']!='RoofSurface':continue
 ring=[Vector(v) for v in s['ring'][:-1]]
 for tr in tessellate_polygon([ring]):roof.append((i,[ring[j] for j in tr] if isinstance(tr[0],int) else list(tr)))
ribs=[]
for o in base:
 if o.type=='MESH' and 'crown_rib' in o.name:
  for f in o.data.polygons:ribs.append([o.matrix_world@o.data.vertices[j].co for j in f.vertices])
def hit(p,tris):
 hits=[]
 for i,vs in tris:
  h=intersect_ray_tri(*vs,Vector((0,0,-1)),Vector((p.x,p.y,60)),True)
  if h:hits.append((h.z,i))
 return max(hits) if hits else None
contacts=[]
for u in [2,7,12,17]:
 chosen=None
 for delta in [0]+[j*.005 for i in range(1,41) for j in [i,-i]]:
  d=5.8+delta;pts=[P(u+du,d+dd,0) for du,dd in [(-.09,-.04),(.09,-.04),(.09,.04),(-.09,.04)]];hs=[hit(p,roof) for p in pts]
  if not all(hs):continue
  # Sample footprint densely to ensure no elevated rib is pierced by the foot.
  clear=True
  for du in [-.09,-.045,0,.045,.09]:
   for dd in [-.04,-.02,0,.02,.04]:
    p=P(u+du,d+dd,0);rh=hit(p,roof);bh=hit(p,list(enumerate(ribs)))
    if bh and rh and bh[0]>rh[0]+.001:clear=False
  if clear:chosen=(d,pts,hs);break
 
 if not chosen:
  print('DEBUG CONTACT',u,[(dd,hit(P(u,dd,0),roof),hit(P(u,dd,0),list(enumerate(ribs)))) for dd in [5.5,5.6,5.7,5.8,5.9,6.0]],flush=True)
 assert chosen,('No rib-free contact',u)
 d,pts,hs=chosen;feet=[Vector((p.x,p.y,h[0]+.0001)) for p,h in zip(pts,hs)];tops=[Vector((p.x,p.y,39.65)) for p in pts];vs=feet+tops
 # n,t frame is right-handed for these perimeter points? Recompute normals against center.
 center=sum(vs,Vector())/8
 for ids in [(0,1,2,3),(4,7,6,5),(0,4,5,1),(1,5,6,2),(2,6,7,3),(3,7,4,0)]:
  fp=[vs[i] for i in ids];fc=sum(fp,Vector())/4
  if (fp[1]-fp[0]).cross(fp[2]-fp[0]).dot(fc-center)<0:fp.reverse()
  face(fp,support)
 contacts.append({'u':u,'d':d,'width':.18,'depth':.08,'roof_sources':[h[1] for h in hs],'feet':[list(p) for p in feet],'roof_z':[h[0] for h in hs],'clearance':.0001,'rib_footprint_grid_clear':True})
box(1.8,17.2,5.78,6.00,39.25,39.43,support)
added=[]
for name,(vv,ff) in G.items():
 me=bpy.data.meshes.new(name);me.from_pydata(vv,[],ff);me.materials.append(bpy.data.materials[name]);o=bpy.data.objects.new(name,me);bpy.context.collection.objects.link(o);added.append(o)
meshes=[o for o in scene.objects if o.type=='MESH'];bpy.ops.object.select_all(action='DESELECT')
for o in meshes:o.select_set(True)
bpy.ops.export_scene.gltf(filepath=str(R/'web/takagi.glb'),export_format='GLB',use_selection=True,export_yup=True)
# Preserve validated facade metadata, derive current counts from the exported GLB.
stats_path=R/'source/data/facade_stats.json'
assert hashlib.sha256(stats_path.read_bytes()).hexdigest()=='792b6a9040ed0a35f40cbd475cb24077647f61a141817b597be9c4363cf6149a'
stats=json.loads(stats_path.read_text())
exported=(R/'web/takagi.glb').read_bytes(); gltf=json.loads(exported[20:20+struct.unpack_from('<I',exported,12)[0]])
primitives=[p for node in gltf['nodes'] if 'mesh' in node for p in gltf['meshes'][node['mesh']]['primitives']]
stats.update({'triangles':sum(gltf['accessors'][p['indices']]['count']//3 for p in primitives),'primitives':len(primitives),'bytes':len(exported),'added_triangles':sum(len(o.data.polygons) for o in added),'status':'Bounded historical rooftop billboard; validated facade metadata inherited','billboard_revision':'historical-2025-v1','inherited_stats_sha256':'792b6a9040ed0a35f40cbd475cb24077647f61a141817b597be9c4363cf6149a'})
(R/'source/data/stats.json').write_text(json.dumps(stats,indent=1)+'\n')
(E/'contacts.json').write_text(json.dumps(contacts,indent=2));(E/'build_audit.json').write_text(json.dumps({'removed_triangles':len(removed),'added_triangles':sum(len(o.data.polygons) for o in added),'frame':{'A':list(A),'t':list(t),'n':list(n)},'parameters':{'width':18,'height':12.5,'center_u':9.616,'depth':5.8,'backing':.25,'bottom':39.5,'top':52,'high_body_clearance':6.424813-6.05},'blender':bpy.app.version_string},indent=2))
cam.location=(-2,20,52);cam.rotation_euler=(Vector((-69,98,25))-cam.location).to_track_quat('-Z','Y').to_euler();cam.data.ortho_scale=61
for screen in bpy.data.screens:
 for area in screen.areas:
  for space in area.spaces:
   if space.type=='FILE_BROWSER' and space.params:space.params.directory=b'//'
scene.render.filepath='//renders/'
bpy.context.preferences.filepaths.save_version=0
bpy.ops.wm.save_as_mainfile(filepath=str(R/'source/blender/takagi.blend'))
if '--no-render' in sys.argv:sys.exit()
render('after_full');render('after_sign_normal',True)
# Reimport exact input for true same-scene before views, hiding only final geometry.
for o in meshes:o.hide_render=True
bpy.ops.import_scene.gltf(filepath=str(R/'source/data/baseline.glb'));render('before_full');render('before_sign_normal',True)
