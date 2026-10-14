"""Station west service-facility B prototype, source shell retained; estimated cladding/vent details.
Blender 4.2.3 -b --python-exit-code 1 -t 4 -P script -- parts.json layout.json ground.glb outdir
"""
import bpy,bmesh,json,math,sys
from pathlib import Path
from mathutils import Vector
from mathutils.bvhtree import BVHTree
src,config,ground,out=sys.argv[sys.argv.index('--')+1:][:4]
assert bpy.app.version==(4,2,3)
D=json.loads(Path(src).read_text());F=json.loads(Path(config).read_text());ROOT=Path(config).parent;OUT=Path(out);OUT.mkdir(parents=True,exist_ok=True)
bpy.ops.wm.read_factory_settings(use_empty=True);bpy.ops.import_scene.gltf(filepath=ground)
bm=bmesh.new()
for ob in list(bpy.context.scene.objects):
 if ob.type=='MESH' and ob.name.startswith(('ground_road','ground_sidewalk','ground_intersection','ground_fill')):
  me=ob.data.copy();me.transform(ob.matrix_world);bm.from_mesh(me);bpy.data.meshes.remove(me)
bvh=BVHTree.FromBMesh(bm);bm.free()
for ob in list(bpy.context.scene.objects):bpy.data.objects.remove(ob,do_unlink=True)
M={};GROUP={}
for name,rgb,rough,metal in [('ss_wall',(.74,.77,.75),.65,.1),('ss_roof',(.43,.47,.46),.8,0),('ss_joint',(.49,.54,.52),.7,0),('ss_metal',(.47,.51,.50),.45,.5),('ss_vent',(.16,.20,.19),.55,.3),('ss_plinth',(.57,.60,.58),.85,0)]:
 m=bpy.data.materials.new(name);m.use_nodes=True;p=m.node_tree.nodes['Principled BSDF'];p.inputs['Base Color'].default_value=(*rgb,1);p.inputs['Roughness'].default_value=rough;p.inputs['Metallic'].default_value=metal;M[name]=m

def face(name,pts):
 if len(pts)>1 and (Vector(pts[0])-Vector(pts[-1])).length<1e-6:pts=pts[:-1]
 bm=GROUP.setdefault(name,bmesh.new());f=bm.faces.new([bm.verts.new(p) for p in pts]);f.normal_update()
def box(center,size,name,angle=0):
 x,y,z=center;w,d,h=size;c,s=math.cos(angle),math.sin(angle)
 p=[(x+c*a-s*b,y+s*a+c*b,z+k) for a,b,k in [(-w/2,-d/2,-h/2),(w/2,-d/2,-h/2),(w/2,d/2,-h/2),(-w/2,d/2,-h/2),(-w/2,-d/2,h/2),(w/2,-d/2,h/2),(w/2,d/2,h/2),(-w/2,d/2,h/2)]]
 for ids in [(0,3,2,1),(4,5,6,7),(0,1,5,4),(1,2,6,5),(2,3,7,6),(3,0,4,7)]:face(name,[p[i] for i in ids])
for part in D:
 for s in part['surfaces']:face('ss_roof' if s['kind']=='RoofSurface' else 'ss_wall',s['ring'])
# Original rectangular shell edges are from PLATEAU, no shifted/scaled wrapper.
corners=[Vector((*p,0)) for p in F['corners_xy_m']];base=F['base_tp_m']-15;top=F['top_tp_m']-15;samples=[];skirt_segments=0
for A,B in zip(corners,corners[1:]+corners[:1]):
 T=(B-A).normalized();N=Vector((-T.y,T.x,0));L=(B-A).length
 def panel(u,z,w,h,name,offset=.025):
  c=A+T*u+N*offset+Vector((0,0,z));face(name,[c-T*w/2-Vector((0,0,h/2)),c-T*w/2+Vector((0,0,h/2)),c+T*w/2+Vector((0,0,h/2)),c+T*w/2-Vector((0,0,h/2))])
 for u in range(3,int(L),3):panel(u,(base+top)/2,F['joint_width_m'],top-base,'ss_joint')
 for z in F['horizontal_joint_tp_m']:panel(L/2,z-15,L,F['joint_width_m'],'ss_joint')
 p=(A+B)/2;box((p.x,p.y,top-.045),(L,.30,.09),'ss_metal',math.atan2(T.y,T.x))
 # A skirt extends only down to local C2a ground; roof datum and source shell do not move.
 hits=[]
 for i in range(13):
  p=A.lerp(B,i/12)+N*.06;hit=bvh.ray_cast(Vector((p.x,p.y,50)),Vector((0,0,-1)))[0]
  hits.append((p,hit.z if hit else None))
  if hit:samples.append({'x':round(p.x,3),'y':round(p.y,3),'tp':round(hit.z+15,3)})
 for (a,za),(b,zb) in zip(hits,hits[1:]):
  if za is not None and zb is not None and max(za,zb)<base-.01:
   face('ss_plinth',[(a.x,a.y,za),(a.x,a.y,base),(b.x,b.y,base),(b.x,b.y,zb)]);skirt_segments+=1
# Short east face: a shallow standard louver case, type/placement explicitly estimated.
A,B=corners[1],corners[2];T=(B-A).normalized();N=Vector((-T.y,T.x,0));L=(B-A).length;angle=math.atan2(T.y,T.x);z=F['vent_center_tp_m']-15;w,h=F['vent_size_m']
p=(A+B)/2+N*.06
box((p.x,p.y,z),(w,.10,h),'ss_vent',angle)
for dz in [-h/2,h/2]:box((p.x+N.x*.08,p.y+N.y*.08,z+dz),(w+.12,.12,.06),'ss_metal',angle)
for u in [-w/2,w/2]:
 q=p+T*u+N*.08;box((q.x,q.y,z),(.06,.12,h),'ss_metal',angle)
for i in range(9):box((p.x+N.x*.085,p.y+N.y*.085,z-h/2+(i+.5)*h/9),(w,.16,.035),'ss_metal',angle)
# Claude review R2 (2026-10-14): from the Hachiko plaza this block reads in 2025-10/11 photographs as a construction
# frontage, not a blank wall: a white site hoarding at street level, scaffolding in front of the plaza faces and a
# large billboard on it (SC04 2025-10-10 "indeed PLUS"; the 2025-11 hachiko.jpg shows a different campaign on the same
# frame). Placement on this PLATEAU shell is an inference from matching view directions; sizes are estimates.
for name,rgb,rough,metal in [('ss_scaffold',(.55,.57,.58),.45,.6),('ss_hoarding',(.86,.87,.86),.7,0),('ss_billboard_frame',(.06,.065,.07),.5,.4)]:
 m=bpy.data.materials.new(name);m.use_nodes=True;p=m.node_tree.nodes['Principled BSDF'];p.inputs['Base Color'].default_value=(*rgb,1);p.inputs['Roughness'].default_value=rough;p.inputs['Metallic'].default_value=metal;M[name]=m
SC=F['scaffold'];sign_faces=[]
for edge in SC['faces']:
 A,B=corners[edge],corners[(edge+1)%4];T=(B-A).normalized();N=Vector((-T.y,T.x,0));L=(B-A).length;ang=math.atan2(T.y,T.x)
 o=SC['offset_m'];z0=base;z1=top+SC['above_roof_m']
 n=max(2,round(L/SC['bay_m']));
 for i in range(n+1):
  for k,off in enumerate((o,o+SC['depth_m'])):
   p=A+T*(L*i/n)+N*off;box((p.x,p.y,(z0+z1)/2),(.05,.05,z1-z0),'ss_scaffold')
 z=z0+SC['lift_m']
 while z<=z1+1e-6:
  for off in (o,o+SC['depth_m']):
   p=(A+B)/2+N*off;box((p.x,p.y,z),(L,.045,.045),'ss_scaffold',ang)
  for i in range(n+1):
   p=A+T*(L*i/n)+N*(o+SC['depth_m']/2);box((p.x,p.y,z),(.04,SC['depth_m'],.04),'ss_scaffold',ang)
  # working deck boards on every second lift
  if round((z-z0)/SC['lift_m'])%2==0:
   p=(A+B)/2+N*(o+SC['depth_m']/2);box((p.x,p.y,z+.03),(L,SC['depth_m']-.05,.03),'ss_scaffold',ang)
  z+=SC['lift_m']
 # diagonal bracing in alternate bays of the outer plane
 for i in range(0,n,2):
  a=A+T*(L*i/n)+N*(o+SC['depth_m']);b=A+T*(L*(i+1)/n)+N*(o+SC['depth_m'])
  for zz in [z0+SC['lift_m']*j for j in range(int((z1-z0)/SC['lift_m']))]:
   d=Vector((b.x-a.x,b.y-a.y,SC['lift_m']));mid=Vector((a.x,a.y,zz))+d/2
   bmx=GROUP.setdefault('ss_scaffold',bmesh.new());cone=bmesh.ops.create_cone(bmx,cap_ends=True,segments=4,radius1=.02,radius2=.02,depth=d.length)
   q=d.to_track_quat('Z','Y')
   for v in cone['verts']:v.co.rotate(q);v.co+=mid
 # white site hoarding along the plaza, with panel seams
 H=F['hoarding']['height_m'];ho=F['hoarding']['offset_m']
 p=(A+B)/2+N*ho;box((p.x,p.y,base+H/2),(L+2*ho*0,.06,H),'ss_hoarding',ang)
 for i in range(int(L/1.8)+1):
  q=A+T*min(L,i*1.8)+N*(ho+.04);box((q.x,q.y,base+H/2),(.03,.02,H),'ss_joint',ang)
 if edge==SC['billboard_face']:
  BB=F['billboard'];c=(A+B)/2+N*(o+SC['depth_m']+.25);zc=base+BB['bottom_above_base_m']+BB['height_m']/2
  box((c.x,c.y,zc),(BB['width_m']+.5,.25,BB['height_m']+.5),'ss_billboard_frame',ang)
  f=c+N*.13;w,h=BB['width_m'],BB['height_m']
  sign_faces.append([f-T*w/2+Vector((0,0,zc-h/2)),f+T*w/2+Vector((0,0,zc-h/2)),f+T*w/2+Vector((0,0,zc+h/2)),f-T*w/2+Vector((0,0,zc+h/2))])
counts={}
for name,bm in GROUP.items():
 bmesh.ops.triangulate(bm,faces=bm.faces[:]);me=bpy.data.meshes.new(name);bm.to_mesh(me);bm.free();me.materials.append(M[name]);me.calc_loop_triangles();ob=bpy.data.objects.new(name,me);bpy.context.collection.objects.link(ob);counts[name]={'triangles':len(me.loop_triangles),'vertices':len(me.vertices)}
bpy.ops.export_scene.gltf(filepath=str(OUT/'station-service.glb'),export_format='GLB',export_yup=True)
for ob in list(bpy.context.scene.objects):bpy.data.objects.remove(ob,do_unlink=True)
sm=bpy.data.materials.new('ss_sign_billboard');sm.use_nodes=True;bp=sm.node_tree.nodes['Principled BSDF'];tx=sm.node_tree.nodes.new('ShaderNodeTexImage')
tx.image=bpy.data.images.load(str(ROOT.parent/'textures'/F['billboard']['texture']));sm.node_tree.links.new(tx.outputs['Color'],bp.inputs['Base Color']);sm.node_tree.links.new(tx.outputs['Color'],bp.inputs['Emission Color']);bp.inputs['Emission Strength'].default_value=1;bp.inputs['Roughness'].default_value=.7
SB=bmesh.new();uv=SB.loops.layers.uv.verify()
for quad in sign_faces:
 fc=SB.faces.new([SB.verts.new(p) for p in quad])
 for l,t in zip(fc.loops,[(1,0),(0,0),(0,1),(1,1)]):l[uv].uv=t   # seen from outside, +T is the viewer's left
me=bpy.data.meshes.new('ss_sign_billboard');SB.to_mesh(me);SB.free();me.materials.append(sm);bpy.context.collection.objects.link(bpy.data.objects.new('ss_sign_billboard',me))
bpy.ops.export_scene.gltf(filepath=str(OUT/'signs-2025-10.glb'),export_format='GLB',export_yup=True)
points=[p for b in D for s in b['surfaces'] for p in s['ring']]
(OUT/'viewer.json').write_text(json.dumps({'planBounds':[min(p[0] for p in points),min(p[1] for p in points),max(p[0] for p in points),max(p[1] for p in points)],'groundElevationTP':15,'layers':{'signs':'signs-2025-10.glb'}},indent=2)+'\n')
for mode in ['day','night']:(OUT/f'emissive_{mode}.json').write_text(json.dumps({'ss_sign_billboard':{'kind':'led','emit':[1,1,1],'estr':.6 if mode=='night' else 0}})+'\n')
(ROOT/'stats.json').write_text(json.dumps({'source_ids':[p['id'] for p in D],'datum_tp_m':15,'roof_deviation_vs_plateau_m':0,'ground_samples':samples,'ground_skirt_segments':skirt_segments,'objects':counts,'triangles':sum(v['triangles'] for v in counts.values()),'status':'B prototype. Association to October18 white service facility inferred, identity/facade coverage unconfirmed. Original PLATEAU shell/roof preserved; panel joints/vent estimated, no reference texture or invented illuminated windows.'},indent=2)+'\n')
print('STATION SERVICE',sum(v['triangles'] for v in counts.values()),'ground samples',len(samples),'skirt segments',skirt_segments)
