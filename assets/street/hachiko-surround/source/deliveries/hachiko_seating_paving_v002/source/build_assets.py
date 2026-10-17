"""Blender 4.2.3: isolated seating/stone/rail components and clearly marked layout candidates.
Run: blender -b --python-exit-code 1 -t 4 -P source/build_assets.py -- [--render]
No original scene, statue, tree, shrub, ground or repository file is read or changed.
"""
import bpy,bmesh,math,json,sys
from pathlib import Path
from mathutils import Vector
ROOT=Path(__file__).resolve().parents[1];TEX=ROOT/'textures';WEB=ROOT/'web';QA=ROOT/'qa';PRE=ROOT/'previews'
for p in (WEB,QA,PRE):p.mkdir(exist_ok=True)
bpy.ops.wm.read_factory_settings(use_empty=True)
C=bpy.data.collections.new('CURRENT_FOOTPRINT_COMPONENTS');bpy.context.scene.collection.children.link(C)
D=bpy.data.collections.new('REFERENCE_LAYOUT_CANDIDATES_NOT_CURRENT');bpy.context.scene.collection.children.link(D)
current_collection=C
mats={}
def texnode(m,file,color=True):
 n=m.node_tree.nodes.new('ShaderNodeTexImage');im=bpy.data.images.load(str(TEX/file),check_existing=True)
 if not color:im.colorspace_settings.name='Non-Color'
 im.pack();n.image=im;return n

def mat(name,col,rough=.8,metal=0,texture=False):
 m=bpy.data.materials.new(name);m.use_nodes=True;m.diffuse_color=(*col,1);b=m.node_tree.nodes.get('Principled BSDF');b.inputs['Base Color'].default_value=(*col,1);b.inputs['Roughness'].default_value=rough;b.inputs['Metallic'].default_value=metal
 if texture:
  a=texnode(m,'granite_basecolor.png');m.node_tree.links.new(a.outputs['Color'],b.inputs['Base Color'])
  a=texnode(m,'granite_roughness.png',False);m.node_tree.links.new(a.outputs['Color'],b.inputs['Roughness'])
  a=texnode(m,'granite_normal.png',False);n=m.node_tree.nodes.new('ShaderNodeNormalMap');n.inputs['Strength'].default_value=.75;m.node_tree.links.new(a.outputs['Color'],n.inputs['Color']);m.node_tree.links.new(n.outputs['Normal'],b.inputs['Normal'])
 mats[name]=m;return m
mat('speckled_granite',(.16,.17,.18),texture=True)
mat('mortar_dark',(.055,.065,.07),.96)
steel=mat('brushed_stainless',(.54,.58,.62),.3,.87);b=steel.node_tree.nodes.get('Principled BSDF');n=texnode(steel,'steel_roughness.png',False);steel.node_tree.links.new(n.outputs['Color'],b.inputs['Roughness'])
mat('fixture_frame',(.025,.033,.037),.45,.65)
mat('fixture_glass_nonemissive',(.20,.235,.22),.5,.1)
mat('support_dark_metal',(.13,.145,.15),.45,.8)
mat('preview_neutral_ground',(.17,.17,.16),.95)
mat('scale_reference_only',(.18,.19,.20),.8)

def finish(o,name,material):
 o.name=name
 for co in list(o.users_collection):co.objects.unlink(o)
 current_collection.objects.link(o);o.data.materials.append(mats[material])
 # UVs in actual meter-scale space; tangents exported normally. No reflected scale.
 if o.type=='MESH':
  if not o.data.uv_layers:o.data.uv_layers.new(name='UVMap')
  for po in o.data.polygons:
   normal=po.normal;axis=max(range(3),key=lambda a:abs(normal[a]));uvaxes=[x for x in range(3) if x!=axis]
   for li in po.loop_indices:
    co=o.data.vertices[o.data.loops[li].vertex_index].co
    o.data.uv_layers.active.data[li].uv=(co[uvaxes[0]]/.65,co[uvaxes[1]]/.65)
  bm=bmesh.new();bm.from_mesh(o.data);bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces));bm.to_mesh(o.data);bm.free();o.data.update()
 return o

def box(name,loc,size,material,bevel=0):
 bpy.ops.mesh.primitive_cube_add(size=1,location=loc);o=bpy.context.object;o.scale=size;bpy.ops.object.transform_apply(location=False,rotation=False,scale=True)
 if bevel:
  mod=o.modifiers.new('small physical edge radius','BEVEL');mod.width=bevel;mod.segments=2;bpy.ops.object.modifier_apply(modifier=mod.name)
 return finish(o,name,material)

def tube(name,p,q,r,material='brushed_stainless',verts=20):
 p,q=Vector(p),Vector(q);bpy.ops.mesh.primitive_cylinder_add(vertices=verts,radius=r,depth=(q-p).length,end_fill_type='NGON',location=(p+q)/2);o=bpy.context.object;o.rotation_euler=(q-p).to_track_quat('Z','Y').to_euler();bpy.ops.object.transform_apply(location=False,rotation=True,scale=True)
 for f in o.data.polygons:f.use_smooth=len(f.vertices)==4
 return finish(o,name,material)

def join_roles(objects,prefix):
 groups={}
 for o in objects:
  role=o.get('role','other');groups.setdefault(role,[]).append(o)
 result=[]
 for role,oo in groups.items():
  bpy.ops.object.select_all(action='DESELECT')
  for o in oo:o.select_set(True)
  bpy.context.view_layer.objects.active=oo[0]
  if len(oo)>1:bpy.ops.object.join()
  o=oo[0];o.name=prefix+'__'+role;o['role']=role;result.append(o)
 return result

def mark(o,role):o['role']=role;return o

assets={}
for side,x0,x1 in [('left',-3.1,-.75),('right',.75,3.1)]:
 objects=[]
 def B(*args,role='stone',**kwargs):
  o=box(*args,**kwargs);mark(o,role);objects.append(o);return o
 def U(*args,role='rails',**kwargs):
  o=tube(*args,**kwargs);mark(o,role);objects.append(o);return o
 y=-1;dep=.75;t=.22;h=.52;length=x1-x0
 # Exact inherited outer envelope; closer visual detail is authored, not a dimensional survey.
 # Narrow vertical face modules and individually jointed caps follow the July 2025 photo.
 count=16;step=length/count
 for k in range(count):
  x=x0+(k+.5)*step
  for tag,yy in [('front',y-t/2),('rear',y-dep+t/2)]:
   B(f'{side}_{tag}_slab_{k:02d}',(x,yy,h/2),(step-.004,t,h),'speckled_granite',.0018)
   B(f'{side}_{tag}_cap_{k:02d}',(x,yy,h+.035),(step-.003,.27,.07),'speckled_granite',.003)
 # End returns retain the accepted rectangular planter outline, but do not create a new soil/shrub mesh.
 for tag,x in [('outer',x0+t/2),('inner',x1-t/2)]:
  B(f'{side}_{tag}_return',(x,y-dep/2,h/2),(t,dep-2*t-.003,h),'speckled_granite',.002)
 # Recessed joint backing stays fully within existing wall dimensions, below cap.
 for yy in [y-t/2,y-dep+t/2]:B(f'{side}_mortar',( (x0+x1)/2,yy,h/2),(length-.006,t-.008,h-.006),'mortar_dark',role='stone')
 yf=y+.12;yb=yf-.22;zf=.65;zb=.81
 for tag,yy,zz in [('front',yf,zf),('rear',yb,zb)]:
  U(f'{side}_{tag}_tube',(x0+.05,yy,zz),(x1-.05,yy,zz),.035)
  # Small end cap seams, independent of the cylinder end surface.
  for x in [x0+.052,x1-.052]:U(f'{side}_{tag}_end_seam',(x-.001,yy,zz),(x+.001,yy,zz),.0357,'support_dark_metal',role='rail_hardware')
 for k in range(4):
  x=x0+.08+k*(length-.16)/3
  U(f'{side}_inclined_tie_{k}',(x,yf,zf),(x,yb,zb),.014,role='rail_hardware')
  U(f'{side}_leg_{k}',(x,y+.02,.01),(x,y+.02,zf),.018,'support_dark_metal',role='rail_hardware')
  B(f'{side}_footplate_{k}',(x,y+.02,.009),(.060,.058,.014),'support_dark_metal',.003,role='rail_hardware')
  # Bolt heads are secondary inference, small and reversible.
  for dx in [-.020,.020]:U(f'{side}_anchor_{k}',(x+dx,y+.02,.016),(x+dx,y+.02,.019),.0032,'brushed_stainless',verts=8,role='rail_hardware')
 # One visible low horizontal fixture per side, rather than asserting four unknown lamps.
 mid=(x0+x1)/2;fy=y+.005
 B(f'{side}_recessed_fixture_frame',(mid,fy,.125),(.51,.012,.17),'fixture_frame',.003,role='lighting_detail')
 B(f'{side}_recessed_fixture_glass',(mid,fy+.007,.125),(.466,.003,.128),'fixture_glass_nonemissive',.001,role='lighting_detail')
 for zz in [.098,.126,.154]:B(f'{side}_fixture_louvre',(mid,fy+.010,zz),(.464,.003,.006),'support_dark_metal',.0005,role='lighting_detail')
 objects=join_roles(objects,'current_'+side)
 root=bpy.data.objects.new('current_'+side+'_statue_local_origin',None);C.objects.link(root);root['status']='Current inherited footprint, photo-informed surface detail; ground anchor still required'
 for o in objects:o.parent=root
 assets['current_'+side]=[root]+objects

# Partial curved front edges ONLY. No reconstructed whole garden, enclosed ring, rear walls, plants or statue.
current_collection=D

def arc_shell(name,r0,r1,a0,a1,z0,z1,material,role):
 seg=max(2,math.ceil(abs(a1-a0)*20));verts=[]
 for z in [z0,z1]:
  for rr in [r0,r1]:
   for i in range(seg+1):
    a=a0+(a1-a0)*i/seg;verts.append((rr*math.cos(a),2.4+rr*math.sin(a),z))
 n=seg+1;faces=[]
 for i in range(seg):
  faces.extend([(i,i+1,n+i+1,n+i),(2*n+i,3*n+i,3*n+i+1,2*n+i+1),(i,2*n+i,2*n+i+1,i+1),(n+i,n+i+1,3*n+i+1,3*n+i)])
 faces += [(0,n,3*n,2*n),(seg,2*n+seg,3*n+seg,n+seg)]
 me=bpy.data.meshes.new(name);me.from_pydata(verts,[],faces);me.update();o=bpy.data.objects.new(name,me);D.objects.link(o);finish(o,name,material);mark(o,role);return o

def curved_tube(name,r,a0,a1,z):
 # Continuous capped polyline tube avoids duplicated segment caps and faceting at joins.
 steps=56;sides=20;verts=[];faces=[]
 for i in range(steps+1):
  a=a0+(a1-a0)*i/steps;center=Vector((r*math.cos(a),2.4+r*math.sin(a),z));radial=Vector((math.cos(a),math.sin(a),0))
  for j in range(sides):
   q=2*math.pi*j/sides;verts.append(tuple(center+.035*(math.cos(q)*radial+Vector((0,0,math.sin(q))))))
 for i in range(steps):
  for j in range(sides):faces.append((i*sides+j,i*sides+(j+1)%sides,(i+1)*sides+(j+1)%sides,(i+1)*sides+j))
 faces += [tuple(range(sides-1,-1,-1)),tuple(steps*sides+j for j in range(sides))]
 me=bpy.data.meshes.new(name);me.from_pydata(verts,[],faces);me.update();o=bpy.data.objects.new(name,me);D.objects.link(o);finish(o,name,'brushed_stainless')
 for p in o.data.polygons:p.use_smooth=len(p.vertices)==4
 mark(o,'rails');return o

for side,deg0,deg1 in [('left',200,258),('right',282,340)]:
 a0,a1=math.radians(deg0),math.radians(deg1);objects=[]
 # Dimensions and angular ends are design candidates, NOT measured coordinates.
 count=27
 for k in range(count):
  aa=a0+(a1-a0)*k/count+.0005;bb=a0+(a1-a0)*(k+1)/count-.0005
  objects.append(arc_shell(f'candidate_{side}_face_{k}',4.0,4.22,aa,bb,0,.52,'speckled_granite','stone'))
  objects.append(arc_shell(f'candidate_{side}_cap_{k}',3.975,4.245,aa,bb,.52,.59,'speckled_granite','stone'))
 objects.append(curved_tube(f'candidate_{side}_front_rail',3.88,a0+.012,a1-.012,.65));objects.append(curved_tube(f'candidate_{side}_rear_rail',4.10,a0+.012,a1-.012,.81))
 for i in range(6):
  a=a0+.02+(a1-a0-.04)*i/5
  def p(r,z):return(r*math.cos(a),2.4+r*math.sin(a),z)
  o=tube('candidate_slope_support',p(3.88,.65),p(4.1,.81),.014);mark(o,'rail_hardware');objects.append(o)
  o=tube('candidate_leg',p(3.98,.01),p(3.98,.65),.018,'support_dark_metal');mark(o,'rail_hardware');objects.append(o)
 objects=join_roles(objects,'candidate_'+side);root=bpy.data.objects.new('candidate_'+side+'_NOT_VERIFIED_CURRENT',None);D.objects.link(root);root['status']='UNVERIFIED PARTIAL CURVED LAYOUT CANDIDATE. Do not enable as current-world geometry.'
 for o in objects:o.parent=root
 assets['candidate_curve_'+side]=[root]+objects

# One flat material preview, explicitly not a replacement for clipped/sloped sidewalk triangles.
pm=mat('paving_ring_LAYOUT_CANDIDATE',(.28,.29,.30),.85);b=pm.node_tree.nodes.get('Principled BSDF')
for f,socket in [('paving_ring_candidate_basecolor.png','Base Color'),('paving_ring_candidate_roughness.png','Roughness')]:
 n=texnode(pm,f,socket=='Base Color');pm.node_tree.links.new(n.outputs['Color'],b.inputs[socket])
n=texnode(pm,'paving_ring_candidate_normal.png',False);nn=pm.node_tree.nodes.new('ShaderNodeNormalMap');nn.inputs['Strength'].default_value=.7;pm.node_tree.links.new(n.outputs['Color'],nn.inputs['Color']);pm.node_tree.links.new(nn.outputs['Normal'],b.inputs['Normal'])
verts=[(-5.2,-4,0),(5.2,-4,0),(5.2,3,0),(-5.2,3,0)];me=bpy.data.meshes.new('paving_flat_PREVIEW_only');me.from_pydata(verts,[],[(0,1,2,3)]);me.update();o=bpy.data.objects.new('paving_flat_PREVIEW_NOT_GROUND',me);D.objects.link(o);o.data.materials.append(pm);uv=o.data.uv_layers.new(name='UVMap')
for l,v in zip(uv.data,[(0,0),(1,0),(1,1),(0,1)]):l.uv=v
o['status']='Flat texture preview only. Preserve original ground triangles, z and collision; transplant atlas/UV only after layout acceptance.';assets['candidate_paving_PREVIEW_ONLY']=[o]

assets['current_pair'] = assets['current_left'] + assets['current_right']

# Export each component alone. Models retain statue-local frame; no cameras/lights/environment leak into GLB.
records={}
for name,objects in assets.items():
 bpy.ops.object.select_all(action='DESELECT')
 for o in objects:o.select_set(True)
 bpy.context.view_layer.objects.active=objects[-1]
 bpy.ops.export_scene.gltf(filepath=str(WEB/(name+'.glb')),export_format='GLB',use_selection=True,export_yup=True,export_materials='EXPORT',export_cameras=False,export_lights=False,export_extras=True)
 coords=[o.matrix_world@v.co for o in objects if o.type=='MESH' for v in o.data.vertices]
 records[name]={'triangles':sum(len(p.vertices)-2 for o in objects if o.type=='MESH' for p in o.data.polygons),'mesh_objects':sum(o.type=='MESH' for o in objects),'bounds_blender_zup':[[min(v[i] for v in coords) for i in range(3)],[max(v[i] for v in coords) for i in range(3)]],'file':str(Path('web')/(name+'.glb'))}
(QA/'build_stats.json').write_text(json.dumps({'blender':bpy.app.version_string,'assets':records,'protected_meshes_included':False,'photograph_pixels_included':False},indent=2))
# Default .blend opens only current seating visible, candidates hidden in viewport and render.
D.hide_render=True;D.hide_viewport=True
bpy.ops.wm.save_as_mainfile(filepath=str(ROOT/'hachiko_seating_paving_v002.blend'))

if '--render' in sys.argv:
 S=bpy.data.collections.new('PREVIEW_STUDIO_NOT_EXPORTED');bpy.context.scene.collection.children.link(S);current_collection=S
 scene=bpy.context.scene;scene.render.engine='CYCLES';scene.cycles.samples=48;scene.cycles.use_denoising=True;scene.render.resolution_x=1440;scene.render.resolution_y=900;scene.render.resolution_percentage=100;scene.world=bpy.data.worlds.new('Preview world');scene.world.use_nodes=True;scene.world.node_tree.nodes['Background'].inputs['Color'].default_value=(.32,.32,.32,1);scene.world.node_tree.nodes['Background'].inputs['Strength'].default_value=.45;scene.view_settings.view_transform='AgX'
 bpy.ops.object.camera_add(location=(5,7,3));cam=bpy.context.object;scene.camera=cam
 def aim(loc,target,lens=52,ortho=None):
  cam.location=loc;cam.rotation_euler=(Vector(target)-cam.location).to_track_quat('-Z','Y').to_euler();cam.data.type='ORTHO' if ortho else 'PERSP';cam.data.lens=lens
  if ortho:cam.data.ortho_scale=ortho
 for loc,power,size in [((1,2,7),1700,6),((-4,-3,5),1100,5),((5,-1,2),800,3)]:
  bpy.ops.object.light_add(type='AREA',location=loc);l=bpy.context.object;l.data.energy=power;l.data.shape='DISK';l.data.size=size;l.rotation_euler=(Vector((0,-1,.4))-l.location).to_track_quat('-Z','Y').to_euler()
 floor=box('preview_floor',(0,0,-.055),(24,24,.10),'preview_neutral_ground')
 def show(mode):
  C.hide_render=mode not in ['current','both'];D.hide_viewport=False;D.hide_render=mode not in ['candidate','paving']
  for key,oo in assets.items():
   visible=(mode=='current' and key.startswith('current')) or (mode=='candidate' and key.startswith('candidate_curve')) or (mode=='paving' and key.startswith('candidate_paving'))
   for ob in oo:ob.hide_render=not visible
 camera_records=[]
 def render(name):
  scene.render.filepath=str(PRE/name);bpy.ops.render.render(write_still=True)
  camera_records.append({'file':name,'location_blender_zup':list(cam.location),'rotation_euler':list(cam.rotation_euler),'type':cam.data.type,'lens_mm':cam.data.lens,'ortho_scale':cam.data.ortho_scale,'resolution':[scene.render.resolution_x,scene.render.resolution_y],'current_footprint_visible':not C.hide_render,'candidate_visible':not D.hide_render})
 show('current');aim((5.4,6.6,3.5),(0,-1.25,.38),52);render('01_current_components_oblique.png')
 show('current');D.hide_render=True;D.hide_viewport=True
 (QA/'preview_cameras.json').write_text(json.dumps(camera_records,indent=2))
print('Completed isolated seating and layout candidates.',records)
