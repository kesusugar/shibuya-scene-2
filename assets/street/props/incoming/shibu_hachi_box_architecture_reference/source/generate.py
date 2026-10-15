"""SHIBU HACHI BOX architectural reference. Blender 4.2.3; no external assets.
Usage: blender -b --python source/generate.py -- --output output [--render]
All coordinates are metres. Z up; facade toward -Y. Bottom footprint centre origin.
"""
import bpy, math, json, argparse, sys
from pathlib import Path
from mathutils import Vector
p=argparse.ArgumentParser();p.add_argument('--output',default='output');p.add_argument('--render',action='store_true');args=p.parse_args(sys.argv[sys.argv.index('--')+1:] if '--' in sys.argv else [])
out=Path(args.output).resolve();out.mkdir(parents=True,exist_ok=True)
bpy.ops.object.select_all(action='SELECT');bpy.ops.object.delete(use_global=False)
for d in list(bpy.data.materials):bpy.data.materials.remove(d)
s=bpy.context.scene;s.unit_settings.system='METRIC';s.unit_settings.scale_length=1
mats={}
def mat(n,c,rough=.5,metal=0,alpha=1):
 m=bpy.data.materials.new(n);m.diffuse_color=(*c,alpha);m.use_nodes=True;b=m.node_tree.nodes.get('Principled BSDF');b.inputs['Base Color'].default_value=(*c,alpha);b.inputs['Roughness'].default_value=rough;b.inputs['Metallic'].default_value=metal;b.inputs['Alpha'].default_value=alpha
 if alpha<1:m.surface_render_method='DITHERED';b.inputs['IOR'].default_value=1.45
 mats[n]=m;return m
white=mat('01_Pale_anodized_frames',(.69,.73,.72),.32,.38)
dark=mat('02_Dark_brown_fascia_and_gaskets',(.065,.049,.039),.43,.25)
stone=mat('03_Pale_mineral_platform',(.61,.62,.57),.82)
warm=mat('04_Warm_pale_soffit_finish',(.55,.43,.29),.68)
glass=mat('05_Clear_glass_portable_alpha',(.48,.62,.62),.14,.06,.16)
objs=[]
def box(n,loc,dim,m,bevel=0):
 bpy.ops.mesh.primitive_cube_add(size=1,location=loc);o=bpy.context.object;o.name=n;o.dimensions=dim;bpy.ops.object.transform_apply(location=False,rotation=False,scale=True);o.data.materials.append(m)
 if bevel:
  mod=o.modifiers.new('Small manufactured edge','BEVEL');mod.width=bevel;mod.segments=2;bpy.context.view_layer.objects.active=o;bpy.ops.object.modifier_apply(modifier=mod.name)
 objs.append(o);return o
# Actual outside footprint 12.559 x 3.572, front -Y. Enclosed width walls at +/-6.103.
# Column centre depth 2.222 and wall centre depth 2.244. Unmeasured top height is 2.80.
front=-.536;rear=1.708;floor=.23;ceil=floor+2.354
box('Platform_main_inferred_slab', (0,.553,.115),(12.559,2.466,.23),stone,.012)
# Narrow side approach areas with broad central raised platform. Outline follows dimensioned offsets.
box('Front_platform_central', (0,-1.223,.115),(10.259,1.126,.23),stone,.01)
for sg in [-1,1]:
 box('End_approach_low_step_'+str(sg),(sg*5.7045,-1.223,.0575),(1.15,1.126,.115),stone,.008)
 box('End_threshold_step_'+str(sg),(sg*5.7045,-.79,.1725),(1.15,.26,.115),stone,.006)
box('Interior_floor',(0,.586,.239),(12.176,2.15,.018),warm)
# Structural piers centres span 12.259. 0.350 divider piers, slim outer corner frames.
centres=[-6.1295,-2.1015,2.1015,6.1295]
for i,x in enumerate(centres):
 w=.35 if i in [1,2] else .15
 for side,y in [('front',front),('rear',rear)]:
  box(f'{side}_pier_{i}',(x,y,(floor+ceil)/2),(w,.15,ceil-floor),white,.005)
# Rear is a plain inferred closure; no invented unseen opening/service details.
box('Rear_closure_INFERRED',(0,rear+.028,(floor+ceil)/2),(12.206,.06,ceil-floor),stone)
# Continuous lintel, sill and glazed-bay frame details.
for name,z,h in [('sill',floor+.055,.11),('head',ceil-.06,.12)]:
 box('Front_'+name,(0,front,z),(12.206,.13,h),white,.003)
for bi,(a,b) in enumerate([(-6.0545,-2.2765),(-1.9265,1.9265),(2.2765,6.0545)]):
 # Side display bays 2 panels. Central bay is paired entrance doors with sidelights.
 cuts=[a,(a+b)/2,b] if bi!=1 else [a,-.91,0,.91,b]
 for j,x in enumerate(cuts[1:-1]):box(f'Bay{bi}_mullion{j}',(x,front-.008,(floor+ceil)/2),(.045,.09,ceil-floor-.12),white,.002)
 for j,(l,r) in enumerate(zip(cuts,cuts[1:])):
  isdoor=bi==1 and j in [1,2];zlo=floor+.065;zhi=ceil-.12
  box(f'Bay{bi}_gasket{j}',((l+r)/2,front+.012,(zlo+zhi)/2),(r-l-.025,.035,zhi-zlo),dark)
  # Actual glass separated from opaque perimeter, no hidden full-face backing.
  objs.pop();g=bpy.context.object;bpy.data.objects.remove(g,do_unlink=True)
  for x in [l+.021,r-.021]:box(f'Bay{bi}_edge_gasket{j}_{x:.3f}',(x,front-.018,(zlo+zhi)/2),(.012,.026,zhi-zlo),dark)
  box(f'Bay{bi}_glass{j}',((l+r)/2,front+.022,(zlo+zhi)/2),(r-l-.055,.008,zhi-zlo-.02),glass)
  if isdoor:
   box(f'Door_lower_rail{j}',((l+r)/2,front-.035,floor+.10),(r-l-.05,.055,.065),white,.002)
   hx=r-.09 if j==1 else l+.09
   box(f'Door_pull{j}',(hx,front-.085,1.25),(.022,.027,.32),dark,.005)
   for hz in [1.11,1.39]:box(f'Door_pull_mount{j}_{hz}',(hx,front-.06,hz),(.025,.06,.025),white,.002)
# Observed central doorway header, left unbranded; vertical size is estimated.
box('Central_doorway_header', (0,front-.07,2.405), (3.853,.14,.23),white,.003)
# Visible end glazing, wide end jambs and low sill.
for sg in [-1,1]:
 x=sg*6.103
 for z,h in [(floor+.055,.11),(ceil-.06,.12)]:box(f'End{sg}_horizontal{z}',(x,.586,z),(.13,2.244,h),white,.003)
 box(f'End{sg}_middle_mullion',(x,.586,(floor+ceil)/2),(.09,.042,ceil-floor-.12),white,.002)
 for j,(a,b) in enumerate([(front+.07,.565),(.607,rear-.07)]):box(f'End{sg}_glass{j}',(x,.5*(a+b),(floor+ceil)/2),(.008,b-a,ceil-floor-.16),glass)
# Shallow dark fascia and visible warm underside. Roof dimensions estimated separately from 12.559 plan width.
roofW=12.76;roofD=3.64;roofY=.006;roofZ=2.77
box('Roof_skin_estimated',(0,roofY,roofZ),(roofW,roofD,.07),dark,.008)
box('Warm_soffit_estimated',(0,roofY,2.69),(roofW-.10,roofD-.10,.06),warm,.004)
for y in [roofY-roofD/2,roofY+roofD/2]:box('Long_dark_fascia',(0,y,2.727),(roofW,.075,.16),dark,.004)
for x in [-roofW/2,roofW/2]:box('End_dark_fascia',(x,roofY,2.727),(.075,roofD,.16),dark,.004)
# Subtle soffit panel joints, explicitly assumed subdivision rather than wood grain.
for i in range(1,13):box('Soffit_panel_joint'+str(i),(-roofW/2+i*roofW/13,roofY,2.657),(.009,roofD-.15,.005),dark)
# Mineral front fascia has real panel rhythm; joint count estimated.
for i in range(1,12):box('Base_panel_joint'+str(i),(-5.1295+i*10.259/12,-1.787,.115),(.009,.004,.19),dark)
box('Front_dark_base_trim',(0,-1.78,.23),(10.259,.04,.065),dark,.002)
for sg in [-1,1]:box('End_dark_base_trim'+str(sg),(sg*6.278,.55,.23),(.04,2.45,.065),dark,.002)
# Low front architectural rail. No advertising on panels. Layout is visual approximation.
for x in [-4.95,-2.475,0,2.475,4.95]:box('Front_rail_post'+str(x),(x,-1.69,.70),(.085,.085,.94),dark,.003)
box('Front_rail_top',(0,-1.69,1.17),(9.985,.055,.055),dark,.003)
for a,b in zip([-4.95,-2.475,0,2.475],[-2.475,0,2.475,4.95]):box('Unbranded_front_rail_glass'+str(a),((a+b)/2,-1.69,.74),(b-a-.085,.012,.80),glass)
# Observed end downpipe, simple corner elbows; no extra invented utilities.
def pipe(n,points,r=.027):
 for i,(a,b) in enumerate(zip(points,points[1:])):
  a,b=Vector(a),Vector(b);v=b-a;bpy.ops.mesh.primitive_cylinder_add(vertices=12,radius=r,depth=v.length,location=(a+b)/2);o=bpy.context.object;o.name=f'{n}_{i}';o.rotation_euler=v.to_track_quat('Z','Y').to_euler();o.data.materials.append(dark);objs.append(o)
pipe('Observed_left_downpipe',[(-6.24,1.75,2.70),(-6.24,1.75,.32),(-6.30,1.75,.22),(-6.30,1.75,.08)])
for z in [.55,1.65]:box('Downpipe_bracket'+str(z),(-6.23,1.745,z),(.085,.05,.035),white,.002)
# Permanent factual identifier only. Sponsor logos and ad art intentionally excluded.
box('Identifier_carrier_estimated',(-1.50,-1.76,3.025),(9.8,.075,.45),dark,.004)
bpy.ops.object.text_add(location=(-5.92,-1.805,2.89),rotation=(math.pi/2,0,0));t=bpy.context.object;t.name='SHIBU_HACHI_BOX_factual_identifier';t.data.body='SHIBU HACHI BOX';t.data.size=.37;t.data.extrude=.006;t.data.space_character=1.08;t.data.materials.append(white);bpy.ops.object.convert(target='MESH');objs.append(bpy.context.object)
# Join by material keeps predictable 5 primitives and material batching; name arch components above preserved in blend.
for o in objs:o['provenance']='Operator 2024 plan; exterior 2024 and 2026 observations. Vertical/depth details partly estimated.'
s['placement_status']='UNPLACED; no runtime registration; no existing object replacement'
s['reference_date_scope']='2024 measured floor plan, architecture visible in 2024/2026. Not a dated advertisement reconstruction.'
# Apply transforms for portable mesh geometry, then select only architecture.
bpy.ops.object.select_all(action='DESELECT')
for o in objs:o.select_set(True)
bpy.context.view_layer.objects.active=objs[0]
bpy.ops.object.transform_apply(location=True,rotation=True,scale=True)
# All mesh object origins at bottom centre (0,0,0).
# Export temporary material batches, retaining editable architectural components.
export_objs=[]
for material in mats.values():
 bpy.ops.object.select_all(action='DESELECT');copies=[]
 for original in objs:
  if original.data.materials[0] == material:
   o=original.copy();o.data=original.data.copy();s.collection.objects.link(o);o.select_set(True);copies.append(o)
 if copies:
  bpy.context.view_layer.objects.active=copies[0];bpy.ops.object.join();o=bpy.context.object;o.name='Batch_'+material.name;o.data.name=o.name+'_mesh';export_objs.append(o)
bpy.ops.object.select_all(action='DESELECT')
for o in export_objs:o.select_set(True)
bpy.ops.export_scene.gltf(filepath=str(out/'shibu_hachi_box.glb'),export_format='GLB',use_selection=True,export_yup=True,export_extras=False,export_cameras=False,export_lights=False,export_materials='EXPORT')
for o in export_objs:bpy.data.objects.remove(o,do_unlink=True)
bpy.ops.object.select_all(action='DESELECT')
for o in objs:o.select_set(True)
tri=sum(sum(len(p.vertices)-2 for p in o.data.polygons) for o in objs)
json.dump({'asset':'shibu_hachi_box','units':'metres','origin':'bottom footprint centre','front':'-Y in Blender','triangles':tri,'mesh_objects':len(objs),'materials':len(mats),'placement':'unplaced','estimated_roof_width':roofW,'measured_outer_plan_width':12.559,'measured_overall_plan_depth':3.572,'interior_clear_height':2.354,'roof_top_estimated':2.805},open(out/'model_stats.json','w'),indent=2)
bpy.ops.wm.save_as_mainfile(filepath=str(out/'shibu_hachi_box.blend'))
if args.render:
 s.render.engine='CYCLES';s.cycles.samples=24;s.cycles.use_denoising=True;s.render.resolution_x=1600;s.render.resolution_y=900;s.render.resolution_percentage=100;s.render.image_settings.file_format='PNG';s.render.film_transparent=False;s.world.color=(.3,.3,.3)
 s.view_settings.view_transform='AgX'
 # Stage floor only in render scene, never GLB or source blend.
 box('STUDIO_ONLY',(0,0,-.065),(200,200,.1),mat('STUDIO_ONLY',(.28,.31,.34),.85))
 for loc,power,size in [((0,-7,10),2500,9),((-8,1,7),1700,7),((7,4,8),2200,7)]:
  bpy.ops.object.light_add(type='AREA',location=loc);o=bpy.context.object;o.data.energy=power;o.data.shape='DISK';o.data.size=size;o.rotation_euler=(Vector((0,0,1))-o.location).to_track_quat('-Z','Y').to_euler()
 for name,loc,scale in [('oblique',(-13,-16,8),17.6),('photo_near',(-12,-15,3.8),16.0),('front',(0,-23,5.2),15.5),('side',(-22,0,1.3),8.0),('rear',(12,16,7),17.5)]:
  bpy.data.objects['STUDIO_ONLY'].hide_render=(name=='side')
  bpy.ops.object.camera_add(location=loc);c=bpy.context.object;c.rotation_euler=(Vector((0,0,1.3))-c.location).to_track_quat('-Z','Y').to_euler();c.data.type='ORTHO';c.data.clip_end=1000;c.data.ortho_scale=scale;c.data.type='PERSP' if name=='photo_near' else 'ORTHO';c.data.lens=42;s.camera=c;s.render.filepath=str(out/(name+'.png'));bpy.ops.render.render(write_still=True)
