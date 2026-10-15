"""Blender 4.2.3 procedural visible soffit fixture; no third-party assets.
blender -b -P source/generate.py -- --output output --render [--context-glb PATH]
"""
import bpy, math, json, sys, argparse
from pathlib import Path
from mathutils import Vector
p=argparse.ArgumentParser();p.add_argument('--output',default='output');p.add_argument('--render',action='store_true');p.add_argument('--context-glb');a=p.parse_args(sys.argv[sys.argv.index('--')+1:] if '--' in sys.argv else [])
out=Path(a.output).resolve();out.mkdir(parents=True,exist_ok=True)
bpy.ops.object.select_all(action='SELECT');bpy.ops.object.delete(use_global=False)
s=bpy.context.scene;s.unit_settings.system='METRIC';s.unit_settings.scale_length=1
mats=[]
for name,col,rough,metal in [('Pale_housing',(.73,.75,.72),.42,.05),('Dark_dome',(.022,.028,.031),.23,.05)]:
 m=bpy.data.materials.new(name);m.use_nodes=True;m.diffuse_color=(*col,1);bs=m.node_tree.nodes.get('Principled BSDF');bs.inputs['Base Color'].default_value=(*col,1);bs.inputs['Roughness'].default_value=rough;bs.inputs['Metallic'].default_value=metal;mats.append(m)
def lathe(name,profile,material):
 # profile includes near-axis vertices; capped ends avoid nonmanifold pole fans
 n=32;v=[];f=[]
 for r,z in profile:
  v.extend([(r*math.cos(i*math.tau/n),r*math.sin(i*math.tau/n),z) for i in range(n)])
 for j in range(len(profile)-1):
  for i in range(n):f.append((j*n+i,j*n+(i+1)%n,(j+1)*n+(i+1)%n,(j+1)*n+i))
 f.append(tuple(reversed(range(n))));f.append(tuple((len(profile)-1)*n+i for i in range(n)))
 me=bpy.data.meshes.new(name);me.from_pydata(v,[],f);me.update();ob=bpy.data.objects.new(name,me);s.collection.objects.link(ob);me.materials.append(material)
 for face in me.polygons:face.use_smooth=len(face.vertices)==4
 return ob
# Lowest visible dome at z=0; diameter 0.12 m and height 0.09 m are estimates.
objs=[lathe('Visible_dark_dome',[(.002,0),(.017,.003),(.032,.011),(.041,.023),(.045,.036),(.045,.043)],mats[1]),lathe('Pale_tapered_housing',[(.044,.038),(.049,.043),(.057,.059),(.057,.079),(.055,.084)],mats[0]),lathe('Shallow_mount_flange',[(.057,.080),(.060,.083),(.060,.089),(.058,.090)],mats[0])]
for o in objs:o['dimension_status']='Estimated, no manufacturer identification';o['asset_id']='shibu_hachi_box_soffit_dome_fixture'
bpy.ops.object.select_all(action='DESELECT')
for o in objs:o.select_set(True)
bpy.context.view_layer.objects.active=objs[0]
s['mount_datum_z_m']=.09;s['integration_status']='Unplaced asset; context translation only, no runtime changes'
bpy.ops.export_scene.gltf(filepath=str(out/'soffit_dome_fixture.glb'),export_format='GLB',use_selection=True,export_yup=True,export_extras=False,export_cameras=False,export_lights=False)
bpy.ops.wm.save_as_mainfile(filepath=str(out/'soffit_dome_fixture.blend'))
tri=sum(sum(len(f.vertices)-2 for f in o.data.polygons) for o in objs)
json.dump({'asset':'shibu_hachi_box_soffit_dome_fixture','metres':True,'diameter':.12,'height':.09,'dimension_status':'estimated','origin':'bottom centre','mount_plane_blender_z':.09,'triangles':tri,'objects':3,'materials':2,'runtime_registered':False},open(out/'stats.json','w'),indent=2)
if not a.render:raise SystemExit
s.render.engine='CYCLES';s.cycles.samples=32;s.cycles.use_denoising=True;s.render.resolution_x=1000;s.render.resolution_y=800;s.render.resolution_percentage=100;s.render.image_settings.file_format='PNG';s.world.color=(.25,.25,.25);s.view_settings.view_transform='AgX'
lights=[]
for loc,power,size in [((-.4,-.4,.6),35,.5),((.4,.2,.35),25,.4)]:
 bpy.ops.object.light_add(type='AREA',location=loc);l=bpy.context.object;l.data.energy=power;l.data.shape='DISK';l.data.size=size;l.rotation_euler=(Vector((0,0,.045))-l.location).to_track_quat('-Z','Y').to_euler();lights.append(l)
def render(name,loc,target,scale):
 bpy.ops.object.camera_add(location=loc);c=bpy.context.object;c.rotation_euler=(Vector(target)-c.location).to_track_quat('-Z','Y').to_euler();c.data.type='ORTHO';c.data.ortho_scale=scale;c.data.clip_start=.001;s.camera=c;s.render.filepath=str(out/(name+'.png'));bpy.ops.render.render(write_still=True)
for name,loc in [('front',(0,-.5,.045)),('side',(-.5,0,.045)),('oblique',(-.3,-.5,-.08))]:render(name,loc,(0,0,.045),.19)
if a.context_glb:
 # Context-only assembled scene is never written to the distributable GLB/blend.
 for o in objs:o.location=(-6.00,-1.48,2.57)
 bpy.ops.import_scene.gltf(filepath=str(Path(a.context_glb).resolve()))
 for l in lights:bpy.data.objects.remove(l,do_unlink=True)
 for loc,power,size in [((-7,-8,7),2000,6),((-9,-2,1.5),300,3),((3,2,8),2200,8)]:
  bpy.ops.object.light_add(type='AREA',location=loc);l=bpy.context.object;l.data.energy=power;l.data.size=size;l.rotation_euler=(Vector((-5,-1,2))-l.location).to_track_quat('-Z','Y').to_euler()
 render('context_detail',(-9,-5,1.8),(-5.8,-1.3,2.45),1.65)
 render('context_overview',(-13,-16,5), (0,0,1.35),16)
