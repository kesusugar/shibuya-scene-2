"""Blender 4.2.3 procedural visible roof-corner device; no third-party assets.
blender -b -P source/generate.py -- --output output --render
"""
import bpy, math, json, sys, argparse
from pathlib import Path
from mathutils import Vector
p=argparse.ArgumentParser();p.add_argument('--output',default='output');p.add_argument('--render',action='store_true');a=p.parse_args(sys.argv[sys.argv.index('--')+1:] if '--' in sys.argv else [])
out=Path(a.output).resolve();out.mkdir(parents=True,exist_ok=True)
bpy.ops.object.select_all(action='SELECT');bpy.ops.object.delete(use_global=False)
s=bpy.context.scene;s.unit_settings.system='METRIC';s.unit_settings.scale_length=1
mats=[]
for name,col,rough,metal in [('Pale_housing',(.73,.75,.72),.42,.05),('Dark_dome',(.022,.028,.031),.23,.05)]:
 m=bpy.data.materials.new(name);m.use_nodes=True;m.diffuse_color=(*col,1);bs=m.node_tree.nodes.get('Principled BSDF');bs.inputs['Base Color'].default_value=(*col,1);bs.inputs['Roughness'].default_value=rough;bs.inputs['Metallic'].default_value=metal;mats.append(m)
def lathe(name,profile,material):
 # profile includes near-axis vertices; capped ends avoid nonmanifold pole fans
 n=24;v=[];f=[]
 for r,z in profile:
  v.extend([(r*math.cos(i*math.tau/n),r*math.sin(i*math.tau/n),z) for i in range(n)])
 for j in range(len(profile)-1):
  for i in range(n):f.append((j*n+i,j*n+(i+1)%n,(j+1)*n+(i+1)%n,(j+1)*n+i))
 f.append(tuple(reversed(range(n))));f.append(tuple((len(profile)-1)*n+i for i in range(n)))
 me=bpy.data.meshes.new(name);me.from_pydata(v,[],f);me.update();ob=bpy.data.objects.new(name,me);s.collection.objects.link(ob);me.materials.append(material)
 for face in me.polygons:face.use_smooth=len(face.vertices)==4
 return ob
# Observed visible portion only. Photo cuts the upper mounting assembly off.
# Diameter .16 m and visible height .23 m are low-confidence estimates.
objs=[lathe('Dark_lower_dome',[(.001,0),(.022,.004),(.042,.015),(.055,.030),(.063,.049),(.065,.066),(.065,.077)],mats[1]),
lathe('White_lower_collar',[(.064,.071),(.074,.077),(.080,.087),(.080,.101)],mats[0]),
lathe('Dark_separator_ring',[(.077,.099),(.078,.105),(.078,.111)],mats[1]),
lathe('White_cylindrical_body',[(.078,.109),(.080,.117),(.080,.204),(.076,.216),(.076,.230)],mats[0])]
for o in objs:o['dimension_status']='Estimated, no manufacturer identification';o['asset_id']='shibu_hachi_box_corner_dome_visible_fragment'
bpy.ops.object.select_all(action='DESELECT')
for o in objs:o.select_set(True)
bpy.context.view_layer.objects.active=objs[0]
s['estimated_cutoff_interface_z_m']=.23;s['integration_status']='Unplaced asset; context translation only, no runtime changes'
bpy.ops.export_scene.gltf(filepath=str(out/'corner_dome_visible_fragment.glb'),export_format='GLB',use_selection=True,export_yup=True,export_extras=False,export_cameras=False,export_lights=False)
bpy.ops.wm.save_as_mainfile(filepath=str(out/'corner_dome_visible_fragment.blend'))
tri=sum(sum(len(f.vertices)-2 for f in o.data.polygons) for o in objs)
json.dump({'asset':'shibu_hachi_box_corner_dome_visible_fragment','metres':True,'diameter':.16,'visible_height':.23,'dimension_status':'low-confidence inferred; upper assembly clipped by photograph','origin':'bottom centre','estimated_cutoff_interface_blender_z':.23,'triangles':tri,'objects':4,'materials':2,'runtime_registered':False,'date_evidence':'2026-08-08; not verified for 2025','complete_device':False},open(out/'stats.json','w'),indent=2)
if not a.render:raise SystemExit
s.render.engine='CYCLES';s.cycles.samples=32;s.cycles.use_denoising=True;s.render.resolution_x=900;s.render.resolution_y=900;s.render.resolution_percentage=100;s.render.image_settings.file_format='PNG';s.world.color=(.25,.25,.25);s.view_settings.view_transform='AgX'
lights=[]
for loc,power,size in [((-.4,-.4,.6),35,.5),((.4,.2,.35),25,.4)]:
 bpy.ops.object.light_add(type='AREA',location=loc);l=bpy.context.object;l.data.energy=power;l.data.shape='DISK';l.data.size=size;l.rotation_euler=(Vector((0,0,.115))-l.location).to_track_quat('-Z','Y').to_euler();lights.append(l)
def render(name,loc,target,scale):
 bpy.ops.object.camera_add(location=loc);c=bpy.context.object;c.rotation_euler=(Vector(target)-c.location).to_track_quat('-Z','Y').to_euler();c.data.type='ORTHO';c.data.ortho_scale=scale;c.data.clip_start=.001;s.camera=c;s.render.filepath=str(out/(name+'.png'));bpy.ops.render.render(write_still=True)
for name,loc in [('front',(0,-.5,.115)),('side',(-.5,0,.115)),('oblique',(-.3,-.5,.22))]:render(name,loc,(0,0,.115),.34)
