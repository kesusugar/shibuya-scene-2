"""Blender 4.2.3. Run --background --python build.py. Pinned baseline surgical edit.
All coordinates retained in source east/north/z(T.P.-15m); no recentering.
"""
import bpy,json,math,sys,hashlib
from pathlib import Path
from mathutils import Vector
from mathutils.geometry import tessellate_polygon
ROOT=Path(__file__).resolve().parents[2]; E=Path(sys.argv[sys.argv.index('--evidence-dir')+1]) if '--evidence-dir' in sys.argv else ROOT/'source/evidence';E.mkdir(parents=True,exist_ok=True)
assert hashlib.sha256((ROOT/'source/data/baseline.glb').read_bytes()).hexdigest()=='5fe2ee53947ca18f72460da90ef5de1f849c687968a6b623e0db2e1cb5ce218d', 'Pinned baseline mismatch'
assert hashlib.sha256((ROOT/'source/data/plateau.json').read_bytes()).hexdigest()=='91168e63a0f5dfdee3c203fe2d83431b8f059ef5a1f61d017c9e09f99f38e42f', 'Pinned source mismatch'
D=json.loads((ROOT/'source/data/plateau.json').read_text()); refs=json.loads((ROOT/'source/refs/target_surfaces.json').read_text()); S={s['index']:[Vector(p) for p in s['ring'][:-1]] for s in refs}
bpy.ops.wm.read_factory_settings(use_empty=True);bpy.ops.import_scene.gltf(filepath=str(ROOT/'source/data/baseline.glb'))
base=list(bpy.context.scene.objects)
def material(name,c,metal=0,rough=.65):
 m=bpy.data.materials.new(name);m.diffuse_color=(*c,1);m.use_nodes=True;p=m.node_tree.nodes['Principled BSDF'];p.inputs['Base Color'].default_value=(*c,1);p.inputs['Metallic'].default_value=metal;p.inputs['Roughness'].default_value=rough;return m
panel=material('takagi_fitted_warm_panel',(.50,.51,.49),.32,.6); rib=material('takagi_fitted_crown_rib',(.12,.135,.13),.35,.55);glass=material('takagi_fitted_glass',(.095,.17,.18),.35,.3)
def obj(name,verts,faces,mat):
 if name.startswith('takagi_fitted_'):
  nv=[];nf=[]
  for f in faces:
   ring=[Vector(verts[i]) for i in f]
   for tri in tessellate_polygon([ring]):
    ps=[ring[i] for i in tri] if isinstance(tri[0],int) else list(tri)
    if (ps[1]-ps[0]).cross(ps[2]-ps[0]).length<1e-8:continue
    st=len(nv);nv.extend(ps);nf.append([st,st+1,st+2])
  verts,faces=nv,nf
 me=bpy.data.meshes.new(name);me.from_pydata(verts,[],faces);me.materials.append(mat);o=bpy.data.objects.new(name,me);bpy.context.collection.objects.link(o);return o
# Same camera throughout baseline and final. Not a calibrated photograph camera.
def camera(name,loc,target,scale):
 bpy.ops.object.camera_add(location=loc);c=bpy.context.object;c.name=name;c.rotation_euler=(Vector(target)-c.location).to_track_quat('-Z','Y').to_euler();c.data.type='ORTHO';c.data.ortho_scale=scale;return c
cam=camera('crossing_inspection',(-2,20,52),(-69,98,25),61)
scene=bpy.context.scene;scene.camera=cam;scene.render.engine='CYCLES';scene.cycles.samples=24;scene.render.resolution_x=1000;scene.render.resolution_y=1000;scene.render.resolution_percentage=100
scene.world=bpy.data.worlds.new('Inspection studio');scene.world.color=(.65,.65,.65);scene.view_settings.view_transform='Standard';scene.view_settings.look='Medium High Contrast'
bpy.ops.object.light_add(type='AREA',location=(-10,35,95));bpy.context.object.data.energy=170000;bpy.context.object.data.shape='DISK';bpy.context.object.data.size=70
scene.render.image_settings.file_format='PNG';scene.render.film_transparent=False

def render(name):scene.render.filepath=str(E/(name+'.png'));bpy.ops.render.render(write_still=True)
if '--baseline' in sys.argv:
 render('before_full')
 # Actual imported baseline plus source-face identifier surfaces.
 labels=[]
 for k,col in [(105,(.85,.12,.10)),(53,(.08,.5,.8)),(45,(.7,.5,.05)),(12,(.6,.2,.7)),(30,(.15,.7,.35)),(22,(.8,.35,.05))]:
  ring=S[k];n=(ring[1]-ring[0]).cross(ring[2]-ring[0]).normalized();n=n if n.z>=0 or k in (105,53) else -n
  if k==105:n=Vector((.921,-.390,0))
  if k==53:n=Vector((-.414,-.910,0))
  o=obj('source_'+str(k),[p+n*.23 for p in ring],[list(range(len(ring)))],material('id_'+str(k),col));labels.append(o)
  center=sum(ring,Vector())/len(ring)+n*.5;bpy.ops.object.text_add(location=center);t=bpy.context.object;t.data.body=str(k);t.data.size=1.4;t.rotation_euler=cam.rotation_euler;t.data.align_x='CENTER';labels.append(t)
 render('baseline_face_ids');sys.exit()
# Preserve source shell, signs, skirts, and all non-target triangles exactly.
# Cut only original facade overlays with plane distance >0.045m in bounded heights.
def clip(poly,axis,value,above=True):
 out=[]
 for i,a in enumerate(poly):
  b=poly[i-1];fa=a[axis]-value;fb=b[axis]-value;ia=fa>=-1e-8 if above else fa<=1e-8;ib=fb>=-1e-8 if above else fb<=1e-8
  if ia!=ib:out.append(b+(a-b)*(fb/(fb-fa)))
  if ia:out.append(a)
 return out
frames={105:(Vector((-59.952,89.353,0)),Vector((7.496,17.711,0)).normalized(),Vector((.921,-.390,0)).normalized(),14,27.9),53:(Vector((-71.367,94.540,0)),Vector((11.415,-5.187,0)).normalized(),Vector((-.414,-.910,0)).normalized(),15,27.9)}
# Source52 concave roof retessellation only.
roof_ring=[Vector(p) for p in D['surfaces'][52]['ring'][:-1]]
removed=0;unchanged=0
for o in base:
 if o.type!='MESH':continue
 vv=[];ff=[];roof52_original=[]
 for p in o.data.polygons:
  pts=[o.matrix_world@o.data.vertices[i].co for i in p.vertices];target=None
  if o.name=='takagi_roof' and all(any((q-r).length<.0001 for r in roof_ring) for q in pts):
   roof52_original.extend(pts);continue
  if not o.name.endswith(('_wall','_roof')):
   for k,(a,t,n,lo,hi) in frames.items():
    length=19.232 if k==105 else 12.538
    if all(.045<(q-a).dot(n)<.22 and -.04<(q-a).dot(t)<length+.04 for q in pts) and min(q.z for q in pts)<hi and max(q.z for q in pts)>lo:target=(lo,hi);break
  pieces=[pts]
  if target:
   lo,hi=target;pieces=[clip(pts,2,lo,False),clip(pts,2,hi,True)];removed+=1
  else:unchanged+=1
  for poly in pieces:
   if len(poly)<3:continue
   start=len(vv);vv.extend(poly);ff.append(list(range(start,start+len(poly))))
 if roof52_original:
  rr=[min(roof52_original,key=lambda q:(q-r).length).copy() for r in roof_ring]
  for tri in tessellate_polygon([rr]):
   pp=[rr[i] for i in tri] if isinstance(tri[0],int) else list(tri)
   if (pp[1]-pp[0]).cross(pp[2]-pp[0]).z<0:pp.reverse()
   start=len(vv);vv.extend(pp);ff.append(list(range(start,start+3)))
 old=o.data;me=bpy.data.meshes.new(o.name+'_preserved');me.from_pydata(vv,[],ff)
 for m in old.materials:me.materials.append(m)
 if o.name=='takagi_roof':
  me.materials.append(rib)
  for poly in me.polygons:
   ps=[me.vertices[i].co for i in poly.vertices]
   if any(all(any((p-r).length<.0001 for r in S[k]) for p in ps) for k in [45,12,30,22]):poly.material_index=len(me.materials)-1
 o.data=me;o.matrix_world.identity()
# Every added patch is clipped to a triangulation of the true source face.
G={};audit=[]
def patch(k,bounds,mat,offset):
 ring=S[k];n=(ring[1]-ring[0]).cross(ring[2]-ring[0]).normalized()
 if k in frames:a,t,n,_,_=frames[k]
 else:
  if n.z<0:n=-n
  a=ring[0];t=Vector((1,0,0))
 for tri in tessellate_polygon([ring]):
  ps=[ring[i].copy() for i in tri] if isinstance(tri[0],int) else [p.copy() for p in tri]
  # local coordinate stores u,z; true 3d positions interpolated on clip edges.
  for coord,val,above in bounds:
   out=[]
   def scalar(p):return (p-a).dot(t) if coord=='u' else p.z
   for j,p in enumerate(ps):
    q=ps[j-1];fp=scalar(p)-val;fq=scalar(q)-val;ip=fp>=-1e-8 if above else fp<=1e-8;iq=fq>=-1e-8 if above else fq<=1e-8
    if ip!=iq:out.append(q+(p-q)*(fq/(fq-fp)))
    if ip:out.append(p)
   ps=out
   if len(ps)<3:break
  if len(ps)<3:continue
  vs,fs=G.setdefault(mat.name,([],[]));start=len(vs);vs.extend([p+n*offset for p in ps]);fs.append(list(range(start,start+len(ps))));audit.append({'source':k,'offset':offset,'points':[list(p) for p in ps]})
def rect(k,u0,u1,z0,z1,mat,off):
 if k in frames:z0=max(z0,frames[k][3]);z1=min(z1,frames[k][4])
 if z1>z0:patch(k,[('u',u0,True),('u',u1,False),('z',z0,True),('z',z1,False)],mat,off)
# Small seams reveal a darker underlying neutral field. Panel gaps .025m.
rect(105,0,19.232,14,27.9,rib,.135)
for i in range(10):
 for j in range(7):rect(105,i*1.9232+.0125,(i+1)*1.9232-.0125,14+j*1.986+.0125,min(27.9,14+(j+1)*1.986-.0125),panel,.16)
# Two broad groups plus two slots. Source-faithful fitted coordinates, not survey.
for u,w in [(.59,2.05),(.85,2.05),(.74,.44),(.98,.44)]:
 c=u*19.232;rect(105,c-w/2-.065,c+w/2+.065,24.48,26.28,panel,.19);rect(105,c-w/2,c+w/2,24.55,26.21,glass,.195)
 if w>1:
  for x in [c-w/6,c+w/6]:rect(105,x-.025,x+.025,24.55,26.21,panel,.205)
rect(53,0,12.538,15,27.9,glass,.135)
for x in [0,2.5,5,7.5,10,12.538]:rect(53,x-.045,x+.045,15,27.9,panel,.18)
for z in [15,18.225,21.45,24.675,27.9]:rect(53,0,12.538,z-.075,z+.075,panel,.18)
for k in [45,12,30,22]:
 for i in range(40):
  z=28+i*.27
  patch(k,[('z',z,True),('z',z+.065,False)],rib,.055)
for name,(vs,fs) in G.items():obj(name,vs,fs,bpy.data.materials[name])
meshes=[o for o in scene.objects if o.type=='MESH'];bpy.ops.object.select_all(action='DESELECT')
for o in meshes:o.select_set(True)
bpy.ops.export_scene.gltf(filepath=str(ROOT/'web/takagi.glb'),export_format='GLB',use_selection=True,export_yup=True)
stats=json.loads((ROOT/'source/data/baseline_stats.json').read_text());stats.update({'triangles':sum(len(p.vertices)-2 for o in meshes for p in o.data.polygons),'primitives':sum(len(set(p.material_index for p in o.data.polygons)) for o in meshes),'bytes':(ROOT/'web/takagi.glb').stat().st_size,'status':'Bounded photo-fit source105/53 and crown45/12/30/22; off-target prototype retained','facade_revision':'upper-field-v1'});(ROOT/'source/data/stats.json').write_text(json.dumps(stats,indent=1)+'\n')
for screen in bpy.data.screens:
 for area in screen.areas:
  for space in area.spaces:
   if space.type=='FILE_BROWSER' and space.params:space.params.directory=b'//'
scene.render.filepath='//renders/'
bpy.context.preferences.filepaths.save_version=0
bpy.ops.wm.save_as_mainfile(filepath=str(ROOT/'source/blender/takagi.blend'))
(E/'added_surface_audit.json').write_text(json.dumps(audit));(E/'edit_counts.json').write_text(json.dumps({'removed_or_clipped_overlay_triangles':removed,'unchanged_original_triangles':unchanged}))
if '--no-render' in sys.argv:sys.exit()
render('after_full')
cam.data.ortho_scale=31;cam.location=(-2,20,52);cam.rotation_euler=(Vector((-60,98,26))-cam.location).to_track_quat('-Z','Y').to_euler();render('after_close')
cam.location=(-20,80,30);cam.rotation_euler=(Vector((-62,98,24))-cam.location).to_track_quat('-Z','Y').to_euler();cam.data.ortho_scale=42;render('after_front')
cam.location=(-100,30,40);cam.rotation_euler=(Vector((-65,95,23))-cam.location).to_track_quat('-Z','Y').to_euler();cam.data.ortho_scale=50;render('after_side')
