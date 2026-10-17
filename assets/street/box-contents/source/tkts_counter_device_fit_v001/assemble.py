"""Translation-only TKTS counter/device local contact study. Blender 4.2.3.
blender -b -t 2 -P source/assemble.py -- [--out OUTPUT] [--render]
Uses only the unchanged, bundled authored BLEND inputs. No photograph required.
This script does not alter or regenerate either published source asset.
"""
import argparse, bpy, hashlib, json, math, sys, time
from pathlib import Path
from mathutils import Vector
from mathutils.bvhtree import BVHTree
START=time.perf_counter()
p=argparse.ArgumentParser();p.add_argument('--out');p.add_argument('--render',action='store_true');a=p.parse_args(sys.argv[sys.argv.index('--')+1:] if '--' in sys.argv else [])
ROOT=Path(__file__).resolve().parent.parent;O=Path(a.out).resolve() if a.out else ROOT
for d in ['models','evidence']: (O/d).mkdir(parents=True,exist_ok=True)
assert bpy.app.version[:3]==(4,2,3)
bpy.ops.wm.read_factory_settings(use_empty=True);s=bpy.context.scene;s.unit_settings.system='METRIC';s.unit_settings.scale_length=1
COUNTER_NAMES=['Front_counter_top_visible','Right_counter_return_top_visible','Front_red_fascia_evidence_cutoff','Right_red_fascia_evidence_cutoff','Left_return_top_visible_estimated_plan','Left_inner_red_fascia_evidence_cutoff']
LAPTOP_NAMES=['Reused_closed_laptop_tapered_chassis','Observed_closed_seam','Reused_lid_closed_variant']
DARK_NAME='Observed_dark_lead_visible_segment'
STAND_NAME='Observed_folio_lower_panel'
inputs={p.name:hashlib.sha256(p.read_bytes()).hexdigest() for p in sorted((ROOT/'inputs').iterdir()) if p.is_file()}

def append_objects(path,names=None):
 with bpy.data.libraries.load(str(path),link=False) as (src,dst):dst.objects=[n for n in src.objects if names is None or n in names]
 out=[]
 for ob in dst.objects:
  if ob is not None:s.collection.objects.link(ob);out.append(ob)
 return out
counter=append_objects(ROOT/'inputs/shibu_hachi_tkts_2024_kit_v003.blend',COUNTER_NAMES)
# All counter meshes have baked local coordinates; remove the illustrative kit root.
for ob in counter:
 mat=ob.matrix_local.copy();ob.parent=None;ob.matrix_world=mat
# An indirectly loaded root is not a delivered asset; clean unattached roots if present.
for ob in list(bpy.data.objects):
 if ob not in counter:bpy.data.objects.remove(ob,do_unlink=True)
devices=append_objects(ROOT/'inputs/tkts_tabletop_devices.blend')
assert len(counter)==6 and len(devices)==13
byname={o.name:o for o in counter+devices};laptop=[byname[n] for n in LAPTOP_NAMES];dark=byname[DARK_NAME]
tablet=[o for o in devices if o not in laptop and o!=dark]
allobs=counter+devices
bpy.context.view_layer.update()

def rounded(v):
 if isinstance(v,(int,float)):return round(float(v),10)
 return [rounded(x) for x in v]
def raw_signature(ob):
 return hashlib.sha256(json.dumps({'v':[rounded(v.co) for v in ob.data.vertices],'p':[list(p.vertices) for p in ob.data.polygons],'mi':[p.material_index for p in ob.data.polygons],'smooth':[p.use_smooth for p in ob.data.polygons]},sort_keys=True).encode()).hexdigest()
def evaluated_points(ob):
 ev=ob.evaluated_get(bpy.context.evaluated_depsgraph_get());me=ev.to_mesh();out=[ob.matrix_world@v.co for v in me.vertices];ev.to_mesh_clear();return out
def material_signature(mat):
 nodes=[]
 if mat.use_nodes:
  for n in mat.node_tree.nodes:
   vals=[]
   for i in n.inputs:
    if hasattr(i,'default_value'):
     v=i.default_value
     if isinstance(v,(int,float)):vals.append([i.name,round(float(v),9)])
     elif not isinstance(v,str) and hasattr(v,'__len__'):vals.append([i.name,[round(float(x),9) for x in v]])
   nodes.append([n.bl_idname,vals])
 return hashlib.sha256(json.dumps({'diffuse':rounded(mat.diffuse_color),'nodes':nodes},sort_keys=True).encode()).hexdigest()
source_signatures={o.name:{'mesh':raw_signature(o),'material':[material_signature(m) for m in o.data.materials],'modifier_types':[m.type for m in o.modifiers]} for o in allobs}
local_eval={o.name:[list(v) for v in evaluated_points(o)] for o in allobs}
# Solve support heights from existing flat mesh faces, not from the authoring datum.
TOP=max(v.z for o in counter if 'top_visible' in o.name or 'return_top' in o.name for v in evaluated_points(o))
stand_min=min(v.z for v in evaluated_points(byname[STAND_NAME]))
laptop_min=min(v.z for o in laptop for v in evaluated_points(o))
TABLET=Vector((-.530,-.325,TOP-stand_min))
# Laptop original centre (.365,.245); target estimated centre (-.560,.015).
LAPTOP=Vector((-.925,-.230,TOP-laptop_min))
# Preserve the dark segment but move its upper endpoint along the existing front
# chassis edge. It must pass the return's inner edge and still meet the laptop.
DARK=LAPTOP+Vector((.150,0,0))
transforms={o.name:list(TABLET if o in tablet else LAPTOP if o in laptop else DARK if o==dark else Vector((0,0,0))) for o in allobs}
for ob in allobs:ob.location=Vector(transforms[ob.name])
bpy.context.view_layer.update()

def area(poly):return abs(sum(poly[i][0]*poly[(i+1)%len(poly)][1]-poly[(i+1)%len(poly)][0]*poly[i][1] for i in range(len(poly)))/2) if len(poly)>2 else 0

def ccw(poly):
 return poly if sum(poly[i][0]*poly[(i+1)%len(poly)][1]-poly[(i+1)%len(poly)][0]*poly[i][1] for i in range(len(poly)))>=0 else list(reversed(poly))
def clip(subject,cutter):
 out=ccw(subject)
 for A,B in zip(ccw(cutter),ccw(cutter)[1:]+ccw(cutter)[:1]):
  inp=out;out=[]
  if not inp:break
  def signed(P):return (B[0]-A[0])*(P[1]-A[1])-(B[1]-A[1])*(P[0]-A[0])
  for P,Q in zip(inp,inp[1:]+inp[:1]):
   dP,dQ=signed(P),signed(Q);inP,inQ=dP>=-1e-10,dQ>=-1e-10
   if inP:out.append(P)
   if inP!=inQ:
    t=dP/(dP-dQ);out.append([P[0]+t*(Q[0]-P[0]),P[1]+t*(Q[1]-P[1])])
 return out

def horizontal_faces(ob,z):
 ev=ob.evaluated_get(bpy.context.evaluated_depsgraph_get());me=ev.to_mesh();pts=[ob.matrix_world@v.co for v in me.vertices];out=[]
 for face in me.polygons:
  vs=[pts[i] for i in face.vertices]
  if all(abs(v.z-z)<2e-7 for v in vs):
   poly=ccw([[v.x,v.y] for v in vs])
   if area(poly)>1e-10:out.append(poly)
 ev.to_mesh_clear();return out
supports=[]
for ob in counter:
 for poly in horizontal_faces(ob,TOP):supports.append({'object':ob.name,'polygon_xy_m':poly,'area_m2':area(poly)})
contact_reports=[]
for label,obs in [('tablet_stand',[byname[STAND_NAME]]),('closed_laptop',laptop)]:
 bottom=[]
 for ob in obs:
  for poly in horizontal_faces(ob,TOP):bottom.append({'object':ob.name,'polygon_xy_m':poly})
 patches=[];total=sum(area(p['polygon_xy_m']) for p in bottom)
 for b in bottom:
  for sup in supports:
   pp=clip(b['polygon_xy_m'],sup['polygon_xy_m'])
   if area(pp)>1e-10:patches.append({'device_part':b['object'],'counter_part':sup['object'],'polygon_xy_m':pp,'area_m2':area(pp)})
 supported=sum(x['area_m2'] for x in patches)
 points=[v for ob in obs for v in evaluated_points(ob)]
 report={'device':label,'lowest_surface_z_m':min(v.z for v in points),'counter_top_z_m':TOP,'minimum_vertical_gap_m':min(v.z for v in points)-TOP,'bottom_flat_area_m2':total,'supported_contact_area_m2':supported,'supported_flat_area_fraction':supported/total if total else 0,'bottom_faces':bottom,'contact_patches':patches}
 assert supported>0 and report['supported_flat_area_fraction']>(.95 if label=='tablet_stand' else .90),report
 contact_reports.append(report)
# Detect device/cable vertices penetrating the six actual evaluated part envelopes.
# Nominal envelope is conservative around bevels: it can flag a false positive,
# but cannot hide a vertex well inside a slab. Contact is not penetration.
boxes=[]
for ob in counter:
 ps=evaluated_points(ob);boxes.append({'object':ob.name,'min':[min(v[k] for v in ps) for k in range(3)],'max':[max(v[k] for v in ps) for k in range(3)]})
penetrations=[]
for ob in devices:
 for i,pt in enumerate(evaluated_points(ob)):
  for box in boxes:
   if all(box['min'][k]+1e-5<pt[k]<box['max'][k]-1e-5 for k in range(3)):penetrations.append({'device':ob.name,'counter':box['object'],'vertex':i,'point':list(pt)})
# Exact source endpoint centre vs preserved laptop surface, radius 1.5 mm.
verts=[];faces=[]
for ob in laptop:
 ev=ob.evaluated_get(bpy.context.evaluated_depsgraph_get());me=ev.to_mesh();off=len(verts);verts.extend([ob.matrix_world@v.co for v in me.vertices]);faces.extend([tuple(off+i for i in p.vertices) for p in me.polygons]);ev.to_mesh_clear()
bvh=BVHTree.FromPolygons(verts,faces,all_triangles=False)
endpoint=Vector((.360,.138,.073))+DARK;nearest=bvh.find_nearest(endpoint)
endpoint_distance=float(nearest[3]);dark_touches=endpoint_distance<=.0015+1e-5
cable_report={'dark_upper_endpoint_centre_m':list(endpoint),'nearest_laptop_surface_m':list(nearest[0]),'centre_to_surface_distance_m':endpoint_distance,'authored_cable_radius_m':.0015,'silhouette_contact':dark_touches,'additional_lateral_translation_vs_laptop_m':.150,'interpretation':'Estimated contact along existing front chassis edge, not a verified electrical connection or port. No connector, hidden continuation, or new cable geometry.'}
# An unresolved cable is preserved but excluded, never concealed by a full-pass label.
held=[]
if not dark_touches or any(x['device']==dark.name for x in penetrations):
 held.append(dark.name);dark.hide_render=True;dark.hide_set(True);dark['assembly_status']='HOLD: original segment preserved; attachment/contact not reconciled'
active=[o for o in allobs if o.name not in held]
active_penetrations=[p for p in penetrations if p['device'] not in held]
assert not active_penetrations,active_penetrations[:10]
# Verify original local meshes, material parameters, modifiers and evaluated shape
# are identical after subtracting the explicitly recorded rigid translation.
max_error=0
for ob in allobs:
 assert raw_signature(ob)==source_signatures[ob.name]['mesh']
 assert [material_signature(m) for m in ob.data.materials]==source_signatures[ob.name]['material']
 cur=evaluated_points(ob);src=local_eval[ob.name];assert len(cur)==len(src)
 for p0,q in zip(src,cur):max_error=max(max_error,(q-Vector(transforms[ob.name])-Vector(p0)).length)
assert max_error<1e-6
for ob in allobs:
 ob['local_fit_translation_m']=transforms[ob.name];ob['world_placement']='null; not a site/runtime transform';ob['source_mesh_preserved']=True
s['asset']='tkts_counter_device_fit_v001';s['scope']='Estimated local contact candidate. Existing geometry and materials preserved. Counter upper-shell bottom is not floor contact.';s['world_transform']='null';s['source_period']='2024-09-19 article; photograph date unknown; 2026 continuity not verified';s['new_geometry']=False
s['laptop_overhang']='304 mm authored envelope on 280 mm estimated return. 12 mm each side nominal; actual bottom-face support is measured in contact_report.json.'
# A clean editable BLEND, no staging or hidden photographic image data.
bpy.context.preferences.filepaths.save_version=0;bpy.ops.object.select_all(action='DESELECT')
for ob in active:ob.select_set(True)
bpy.context.view_layer.objects.active=active[0];bpy.ops.file.pack_all();bpy.ops.wm.save_as_mainfile(filepath=str(O/'tkts_counter_device_fit_v001.blend'))
# Export only existing evaluated geometry, bake this local assembly translation.
# Parts remain separated to preserve selection and provenance in the combined GLB.
copies=[]
for ob in active:
 me=bpy.data.meshes.new_from_object(ob.evaluated_get(bpy.context.evaluated_depsgraph_get()),depsgraph=bpy.context.evaluated_depsgraph_get());cp=bpy.data.objects.new(ob.name+'_local_fit',me);s.collection.objects.link(cp);cp.matrix_world=ob.matrix_world.copy();copies.append(cp)
bpy.ops.object.select_all(action='DESELECT')
for ob in copies:ob.select_set(True)
bpy.context.view_layer.objects.active=copies[0];bpy.ops.object.transform_apply(location=True,rotation=True,scale=True)
bpy.ops.export_scene.gltf(filepath=str(O/'models/tkts_counter_device_fit_v001.glb'),export_format='GLB',use_selection=True,export_yup=True,export_extras=False,export_cameras=False,export_lights=False)
export_bounds=[[min(v[k] for ob in copies for v in evaluated_points(ob)) for k in range(3)],[max(v[k] for ob in copies for v in evaluated_points(ob)) for k in range(3)]]
export_triangle_count=sum(len(p.vertices)-2 for o in copies for p in o.data.polygons)
for ob in copies:bpy.data.objects.remove(ob,do_unlink=True)
# Bounded verification of this new combined export only. Published source modules
# are not revalidated. No repeated full topology/asset audit is performed.
before_ids=set(bpy.data.objects)
bpy.ops.import_scene.gltf(filepath=str(O/'models/tkts_counter_device_fit_v001.glb'))
imported=[o for o in bpy.data.objects if o not in before_ids]
im=[o for o in imported if o.type=='MESH'];bpy.context.view_layer.update()
ib=[[min(v[k] for ob in im for v in evaluated_points(ob)) for k in range(3)],[max(v[k] for ob in im for v in evaluated_points(ob)) for k in range(3)]]
it=sum(len(p.vertices)-2 for o in im for p in o.data.polygons)
err=max(abs(export_bounds[i][k]-ib[i][k]) for i in range(2) for k in range(3))
assert len(im)==len(active) and it==export_triangle_count and err<1e-6
combined_import={'mesh_parts':len(im),'triangles':it,'bounds_max_error_m':err,'finite_bounds':all(math.isfinite(x) for b in ib for x in b),'scope':'Bounded combined-export check only; no published-source topology rerun.'}
for ob in imported:bpy.data.objects.remove(ob,do_unlink=True)
report={'status':'LOCAL_CONTACT_SUPPORTED_WITH_DISCLOSED_INFERENCES' if not held else 'LOCAL_DEVICE_CONTACT_SUPPORTED_CABLE_HOLD','units':'metres','world_transform':None,'runtime_integration':False,'device_rotation_changes':False,'device_scaling_changes':False,'new_geometry':False,'counter_top_z_m':TOP,'tablet_source_stand_bottom_m':stand_min,'laptop_source_bottom_m':laptop_min,'old_laptop_bottom_is_authoring_datum_not_measurement':True,'transforms_blender_z_up':transforms,'source_preservation':{'mesh_material_signature_count':len(source_signatures),'maximum_evaluated_translation_residual_m':max_error,'bundled_input_sha256':inputs},'supports':supports,'devices':contact_reports,'cable':cable_report,'held_optional_objects':held,'conservative_vertex_penetrations':active_penetrations,'combined_export':{'mesh_parts':len(active),'triangles':export_triangle_count,'bounds_blender_m':export_bounds},'combined_export_reimport':combined_import,'limits':['Local supported candidate, not solved world placement or calibrated photo registration.','Counter plan, coplanarity, dimensions and device positions remain estimated.','Laptop side overhang is an explicitly retained inference, not a defect or new support.','The source cable association is uncertain even when silhouette contact passes.','Counter bottom is an evidence cutoff, not the floor; no cabinet/support geometry added.']}
(O/'evidence/contact_report.json').write_text(json.dumps(report,indent=2)+'\n')
(O/'evidence/preservation_signatures.json').write_text(json.dumps(source_signatures,indent=2)+'\n')
# Matched views of the assembly only; no photograph or staging desk is used.
if a.render:
 s.render.engine='CYCLES';s.cycles.samples=32;s.cycles.use_denoising=True;s.render.resolution_x=1200;s.render.resolution_y=950;s.render.resolution_percentage=100;s.render.image_settings.file_format='PNG';s.view_settings.view_transform='AgX'
 s.world=bpy.data.worlds.new('Neutral_inspection_world');s.world.use_nodes=True;s.world.node_tree.nodes['Background'].inputs[0].default_value=(.12,.145,.17,1);s.world.node_tree.nodes['Background'].inputs[1].default_value=.6
 target=Vector((-.015,.0,.29));direction=Vector((3,-6,3.6)).normalized()
 for loc,power,size in [((-3,-4,5),500,4),((4,-1,3),350,3),((0,3,4),400,3)]:
  bpy.ops.object.light_add(type='AREA',location=loc);li=bpy.context.object;li.data.energy=power;li.data.size=size;li.rotation_euler=(target-li.location).to_track_quat('-Z','Y').to_euler()
 bpy.ops.object.camera_add(location=target+direction*5);cam=bpy.context.object;cam.rotation_euler=(-direction).to_track_quat('-Z','Y').to_euler();cam.data.type='ORTHO';cam.data.ortho_scale=1.74;s.camera=cam
 frames=[]
 for name,is_after in [('before_authoring_offsets',False),('after_supported_local_fit',True)]:
  for ob in devices:ob.location=Vector(transforms[ob.name]) if is_after else TABLET
  bpy.context.view_layer.update();s.render.filepath=str(O/'evidence'/(name+'.png'));bpy.ops.render.render(write_still=True)
  frames.append({'file':name+'.png','camera_location':list(cam.location),'camera_rotation':list(cam.rotation_euler),'orthographic_scale_m':cam.data.ortho_scale,'identical_lighting':True,'photo_registration':False,'before_definition':'Unchanged device-kit offsets, translated only to place tablet stand on current counter. Not an earlier installed assembly.'})
 (O/'evidence/comparison_framing.json').write_text(json.dumps(frames,indent=2)+'\n')
(O/'evidence/timing.json').write_text(json.dumps({'seconds':time.perf_counter()-START,'rendered':a.render},indent=2)+'\n')
print('ASSEMBLY_COMPLETE',report['status'],json.dumps({'contacts':[{k:v for k,v in r.items() if k not in ['bottom_faces','contact_patches']} for r in contact_reports],'cable':cable_report,'held':held,'max_shape_residual':max_error}))
