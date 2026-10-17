"""Translation-only bounded souvenir-wall review. Blender 4.2.3 LTS.
Reuses input blends without running their generators. No source photos required.
Usage: blender -b -t 2 --python source/assemble_review.py -- PACKAGE_DIR
"""
import bpy, sys, json, hashlib, struct, math, time
from pathlib import Path
from mathutils import Vector
from mathutils.bvhtree import BVHTree
assert bpy.app.version[:3] == (4,2,3)
T=time.perf_counter(); P=Path(sys.argv[sys.argv.index('--')+1]).resolve()
bpy.ops.wm.read_factory_settings(use_empty=True)
s=bpy.context.scene;s.name='EDITABLE_PARTIAL_SECTION';s.unit_settings.system='METRIC';s.unit_settings.scale_length=1
G={}; roots={}; signatures={}; original_world={}; original_root={}

def mdump(v):return [[float(x) for x in row] for row in v]
def vec(v):return [float(x) for x in v]
def mesh_signature(o):
 h=hashlib.sha256();h.update(o.type.encode())
 for v in o.data.vertices:h.update(struct.pack('<3f',*v.co))
 for p in o.data.polygons:h.update(struct.pack('<i?',p.material_index,p.use_smooth));h.update(struct.pack('<'+'I'*len(p.vertices),*p.vertices))
 for layer in o.data.uv_layers:
  h.update(layer.name.encode())
  for q in layer.data:h.update(struct.pack('<2f',*q.uv))
 for m in o.modifiers:
  h.update(m.type.encode())
  for prop in m.bl_rna.properties:
   if prop.identifier in ['rna_type','name','type']:continue
   try:
    val=getattr(m,prop.identifier)
    if isinstance(val,(int,float,str,bool)):h.update(f'{prop.identifier}:{val}'.encode())
   except:pass
 for mat in o.data.materials:h.update(mat.name.encode())
 return h.hexdigest()
def mat_signature(m):
 d={'name':m.name,'use_nodes':m.use_nodes,'diffuse_color':vec(m.diffuse_color),'nodes':[],'links':[]}
 if m.use_nodes:
  for n in m.node_tree.nodes:
   x={'name':n.name,'type':n.type,'inputs':{}}
   for i in n.inputs:
    if hasattr(i,'default_value'):
     v=i.default_value
     if isinstance(v,(int,float,str,bool)):x['inputs'][i.name]=v
     else:
      try:x['inputs'][i.name]=list(v)
      except:pass
   if hasattr(n,'image') and n.image:x['image']=n.image.name
   d['nodes'].append(x)
  d['links']=[(l.from_node.name,l.from_socket.name,l.to_node.name,l.to_socket.name) for l in m.node_tree.links]
 return hashlib.sha256(json.dumps(d,sort_keys=True).encode()).hexdigest()
def bounds(obs):
 pts=[];deps=bpy.context.evaluated_depsgraph_get()
 for o in obs:
  ev=o.evaluated_get(deps);me=ev.to_mesh();pts.extend(o.matrix_world@v.co for v in me.vertices);ev.to_mesh_clear()
 return [Vector([min(v[k] for v in pts) for k in range(3)]),Vector([max(v[k] for v in pts) for k in range(3)])]
def serial_bounds(obs):return [vec(v) for v in bounds(obs)]
def append_objects(path):
 with bpy.data.libraries.load(str(path),link=False) as (src,dst):dst.objects=list(src.objects)
 return [o for o in dst.objects if o]
def collection(name):
 c=bpy.data.collections.new(name);s.collection.children.link(c);return c
wallobs=append_objects(P/'inputs/wall_louver_source.blend')
wc=collection('ASSET_wall_louver_sample')
wr=bpy.data.objects.new('Wall_sample_CUT_EDGE_NOT_FLOOR',None);wc.objects.link(wr)
for o in wallobs:
 if o.type!='MESH':continue
 wc.objects.link(o);o.parent=wr
G['wall_louver_sample']=[o for o in wallobs if o.type=='MESH'];roots['wall_louver_sample']=wr
kitobs=append_objects(P/'inputs/souvenir_kit_source.blend')
for key in ['wire_display','box_shelves']:
 c=collection('ASSET_'+key);rt=next(o for o in kitobs if o.name.startswith(key+'_bottom_centre'));roots[key]=rt;c.objects.link(rt)
 obs=[o for o in kitobs if o.type=='MESH' and o.parent==rt]
 for o in obs:c.objects.link(o)
 G[key]=obs
# One unchanged linked panel instance extends only the PHOTO-SUPPORTED upper wood patch.
# Its lower edge remains the SAME cut at 1.10 m. No full-height wall is inferred.
pc=collection('ASSET_souvenir_wall_panel_instance')
pr=bpy.data.objects.new('Panel_instance_CUT_EDGE_NOT_FLOOR',None);pc.objects.link(pr)
panel_source=next(o for o in G['wall_louver_sample'] if o.name=='Wall_patch_vertical_grain_2')
pi=panel_source.copy();pi.name='Linked_existing_broad_wood_panel';pi.data=panel_source.data;pi.parent=pr;pc.objects.link(pi)
pi['source_object']='Wall_patch_vertical_grain_2';pi['linked_instance_only']=True
G['souvenir_wall_panel_instance']=[pi];roots['souvenir_wall_panel_instance']=pr
bpy.context.view_layer.update()
for key,obs in G.items():
 original_root[key]=mdump(roots[key].matrix_world)
 for o in obs:signatures[o.name]=mesh_signature(o);original_world[o.name]=mdump(o.matrix_world)
all_mats={m for obs in G.values() for o in obs for m in o.data.materials}
material_before={m.name:mat_signature(m) for m in all_mats}
image_before={im.name:hashlib.sha256(bytes(im.packed_file.data)).hexdigest() for im in bpy.data.images if im.packed_file}
# ONLY these root translations are authored. No rotation/scaling or geometry edits.
placements={'wall_louver_sample':(2.10,.245,1.10),'wire_display':(-.54,0,0),'box_shelves':(.64,0,0),'souvenir_wall_panel_instance':(-.752,.245,1.10)}
for key,rt in roots.items():
 rt.location=placements[key];rt.rotation_euler=(0,0,0);rt.scale=(1,1,1)
 rt['review_only']=True;rt['measured_placement']=False;rt['source_period']='Published 2024-09-19; capture date unknown; 2026 persistence unverified'
 rt['world_transform']='UNRESOLVED'
 rt['placement_basis']=('One unchanged linked wood panel extends the supported upper wall only; lower cut remains 1.10 m.' if key=='souvenir_wall_panel_instance' else 'Counter-derived patch is adjacent RIGHT of souvenir zone; lower and left continuation omitted. Louver is not centred above souvenirs.' if key=='wall_louver_sample' else 'Wire left / six boxes right is photo-supported. Numeric spacing/depth/common base datum estimated.')
wr['lower_edge']='SAMPLE CUT at review Z=1.10; not floor, countertop, or real wall termination'
s['scope']='PARTIAL WALL SECTION: floor, window, wall continuation, physical support and real installation transform unresolved'
s['no_extra_products']=True;s['no_floor']=True;s['no_window']=True;s['not_current_survey']=True
bpy.context.view_layer.update()
transforms={}; part_transforms=[]
for key,obs in G.items():
 rt=roots[key]
 transforms[key]={'source_root_matrix_world':original_root[key],'review_matrix_world':mdump(rt.matrix_world),'bounds_m':serial_bounds(obs),'mesh_objects':len(obs),'world_transform':None,'units':'metres','blender_front':'-Y','status':'estimated relative section, not installation'}
 for o in obs:part_transforms.append({'group':key,'name':o.name,'source_world_matrix':original_world[o.name],'review_world_matrix':mdump(o.matrix_world),'parent_local_matrix':mdump(o.matrix_local),'geometry_sha256_unchanged':mesh_signature(o)==signatures[o.name]})
box_parts=[]
for row in range(1,4):
 for col in range(1,3):
  pre=f'Cube_R{row}_C{col}';obs=[o for o in G['box_shelves'] if o.name.startswith(pre)]
  box_parts.append({'id':pre,'boards_and_edge_objects':len(obs),'bounds_m':serial_bounds(obs),'root_matrix':mdump(roots['box_shelves'].matrix_world)})
# Inter-group AABBs, BVH surface intersections and deliberate inherited joints.
def bvh(obs):
 vs=[];polys=[];deps=bpy.context.evaluated_depsgraph_get()
 for o in obs:
  ev=o.evaluated_get(deps);me=ev.to_mesh();me.calc_loop_triangles();off=len(vs)
  vs.extend(o.matrix_world@v.co for v in me.vertices);polys.extend(tuple(off+i for i in tr.vertices) for tr in me.loop_triangles);ev.to_mesh_clear()
 return BVHTree.FromPolygons(vs,polys,all_triangles=True),len(polys)
bvhs={};triangles={}
for k,obs in G.items():bvhs[k],triangles[k]=bvh(obs)
checks=[]
keys=list(G)
for i,k in enumerate(keys):
 for j in range(i+1,len(keys)):
  l=keys[j];ba=bounds(G[k]);bb=bounds(G[l]);sep=[max(float(ba[0][a]-bb[1][a]),float(bb[0][a]-ba[1][a]),0.) for a in range(3)]
  overlaps=bvhs[k].overlap(bvhs[l]);checks.append({'a':k,'b':l,'aabb_separation_axes_m':sep,'triangle_surface_overlap_pairs':len(overlaps),'pass_no_inter_group_collision':not overlaps and max(sep)>0})
wall_b=bounds(G['wall_louver_sample']);wire_b=bounds(G['wire_display']);box_b=bounds(G['box_shelves'])
louver=[o for o in G['wall_louver_sample'] if o.name.startswith('Horizontal_louver')]
lb=bounds(louver)
report={'blender':bpy.app.version_string,'build_hash':bpy.app.build_hash.decode(),'geometry_unchanged':all(mesh_signature(o)==signatures[o.name] for obs in G.values() for o in obs),'material_nodes_unchanged':all(mat_signature(m)==material_before[m.name] for m in all_mats),'packed_image_payloads_unchanged':all(hashlib.sha256(bytes(im.packed_file.data)).hexdigest()==image_before[im.name] for im in bpy.data.images if im.packed_file),'group_triangles':triangles,'source_modifiers_preserved':True,'additional_panel_is_linked_source_mesh':pi.data==panel_source.data,'new_unique_panel_geometry':False,'source_wall_meshes':10,'additional_panel_instances':1,'inter_group_checks':checks,'six_box_bounds':box_parts,'wire_to_boxes_x_gap_m':float(box_b[0].x-wire_b[1].x),'louver_left_to_boxes_right_x_gap_m':float(lb[0].x-box_b[1].x),'minimum_back_clearance_to_wall_envelope_m':{'wire_display':float(wall_b[0].y-wire_b[1].y),'box_shelves':float(wall_b[0].y-box_b[1].y)},'floor_contact_verified':False,'floor_not_modelled':True,'window_relation_verified':False,'window_not_modelled':True,'wall_cut_edge_review_z_m':float(wall_b[0].z),'model_base_datum_not_floor':True,'scope':'Only inter-asset arrangement. Existing board contacts, wire intersections and source closure/UV validations are not repeated or changed. No runtime collision/visibility/FPS tests.'}
(P/'validation/assembly_checks.json').write_text(json.dumps(report,indent=2)+'\n')
(P/'transforms.json').write_text(json.dumps({'coordinate_system':'Blender metres Z-up, front -Y. glTF export Y-up/front +Z. z=0 fixture model-base datum; NOT surveyed floor.','groups':transforms,'six_box_carcasses':box_parts,'parts':part_transforms},indent=2)+'\n')
# Editable model saves preserved original geometry/materials and reversible parent translations.
bpy.ops.object.select_all(action='DESELECT')
for obs in G.values():
 for o in obs:o.select_set(True)
bpy.context.view_layer.objects.active=G['box_shelves'][0]
bpy.ops.wm.save_as_mainfile(filepath=str(P/'pavilion_souvenir_wall_fit_v001.blend'))
# Export copies batched by original material, retaining per-group root translations.
export_roots=[];temp=[];deps=bpy.context.evaluated_depsgraph_get()
for key,obs in G.items():
 er=bpy.data.objects.new(key+'_REVIEW_ONLY',None);s.collection.objects.link(er);er.matrix_world=roots[key].matrix_world.copy();er['scope']='Partial section only, unresolved floor/window/installation';export_roots.append(er)
 for mat in sorted({o.data.materials[0] for o in obs},key=lambda x:x.name):
  copies=[];bpy.ops.object.select_all(action='DESELECT')
  for o in obs:
   if o.data.materials[0]!=mat:continue
   me=bpy.data.meshes.new_from_object(o.evaluated_get(deps),depsgraph=deps);cp=bpy.data.objects.new('export_'+o.name,me);s.collection.objects.link(cp);cp.matrix_world=roots[key].matrix_world.inverted()@o.matrix_world;cp.select_set(True);copies.append(cp)
  bpy.context.view_layer.objects.active=copies[0];bpy.ops.object.join();cp=bpy.context.object;bpy.ops.object.transform_apply(location=True,rotation=True,scale=True);cp.name=key+'__'+mat.name;cp.parent=er;temp.append(cp)
bpy.ops.object.select_all(action='DESELECT')
for o in export_roots+temp:o.select_set(True)
bpy.context.view_layer.objects.active=temp[0]
glb=P/'models/pavilion_souvenir_wall_PARTIAL_REVIEW.glb'
bpy.ops.export_scene.gltf(filepath=str(glb),export_format='GLB',use_selection=True,export_yup=True,export_extras=True,export_cameras=False,export_lights=False)
for o in temp+export_roots:bpy.data.objects.remove(o,do_unlink=True)
# Inspect/render the combined file once, not source generators or original-asset validation.
bpy.ops.wm.read_factory_settings(use_empty=True);bpy.ops.import_scene.gltf(filepath=str(glb));s=bpy.context.scene
rmeshes=[o for o in s.objects if o.type=='MESH'];rtri=0
for o in rmeshes:o.data.calc_loop_triangles();rtri+=len(o.data.loop_triangles)
reimport={'mesh_objects':len(rmeshes),'triangles':rtri,'expected_triangles':sum(triangles.values()),'triangle_count_preserved':rtri==sum(triangles.values()),'bounds_m':serial_bounds(rmeshes),'source_scene_contains_floor':False,'cameras_or_lights_in_glb':any(o.type in ['CAMERA','LIGHT'] for o in s.objects)}
assert reimport['triangle_count_preserved'];assert not reimport['cameras_or_lights_in_glb']
# Reimport group bounds verify root transforms survived export.
for key in keys:
 obs=[o for o in rmeshes if o.name.startswith(key+'__')];rb=serial_bounds(obs);expected=transforms[key]['bounds_m'];err=max(abs(rb[i][a]-expected[i][a]) for i in range(2) for a in range(3));reimport[key]={'bounds_m':rb,'max_bound_error_m':err,'pass':err<1e-5};assert err<1e-5
(P/'validation/combined_glb_check.json').write_text(json.dumps(reimport,indent=2)+'\n')
s.render.engine='CYCLES';s.cycles.samples=48;s.cycles.use_denoising=True;s.render.resolution_x=1800;s.render.resolution_y=1100;s.render.resolution_percentage=100;s.render.image_settings.file_format='PNG';s.view_settings.view_transform='AgX';s.render.film_transparent=False
s.world=bpy.data.worlds.new('RENDER_ONLY_world');s.world.use_nodes=True;s.world.node_tree.nodes['Background'].inputs[0].default_value=(.036,.046,.063,1);s.world.node_tree.nodes['Background'].inputs[1].default_value=.55
for loc,power,size in [((-3,-5,5),850,5),((5,-3,4),600,4),((1,2,5),450,3)]:
 bpy.ops.object.light_add(type='AREA',location=loc);l=bpy.context.object;l.name='RENDER_ONLY_light';l.data.energy=power;l.data.size=size;l.rotation_euler=(Vector((1,.1,1.2))-l.location).to_track_quat('-Z','Y').to_euler()
# No floor/backdrop mesh: the incompleteness stays visible. Text is render-only.
labelmat=bpy.data.materials.new('RENDER_ONLY_annotation');labelmat.use_nodes=True;nodes=labelmat.node_tree.nodes;nodes.clear();em=nodes.new('ShaderNodeEmission');em.inputs[0].default_value=(.77,.85,.96,1);em.inputs[1].default_value=.85;out=nodes.new('ShaderNodeOutputMaterial');labelmat.node_tree.links.new(em.outputs[0],out.inputs[0])
views=[('01_front_partial_section',(1.05,-8,1.25),(1.05,0,1.25),6.10),('02_oblique_depth_and_cut',(-3.5,-8,4.0),(1.05,.1,1.23),6.10)]
visibility=[]
for label,loc,target,scale in views:
 bpy.ops.object.camera_add(location=loc);cam=bpy.context.object;cam.name='RENDER_ONLY_'+label;cam.rotation_euler=(Vector(target)-cam.location).to_track_quat('-Z','Y').to_euler();cam.data.type='ORTHO';cam.data.ortho_scale=scale;s.camera=cam
 anns=[]
 def text_overlay(body,x,y,size):
  cu=bpy.data.curves.new('RENDER_ONLY_label','FONT');cu.body=body;cu.size=size;cu.align_x='LEFT';cu.materials.append(labelmat);ob=bpy.data.objects.new('RENDER_ONLY_label',cu);s.collection.objects.link(ob);ob.rotation_euler=cam.rotation_euler;ob.location=cam.matrix_world@Vector((x,y,-2.5));anns.append(ob)
 bpy.context.view_layer.update()
 text_overlay('SHIBU HACHI BOX  |  PARTIAL SOUVENIR WALL REVIEW',-2.70,1.56,.095)
 text_overlay('Preserved assets. Relative translations estimated. Not a full room or current survey.',-2.70,1.40,.065)
 text_overlay('NO FLOOR / NO WINDOW   |   Z=0 is only the fixture model-base datum',-2.70,-1.55,.066)
 text_overlay('Wall lower edge = SAMPLE CUT at Z=1.10 m. Lower continuation intentionally omitted; upper wood uses one linked panel instance.',-2.70,-1.67,.060)
 from bpy_extras.object_utils import world_to_camera_view
 coords=[world_to_camera_view(s,cam,o.matrix_world@v.co) for o in rmeshes for v in o.data.vertices]
 visibility.append({'view':label,'camera_location':vec(cam.location),'camera_target':target,'orthographic_scale':scale,'projection_min':[min(v[i] for v in coords) for i in range(2)],'projection_max':[max(v[i] for v in coords) for i in range(2)],'all_asset_vertices_inside_frame':all(0<=v.x<=1 and 0<=v.y<=1 and v.z>0 for v in coords),'floor_render_helper_used':False})
 s.render.filepath=str(P/'images'/(label+'.png'));bpy.ops.render.render(write_still=True)
 for ob in anns:bpy.data.objects.remove(ob,do_unlink=True)
(P/'validation/view_checks.json').write_text(json.dumps(visibility,indent=2)+'\n')
(P/'validation/build_timing.json').write_text(json.dumps({'seconds':time.perf_counter()-T,'original_asset_regeneration':False,'combined_export_reimport_checks':1,'renders':2},indent=2)+'\n')
print(json.dumps({'assembly_checks':report,'reimport':reimport,'views':visibility},indent=2))
