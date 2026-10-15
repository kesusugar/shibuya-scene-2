"""Blender4.2.3: PARCO terrace candidate on the roof22-corrected base, relative portable paths."""
from pathlib import Path
import bpy,bmesh,json,math,sys,hashlib
from mathutils import Vector
from mathutils.geometry import tessellate_polygon
ROOT=Path(__file__).resolve().parents[1];G=ROOT/'geometry';L=json.loads((G/'layout.json').read_text());levels=L['levels'];F4=levels['fourF_z'];F5=levels['fiveF_z'];F6=levels['sixF_z']
assert bpy.app.version[:3]==(4,2,3)
coverage=json.loads((ROOT/'verification/floor_coverage/coverage-proof.json').read_text())
assert coverage['full_coverage_proved'], 'Core base removal requires full coverage proof'
assert hashlib.sha256((ROOT/'inputs/frozen-terrace-layout.json').read_bytes()).hexdigest()==coverage['source_layout_sha256']
proven=json.loads((ROOT/'inputs/frozen-terrace-layout.json').read_text())
assert L['core_polygon']==proven['core_polygon'] and L['corner_floor_polygon']==proven['corner_floor_polygon'] and L['levels']==proven['levels'], 'Coverage proof no longer matches geometry'
bpy.ops.wm.read_factory_settings(use_empty=True);bpy.ops.import_scene.gltf(filepath=str(G/'authorized-shell-cut.glb'));originals=list(bpy.context.scene.objects)
def material(name,color,rough=.65,metal=0,alpha=1):
 m=bpy.data.materials.new(name);m.diffuse_color=(*color,alpha);m.use_nodes=True;bs=m.node_tree.nodes.get('Principled BSDF');bs.inputs['Base Color'].default_value=(*color,1);bs.inputs['Roughness'].default_value=rough;bs.inputs['Metallic'].default_value=metal;bs.inputs['Alpha'].default_value=alpha
 if alpha<1:m.surface_render_method='DITHERED';m.use_transparency_overlap=False
 return m
M={'structure':material('parco_terrace_pale_structure',(.67,.675,.65)), 'floor':material('parco_terrace_stone_paving',(.46,.47,.45)), 'glass':material('parco_terrace_reflective_glass',(.32,.44,.45),.23,.22),'frame':material('parco_terrace_anodized_frame',(.48,.51,.51),.32,.42),'rail':material('parco_terrace_clear_rail_glass',(.54,.65,.66),.20,.12,.28),'retained':bpy.data.materials['parco_wall'],'retained_spandrel':bpy.data.materials['parco_spandrel']}
V={k:[] for k in M};FS={k:[] for k in M};LOG=[]
def mesh(k,vs,fs,label,**meta):
 start=len(V[k]);V[k]+=list(map(tuple,vs));FS[k]+=[tuple(start+i for i in f) for f in fs];LOG.append({'label':label,'material':k,'vertices':len(vs),'faces':len(fs),**meta})
def prism_poly(k,xy,z0,z1,label):
 pts=[Vector((x,y,z0)) for x,y in xy];tris=tessellate_polygon([pts]);idx={tuple(v):i for i,v in enumerate(pts)};nn=len(pts);fs=[]
 for tr in tris:
  ii=tuple(v if isinstance(v,int) else idx[tuple(v)] for v in tr);fs.extend([tuple(reversed(ii)),tuple(nn+j for j in ii)])
 for i in range(nn):j=(i+1)%nn;fs.append((i,j,j+nn,i+nn))
 mesh(k,[tuple(p) for p in pts]+[(p.x,p.y,z1) for p in pts],fs,label,z=[z0,z1],plan=[list(p) for p in xy])
def beam(k,a,b,z0,z1,width,label):
 a=Vector(a);b=Vector(b);d=(b-a).normalized();n=Vector((-d.y,d.x))*width/2;prism_poly(k,[a+n,b+n,b-n,a-n],z0,z1,label)
def post(xy,z0,z1,width,label):
 x,y=xy;prism_poly('structure',[(x-width/2,y-width/2),(x+width/2,y-width/2),(x+width/2,y+width/2),(x-width/2,y+width/2)],z0,z1,label)
def wall(k,a,b,z0,z1,label,width=.12):beam(k,a,b,z0,z1,width,label)
def rail(a,b,z,label):
 a=Vector(a);b=Vector(b);ln=(b-a).length;n=max(1,round(ln/1.65));u=(b-a)/n
 for i in range(n):
  aa=a+u*i;bb=a+u*(i+1);wall('rail',aa+u.normalized()*.025,bb-u.normalized()*.025,z+.1,z+1.1,label+'_panel',.022)
 for i in range(n+1):
  p=a+u*i;beam('frame',p-Vector((.018,0)),p+Vector((.018,0)),z,z+1.13,.035,label+'_post')
 beam('frame',a,b,z+1.10,z+1.135,.04,label+'_handrail')
def glazeline(a,b,z0,z1,label,intervals):
 a=Vector(a);b=Vector(b);ln=(b-a).length;n=max(1,round(ln/2.2));u=(b-a)/n
 for i in range(n):wall('glass',a+u*i,a+u*(i+1),z0,z1,label+'_pane',.055)
 for i in range(n+1):
  p=a+u*i;beam('frame',p-Vector((.03,0)),p+Vector((.03,0)),z0,z1,.065,label+'_mullion')
 for z in [z0]+intervals+[z1]:beam('frame',a,b,z-.035,z+.035,.075,label+'_transom')
# Retained fragments outside authorized apertures, not an all-face delete.
for f in json.loads((G/'retained-wall-fragments.json').read_text()):
 vs=f['vertices'];mesh('retained',vs,[(0,i,i+1) for i in range(1,len(vs)-1)],'retained_source_'+str(f['source_face']),source_triangle=f['source_triangle'])
for f in json.loads((G/'retained-spandrel-fragments.json').read_text()):
 vs=f['vertices'];mesh('retained_spandrel',vs,[(0,i,i+1) for i in range(1,len(vs)-1)],'retained_spandrel_'+str(f['source_face']),source_triangle=f['source_triangle'])
# Separate plazafloor and two-storey soffit are metre-deep geometry.
for key,label in [('east_floor_polygon','east_plaza'),('corner_floor_polygon','core_wrap')]:
 prism_poly('floor',L[key],F4-.35,F4,label+'_4F_floor')
 z=34.7 if key=='east_floor_polygon' else 39.3
 prism_poly('structure',L[key],z,z+.28,label+'_soffit')
wall('structure',*L['north_side_return'],F4,39.3,'north_scope_end_return',.25)
wall('structure',*L['north_back_return'],F4,39.3,'north_recessed_back_return',.20)
wall('structure',L['east_floor_polygon'][1],L['core_polygon'][4],34.7,39.3,'stepped_soffit_transition_return',.18)
# Taller corner; only the western north return changes to5F. Under it original wall is retained.
prism_poly('floor',L['north_fiveF_polygon'],F5-.30,F5,'north_return_5F_walkway')
prism_poly('floor',L['core_west_fiveF_walkway'],F5-.30,F5,'core_west_5F_link')
# Retained substantial glazed lift core, closed with floor/roof; glazing is not a frontage decal.
core=L['core_polygon'];# Redundant core_base omitted: retained core-wrap floor fully covers its XY and Z volume.
prism_poly('structure',core,39.12,39.3,'core_cap')
for z in [F5,F6]:prism_poly('floor',core,z-.24,z,'core_internal_floor')
for i,(a,b) in enumerate(zip(core,core[1:]+core[:1])):
 glazeline(a,b,F4,39.3,'retained_lift_core_side_'+str(i),[F5,F6])
# Inferred opaque shaft volumes sit inside, never replacing the entire corner with empty space.
for x,y in [(-136.7,299.3),(-129.9,301.4)]:
 prism_poly('structure',[(x-1.6,y-1.4),(x+1.6,y-1.4),(x+1.6,y+1.4),(x-1.6,y+1.4)],F4,39.12,'core_internal_shaft_inferred')
# Stepped/angled recessed shopfront from the4F plan. First long plane is~8–12m behind east line, not constant8m.
shop=L['shopfront_polyline']
for i,(a,b) in enumerate(zip(shop,shop[1:])):glazeline(a,b,F4,34.7,'recessed_shopfront_'+str(i),[F5])
# Southern terrace termination: physical return wall. Northern core-side closure remains open to circulation.
wall('structure',L['east_floor_polygon'][0],shop[0],F4,34.7,'south_terrace_sidewall',.25)
# Source171 columns estimated from visible pale supports, set inward from boundary rather than paper strips.
for zone in L['zones']:
 a=Vector(zone['a']);b=Vector(zone['b']);tt=(b-a).normalized();inward=Vector((-tt.y,tt.x))
 if zone['face']==171:
  for u in [3.6,16.1]:post(a+tt*u+inward*1.15,F4,34.7,.60,'east_pale_support')
  rail(a+inward*.30,b+inward*.30,F4,'east_outer_balustrade')
 elif zone['face']==108:
  post(a+tt*1.1+inward*1.1,F4,39.3,.58,'corner_pale_support')
  rail(a+inward*.30,b+inward*.30,F4,'corner_outer_balustrade')
 else:
  for u in [7.9,17.0]:post(a+tt*u+inward*1.05,F4 if u<11 else F5,39.3,.60,'north_pale_support')
  rail(a+inward*.30,a+tt*11+inward*.30,F4,'north_4F_balustrade')
  rail(a+tt*11+inward*.30,b+inward*.30,F5,'north_5F_balustrade')
#4Fto5F stairs behind retained core, with actual treads/risers/side stringers.
def stair(spec,z0,label):
 a=Vector(spec['start']);b=Vector(spec['end']);d=(b-a);n=Vector((-d.y,d.x)).normalized()*spec['width']/2;N=spec['steps'];rise=spec['rise'];step=d/N
 for i in range(N):
  aa=a+step*i;bb=a+step*(i+1);zt=z0+rise*(i+1)/N;prism_poly('floor',[aa+n,bb+n,bb-n,aa-n],zt-.18,zt,label+'_tread')
  # Explicit risers seal each step; do not fill the air below as a giant wedge.
  wall('floor',aa-n,aa+n,zt-rise/N,zt,label+'_riser',.05)
 for side in [-1,1]:
  aa=a+n*side;bb=b+n*side
  # Sloped solid stringer via8vertices.
  tangent=d.normalized();w=Vector((-tangent.y,tangent.x))*.06;vs=[]
  for p,z in [(aa,z0-.22),(bb,z0+rise-.22),(bb,z0+rise-.02),(aa,z0-.02)]:vs.extend([(p.x-w.x,p.y-w.y,z),(p.x+w.x,p.y+w.y,z)])
  mesh('structure',vs,[(0,2,3,1),(2,4,5,3),(4,6,7,5),(6,0,1,7),(0,6,4,2),(1,3,5,7)],label+'_stringer')
  # Posts and sloped handrail.
  for i in range(0,N+1,5):
   p=aa+(bb-aa)*i/N;z=z0+rise*i/N;beam('frame',p-Vector((.02,0)),p+Vector((.02,0)),z,z+1.1,.04,label+'_rail_post')
  vs=[]
  for p,z in [(aa,z0+1.07),(bb,z0+rise+1.07),(bb,z0+rise+1.12),(aa,z0+1.12)]:vs.extend([(p.x-w.x/3,p.y-w.y/3,z),(p.x+w.x/3,p.y+w.y/3,z)])
  mesh('frame',vs,[(0,2,3,1),(2,4,5,3),(4,6,7,5),(6,0,1,7),(0,6,4,2),(1,3,5,7)],label+'_sloped_handrail')
stair(L['core_south_stair'],F4,'core_4F_to5F_stair')
# The map shows an eastern3Fto4F escalator, but its lower opening conflicts with preserved source roof47.
# Do not fake/cut it: represent only its4F upper landing, and disclose the unmodeled lower connection.
e=L['east_plaza_stair'];a=Vector(e['end']);t=(Vector(e['end'])-Vector(e['start'])).normalized();n=Vector((-t.y,t.x))*e['width']/2
prism_poly('floor',[a+n,a+t*1.3+n,a+t*1.3-n,a-n],F4-.2,F4,'east_vertical_route_upper_landing_only')
added=[]
for k in M:
 me=bpy.data.meshes.new('prototype_terrace_'+k);me.from_pydata(V[k],[],FS[k]);me.materials.append(M[k]);me.update()
 if not k.startswith('retained'):
  bm=bmesh.new();bm.from_mesh(me);bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces));bm.to_mesh(me);bm.free()
 o=bpy.data.objects.new('prototype_terrace_'+k,me);bpy.context.collection.objects.link(o);o['candidate_only']=True;o['scope']='171, upper108, short eastern152';added.append(o)
bpy.ops.object.select_all(action='DESELECT')
for o in added:o.select_set(True)
bpy.context.view_layer.objects.active=added[0]
bpy.ops.export_scene.gltf(filepath=str(G/'additions.glb'),export_format='GLB',use_selection=True,export_yup=True,export_extras=True,export_cameras=False,export_lights=False)
(G/'component-log.json').write_text(json.dumps(LOG,indent=2)+'\n')
# Save source-neutral authoring view. No copyrighted references embedded.
scene=bpy.context.scene;scene.render.engine='CYCLES';scene.cycles.samples=24;scene.cycles.use_denoising=True;scene.render.resolution_x=1200;scene.render.resolution_y=1100;scene.render.resolution_percentage=100
scene.world=bpy.data.worlds.new('Review');scene.world.use_nodes=True;scene.world.node_tree.nodes['Background'].inputs[0].default_value=(.7,.72,.75,1);scene.world.node_tree.nodes['Background'].inputs[1].default_value=.6
bpy.ops.object.light_add(type='SUN');sun=bpy.context.object;sun.rotation_euler=Vector((-.65,-.55,-1)).to_track_quat('-Z','Y').to_euler();sun.data.energy=2.1;sun.data.angle=.12
bpy.ops.object.camera_add(location=(-74,354,10.1));cam=bpy.context.object;cam.rotation_euler=(Vector((-126,296,37))-cam.location).to_track_quat('-Z','Y').to_euler();cam.data.lens=50;scene.camera=cam
text=bpy.data.texts.new('CANDIDATE_README');text.write('PARCO scoped terrace production candidate. Roof22-corrected base retained. NOT accepted or deployed runtime replacement. Source footprint/roof/office geometry unchanged. No copyrighted drawings embedded. See README and registration residuals; floor levels and supports are bounded inference. Source84/141 notch untouched. Lower eastern escalator opening not modeled because roof preservation forbids its excavation.\n')
bpy.ops.wm.save_as_mainfile(filepath=str(ROOT/'parco_terrace_candidate.blend'))
print('ADDED_GEOMETRY_COMPONENTS',len(LOG))
