import bpy, math, os, sys, json, hashlib
from mathutils import Vector
import numpy as np
OUT=os.path.dirname(os.path.abspath(__file__))
if '--' in sys.argv:
 a=sys.argv[sys.argv.index('--')+1:]
 if a: OUT=os.path.abspath(a[0])
os.makedirs(OUT,exist_ok=True)
bpy.ops.object.select_all(action='SELECT'); bpy.ops.object.delete(use_global=False)
for d in list(bpy.data.materials): bpy.data.materials.remove(d)
scene=bpy.context.scene; scene.unit_settings.system='METRIC';scene.unit_settings.scale_length=1
# Entirely original deterministic light-oak texture. No photographic pixels.
rng=np.random.default_rng(491); W,H=512,1024
x=np.arange(W)[None,:]/W;z=np.arange(H)[:,None]/H
warp=x+0.0028*np.sin(z*15)+0.0015*np.sin(z*39+x*17)
gr=.027*np.sin(warp*2*math.pi*89)+.013*np.sin(warp*2*math.pi*181)+.017*np.sin(warp*2*math.pi*17)
gr+=rng.normal(0,.006,(H,W)); pores=np.maximum(0,np.sin(warp*2*math.pi*147))**28*.030
base=np.array([.67,.49,.29]); rgb=np.clip(base[None,None,:]+(gr-pores)[:,:,None],0,1)
a=np.ones((H,W,4),dtype=np.float32);a[:,:,:3]=rgb
im=bpy.data.images.new('Original_light_oak_grain',width=W,height=H);im.pixels.foreach_set(a.ravel());im.filepath_raw=os.path.join(OUT,'oak_grain.png');im.file_format='PNG';im.save();im.pack()
wood=bpy.data.materials.new('Light oak veneer - original texture');wood.use_nodes=True
bs=wood.node_tree.nodes.get('Principled BSDF');bs.inputs['Roughness'].default_value=.59
tex=wood.node_tree.nodes.new('ShaderNodeTexImage');tex.image=im;wood.node_tree.links.new(tex.outputs['Color'],bs.inputs['Base Color'])
def mat(n,col,rough):
 m=bpy.data.materials.new(n);m.diffuse_color=(*col,1);m.use_nodes=True;p=m.node_tree.nodes.get('Principled BSDF');p.inputs['Base Color'].default_value=(*col,1);p.inputs['Roughness'].default_value=rough;return m
white=mat('Warm white rack backing and coated rails',(.79,.80,.77),.48)
objects=[]
def box(n,loc,scale,m,bevel=.002):
 bpy.ops.mesh.primitive_cube_add(size=1,location=loc);o=bpy.context.object;o.name=n;o.dimensions=scale;bpy.ops.object.transform_apply(location=False,rotation=False,scale=True);o.data.materials.append(m)
 # UVs stay vertical on front and side faces, with horizontal run on top.
 uv=o.data.uv_layers.active
 for p in o.data.polygons:
  for li in p.loop_indices:
   v=o.data.vertices[o.data.loops[li].vertex_index].co
   if abs(p.normal.z)>.5: u,t=v.x/.7+.5,v.y/.7+.5
   elif abs(p.normal.y)>.5: u,t=v.x/.7+.5,v.z/1.0+.5
   else:u,t=v.y/.7+.5,v.z/1.0+.5
   uv.data[li].uv=(u,t)
 if bevel:
  mod=o.modifiers.new('Small physical edge bevel','BEVEL');mod.width=bevel;mod.segments=3;bpy.context.view_layer.objects.active=o;bpy.ops.object.modifier_apply(modifier=mod.name)
 for p in o.data.polygons:p.use_smooth=False
 objects.append(o);return o
# Dimensions are photo-derived estimates, not measured manufacturer dimensions.
# Front faces negative Y, counter width 2.4m, depth .56m, height .98m.
box('Countertop', (0,0,.9575),(2.4,.56,.045),wood,.003)
box('Right oak front',(0.355,-.258,.4675),(1.69,.034,.935),wood)
box('Left stile',(-1.165,-.258,.4675),(.07,.034,.935),wood)
box('Rack right stile',(-.525,-.258,.4675),(.07,.034,.935),wood)
box('Rack upper lintel',(-.845,-.258,.885),(.57,.034,.1),wood)
box('Rack lower plinth',(-.845,-.258,.070),(.57,.034,.14),wood)
box('Rack middle separator',(-.845,-.258,.48),(.57,.034,.055),wood)
# Box shell is deliberately plain; unseen rear construction is provisional.
box('Left side',(-1.182,0,.4675),(.036,.49,.935),wood)
box('Right side',(1.182,0,.4675),(.036,.49,.935),wood)
box('Provisional plain rear',(0,.243,.4675),(2.328,.026,.935),wood)
box('Provisional bottom',(0,0,.018),(2.328,.46,.036),wood)
for label,lo,hi in [('lower',.14,.4525),('upper',.5075,.835)]:
 box(label+' recessed pale back',(-.845,-.125,(lo+hi)/2),(.57,.014,hi-lo),white,.001)
 box(label+' rack shelf',(-.845,-.194,lo+.007),(.57,.125,.014),wood,.001)
 for j in range(3):
  h=lo+.065+j*.068
  box(label+' white horizontal rail '+str(j+1),(-.845,-.28,h),(.566,.008,.006),white,.0015)
 for k,xx in enumerate([ -1.124,-.845,-.566]):
  box(label+' white upright '+str(k+1),(xx,-.28,lo+.14),(.006,.008,.26),white,.0015)
# A single root gives a bottom-centre origin and explicit authored orientation.
root=bpy.data.objects.new('SHIBUHACHIBOX_counter_bottom_center',None);scene.collection.objects.link(root)
root['dimensions_estimated_m']='2.40 x 0.56 x 0.98';root['source_period']='September / December 2024, persistence in 2026 unverified';root['front_direction']='-Y';root['unplaced']=True
for o in objects:o.parent=root
bpy.ops.object.select_all(action='DESELECT')
for o in objects+[root]:o.select_set(True)
bpy.context.view_layer.objects.active=root
# Export canonical separate parts, then losslessly batch normal/UV data by material.
export_path=os.path.join(OUT,'shibuhachibox_counter.glb')
bpy.ops.export_scene.gltf(filepath=export_path,export_format='GLB',use_selection=True,export_yup=True,export_apply=True)
import runpy
runpy.run_path(os.path.join(os.path.dirname(os.path.abspath(__file__)),'batch_export.py'))['batch_glb'](export_path)
# Render rig intentionally excluded from GLB.
world=bpy.data.worlds.new('Neutral studio');scene.world=world;world.use_nodes=True;world.node_tree.nodes['Background'].inputs[0].default_value=(.8,.8,.8,1);world.node_tree.nodes['Background'].inputs[1].default_value=.45
for n,loc,power,size in [('Key',(-3,-4,5),550,4),('Fill',(3,-1,3),300,3)]:
 d=bpy.data.lights.new(n,'AREA');d.energy=power;d.shape='DISK';d.size=size;o=bpy.data.objects.new(n,d);scene.collection.objects.link(o);o.location=loc;o.rotation_euler=(Vector((0,0,.5))-o.location).to_track_quat('-Z','Y').to_euler()
d=bpy.data.cameras.new('Inspection_camera');cam=bpy.data.objects.new('Inspection_camera',d);scene.collection.objects.link(cam);scene.camera=cam
scene.render.engine='CYCLES';scene.cycles.samples=32;scene.cycles.use_denoising=True;scene.render.resolution_x=1200;scene.render.resolution_y=800;scene.render.resolution_percentage=100;scene.render.image_settings.file_format='PNG';scene.render.film_transparent=True
scene.view_settings.view_transform='AgX'
views=[('front',(0,-5,.54),(0,0,.49),True),('side',(4,0,.6),(0,0,.49),True),('photo_near',(2.5,-4.4,2.3),(0,0,.48),False)]
for name,pos,target,ortho in views:
 cam.location=pos;cam.rotation_euler=(Vector(target)-cam.location).to_track_quat('-Z','Y').to_euler();d.type='ORTHO' if ortho else 'PERSP';d.ortho_scale=2.7 if name=='front' else 1.8;d.lens=54
 scene.render.filepath=os.path.join(OUT,name+'.png')
 if os.environ.get('COUNTER_SKIP_RENDER') != '1': bpy.ops.render.render(write_still=True)
# Save with final photo-near viewpoint and packed texture.
scene.render.filepath='//photo_near.png';im.filepath='//oak_grain.png'
bpy.ops.wm.save_as_mainfile(filepath=os.path.join(OUT,'shibuhachibox_counter.blend'))
tri=sum(sum(len(p.vertices)-2 for p in o.data.polygons) for o in objects)
verts=[o.matrix_world@v.co for o in objects for v in o.data.vertices]
mins=[min(v[i] for v in verts) for i in range(3)];maxs=[max(v[i] for v in verts) for i in range(3)]
report={'blender':bpy.app.version_string,'meshes':len(objects),'triangles':tri,'materials':2,'bounds_blender_m':[mins,maxs],'dimensions_m':[maxs[i]-mins[i] for i in range(3)],'root_origin':[0,0,0],'front':'-Y','placement':'unplaced','tests':{'height_exact':abs(maxs[2]-.98)<1e-6,'bottom_zero':abs(mins[2])<1e-6,'width_2_4':abs(maxs[0]-mins[0]-2.4)<1e-6,'triangle_budget':tri<8000,'finite_geometry':all(math.isfinite(c) for v in verts for c in v)}}
assert all(report['tests'].values()),report
with open(os.path.join(OUT,'validation.json'),'w') as f:json.dump(report,f,indent=2)
print('VALIDATION',json.dumps(report))
