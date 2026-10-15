"""Blender 4.2.3. Procedural lettering only; no source photo or external fonts.
blender -b --python source/generate.py -- --output output [--context path/to/parent.blend]
"""
import bpy, math, argparse,sys,json
from pathlib import Path
from mathutils import Vector
p=argparse.ArgumentParser();p.add_argument('--output',default='output');p.add_argument('--context');p.add_argument('--no-render',action='store_true');a=p.parse_args(sys.argv[sys.argv.index('--')+1:] if '--' in sys.argv else [])
out=Path(a.output).resolve();out.mkdir(parents=True,exist_ok=True)
bpy.ops.object.select_all(action='SELECT');bpy.ops.object.delete(use_global=False)
s=bpy.context.scene;s.unit_settings.system='METRIC';s.unit_settings.scale_length=1
# Existing parent carrier centre (0,-.606,2.405), face -Y at -.676.
# Lettering assembly origin placed at (0,-.686,2.315), an 8 mm rear gap.
red=bpy.data.materials.new('Estimated_dark_red_lettering');red.diffuse_color=(.30,.035,.027,1);red.use_nodes=True;red.node_tree.nodes['Principled BSDF'].inputs['Base Color'].default_value=red.diffuse_color
white=bpy.data.materials.new('Pale_information_glyph');white.diffuse_color=(.80,.82,.78,1);white.use_nodes=True;white.node_tree.nodes['Principled BSDF'].inputs['Base Color'].default_value=white.diffuse_color
black=bpy.data.materials.new('Estimated_dark_trailing_lettering');black.diffuse_color=(.025,.025,.025,1);black.use_nodes=True;black.node_tree.nodes['Principled BSDF'].inputs['Base Color'].default_value=black.diffuse_color
objs=[]
def txt(body,x,z,height,width,mat):
 bpy.ops.object.text_add(location=(x,0,z),rotation=(math.pi/2,0,0));o=bpy.context.object;o.name='Observed_'+body.replace(' ','_');o.data.body=body;o.data.size=1;o.data.resolution_u=3;o.data.extrude=0;o.data.materials.append(mat)
 bpy.ops.object.convert(target='MESH')
 xs=[v.co.x for v in o.data.vertices];ys=[v.co.y for v in o.data.vertices]
 for v in o.data.vertices:
  v.co.x=(v.co.x-min(xs))*width/(max(xs)-min(xs));v.co.y=(v.co.y-min(ys))*height/(max(ys)-min(ys))
 bpy.ops.object.transform_apply(location=False,rotation=False,scale=True);objs.append(o);return o
# Bfont stands in for unidentified actual sans-serif font. Proportion is inferred.
t=txt('Tourist Information',-1.48,0,.16,2.32,red)
# Circular i symbol is visible; this simple procedural approximation is not a copied logo.
bpy.ops.mesh.primitive_cylinder_add(vertices=32,radius=.09,depth=.002,location=(-1.65,0,.09),rotation=(math.pi/2,0,0));o=bpy.context.object;o.name='Observed_information_disk';o.data.materials.append(red);objs.append(o)
i=txt('i',-1.669,.028,.126,.038,white);i.location.y=-.003
txt('& Souvenir Store',.88,0,.092,1.03,black)
# Apply all transforms, then enforce exact bottom-centre origin from all vertex bounds.
bpy.ops.object.select_all(action='DESELECT')
for o in objs:o.select_set(True)
bpy.context.view_layer.objects.active=objs[0];bpy.ops.object.transform_apply(location=True,rotation=True,scale=True)
lo=Vector(tuple(min(v.co[k] for o in objs for v in o.data.vertices) for k in range(3)));hi=Vector(tuple(max(v.co[k] for o in objs for v in o.data.vertices) for k in range(3)));shift=Vector(((lo.x+hi.x)/2,(lo.y+hi.y)/2,lo.z))
for o in objs:
 for v in o.data.vertices:v.co-=shift
 o['reference']='CASIO exterior photograph 2024-11-15. Frontal photo confirms Tourist Information & Souvenir Store and circular i.'
# One mesh with two material primitives; component objects remain editable in blend.
def export():
 bpy.ops.object.select_all(action='DESELECT');copies=[]
 for original in objs:
  o=original.copy();o.data=original.data.copy();s.collection.objects.link(o);o.select_set(True);copies.append(o)
 bpy.context.view_layer.objects.active=copies[0];bpy.ops.object.join();o=bpy.context.object;o.name='shibu_hachi_box_information_header';o.data.name=o.name+'_mesh'
 bpy.ops.export_scene.gltf(filepath=str(out/'shibu_hachi_box_information_header.glb'),export_format='GLB',use_selection=True,export_yup=True,export_extras=False,export_cameras=False,export_lights=False)
 bpy.data.objects.remove(o,do_unlink=True)
export()
s['placement']='Unplaced. Add-on only; keep existing blank carrier. Blender offset [0,-0.686,2.315] in parent local axes, approximate; never applied to runtime.'
tri=sum(len(p.vertices)-2 for o in objs for p in o.data.polygons)
stats={'triangles':tri,'dimensions_m':list(hi-lo),'materials':3,'origin':'bottom footprint centre','front':'Blender -Y','parent_blender_offset_m':[0,-.686,2.315],'status':'unplaced lettering only','font':'Blender bundled Bfont, approximate','confirmed_text':'Tourist Information & Souvenir Store'}
(out/'model_stats.json').write_text(json.dumps(stats,indent=2));bpy.ops.wm.save_as_mainfile(filepath=str(out/'shibu_hachi_box_information_header.blend'))
if a.no_render:sys.exit(0)
s.render.engine='CYCLES';s.cycles.samples=16;s.cycles.use_denoising=True;s.render.resolution_x=1400;s.render.resolution_y=500;s.render.resolution_percentage=100;s.render.image_settings.file_format='PNG';s.world.color=(.5,.5,.5);s.view_settings.view_transform='AgX'
for loc in [(0,-4,6),(-4,-3,2)]:
 bpy.ops.object.light_add(type='AREA',location=loc);o=bpy.context.object;o.data.energy=450;o.data.size=5;o.rotation_euler=(Vector((0,0,.1))-o.location).to_track_quat('-Z','Y').to_euler()
def render(name,loc,target,scale):
 bpy.ops.object.camera_add(location=loc);c=bpy.context.object;c.rotation_euler=(Vector(target)-c.location).to_track_quat('-Z','Y').to_euler();c.data.type='ORTHO';c.data.ortho_scale=scale;s.camera=c;s.render.filepath=str(out/(name+'.png'));bpy.ops.render.render(write_still=True)
render('front',(0,-5,.09),(0,0,.09),4.1)
render('oblique',(-2,-5,1.2),(0,0,.09),4.2)
if a.context:
 with bpy.data.libraries.load(str(Path(a.context).resolve()),link=False) as (src,dst):dst.objects=[n for n in src.objects]
 for o in dst.objects:
  if o and o.type=='MESH':s.collection.objects.link(o)
 for o in objs:o.location=Vector((0,-.686,2.315))
 s.render.resolution_y=700
 for o in objs:o.hide_render=True
 render('context_before',(-4,-11,3.0),(0,-.5,2.26),5.5)
 for o in objs:o.hide_render=False
 render('context_after',(-4,-11,3.0),(0,-.5,2.26),5.5)
