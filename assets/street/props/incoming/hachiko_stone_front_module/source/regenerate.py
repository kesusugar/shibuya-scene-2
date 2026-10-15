"""Blender 4.2.3. Run: blender -b --python-exit-code 1 -P source/regenerate.py -- OUTPUT_DIRECTORY
A replacement FRONT wall assembly only; no placement or surrounding geometry.
"""
import bpy,math,json,sys,hashlib
from pathlib import Path
from mathutils import Vector
import numpy as np
OUT=Path(sys.argv[sys.argv.index('--')+1]).resolve() if '--' in sys.argv else Path(__file__).resolve().parent.parent
OUT.mkdir(parents=True,exist_ok=True)
bpy.ops.wm.read_factory_settings(use_empty=True)
bpy.context.scene.unit_settings.system='METRIC';bpy.context.scene.unit_settings.scale_length=1
M={};objects=[]
def material(name,color,metal,rough):
 m=bpy.data.materials.new(name);m.use_nodes=True;p=m.node_tree.nodes.get('Principled BSDF');p.inputs['Base Color'].default_value=(*color,1);p.inputs['Metallic'].default_value=metal;p.inputs['Roughness'].default_value=rough;M[name]=m;return m
stone=material('granite_procedural',(.14,.15,.14),0,.91)
material('fixture_frame',(.025,.028,.027),.35,.72)
material('fixture_diffuser',(.19,.22,.20),0,.62)
# Original deterministic synthetic granite, not pixels derived from any photo.
rng=np.random.default_rng(20261015);noise=rng.normal(.30,.045,(256,256));fleck=rng.random((256,256));noise[fleck<.055]*=.53;noise[fleck>.95]+=.17;noise=np.clip(noise,.10,.58)
rgba=np.ones((256,256,4),dtype=np.float32);rgba[:,:,:3]=noise[:,:,None]*np.array([.98,1.0,.97])[None,None,:]
im=bpy.data.images.new('synthetic_granite',width=256,height=256);im.pixels.foreach_set(rgba.ravel());im.filepath_raw=str(OUT/'synthetic_granite.png');im.file_format='PNG';im.save();im.pack()
t=stone.node_tree.nodes.new('ShaderNodeTexImage');t.image=im;t.extension='REPEAT';stone.node_tree.links.new(t.outputs['Color'],stone.node_tree.nodes['Principled BSDF'].inputs['Base Color'])
def box(name,loc,size,mat,bevel):
 bpy.ops.mesh.primitive_cube_add(size=1,location=loc);o=bpy.context.object;o.name=name;o.scale=size;bpy.ops.object.transform_apply(location=False,rotation=False,scale=True)
 if bevel:
  mod=o.modifiers.new('physical_edge','BEVEL');mod.width=bevel;mod.segments=1;bpy.ops.object.modifier_apply(modifier=mod.name)
 o.data.materials.append(M[mat]);objects.append(o)
 # Real-world triplanar UV projection, 0.25 m tile size.
 uv=o.data.uv_layers.active or o.data.uv_layers.new()
 for face in o.data.polygons:
  axis=max(range(3),key=lambda a:abs(face.normal[a]));axes=[a for a in range(3) if a!=axis]
  for li in face.loop_indices:
   p=o.data.vertices[o.data.loops[li].vertex_index].co+o.location;uv.data[li].uv=(p[axes[0]]/.25,p[axes[1]]/.25)
 return o
WIDTH=2.35;HEIGHT=.52;THICKNESS=.22;CAP_DEPTH=.27;CAP_HEIGHT=.07
# Front plane +Y=.11, rear plane -.11. Cap bounds +/-.135. Bottom is Z=0.
y=.11;count=math.ceil(WIDTH/.18);step=WIDTH/count;gap=.006;lw=.46;lh=.17;lz=.045
for i in range(count):
 xa=-WIDTH/2+i*step+gap/2;xb=-WIDTH/2+(i+1)*step-gap/2
 cuts=sorted(set([xa,xb]+[v for v in [-lw/2,lw/2] if xa<v<xb]))
 for aa,bb in zip(cuts,cuts[1:]):
  spans=[(0,lz),(lz+lh,HEIGHT)] if -lw/2<(aa+bb)/2<lw/2 else [(0,HEIGHT)]
  for za,zb in spans:box('front_stone',( (aa+bb)/2,0,(za+zb)/2),(bb-aa,THICKNESS,zb-za),'granite_procedural',.002)
 box('coping_stone',((xa+xb)/2,0,HEIGHT+CAP_HEIGHT/2),(xb-xa,CAP_DEPTH,CAP_HEIGHT),'granite_procedural',.004)
fy=y-.022;fz=lz+lh/2
box('fixture_back',(0,fy-.026,fz),(lw,.018,lh),'fixture_frame',.003)
box('diffuser',(0,fy-.014,fz),(lw-.045,.006,lh-.04),'fixture_diffuser',.002)
for x in [-lw/2+.009,lw/2-.009]:box('frame_jamb',(x,fy,fz),(.018,.04,lh),'fixture_frame',.002)
for z in [lz+.009,lz+lh-.009]:box('frame_edge',(0,fy,z),(lw,.04,.018),'fixture_frame',.002)
for z in [fz-.025,fz+.025]:box('horizontal_guard',(0,fy+.003,z),(lw-.036,.014,.012),'fixture_frame',.001)
# Consolidate by material, bake transforms, and keep all nodes at bottom-centre origin.
groups={name:[o for o in objects if o.data.materials[0]==mat] for name,mat in M.items()}
for name,group in groups.items():
 bpy.ops.object.select_all(action='DESELECT')
 for o in group:o.select_set(True)
 bpy.context.view_layer.objects.active=group[0]
 if len(group)>1:bpy.ops.object.join()
 o=bpy.context.object;o.name='hachiko_front_'+name
 bpy.ops.object.transform_apply(location=True,rotation=True,scale=True)
bpy.ops.object.select_all(action='SELECT')
bpy.context.scene.cursor.location=(0,0,0);bpy.ops.object.origin_set(type='ORIGIN_CURSOR')
bpy.ops.export_scene.gltf(filepath=str(OUT/'hachiko_stone_front_module.glb'),export_format='GLB',export_yup=True)
im.filepath='//synthetic_granite.png'
bpy.ops.wm.save_as_mainfile(filepath=str(OUT/'hachiko_stone_front_module.blend'),compress=True)
vertices=[o.matrix_world@v.co for o in bpy.context.scene.objects if o.type=='MESH' for v in o.data.vertices]
stats={'blender':bpy.app.version_string,'triangles':sum(len(p.vertices)-2 for o in bpy.context.scene.objects if o.type=='MESH' for p in o.data.polygons),'materials':len(M),'bounds_blender':[[min(v[i] for v in vertices) for i in range(3)],[max(v[i] for v in vertices) for i in range(3)]],'stone_count':count,'units':'metres','origin':'bottom centre','lighting':'non-emissive; actual intensity and lamp technology unknown','scope':'replacement front facing and coping only; no return walls, rear walls, planting, rails or placement'}
(OUT/'model_stats.json').write_text(json.dumps(stats,indent=2)+'\n')
