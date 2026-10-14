"""Provisional photo-informed Shibuya bollard. Run: blender -b --python regenerate_bollard.py
All absolute dimensions are estimates, NOT measured. Blender 4.2.3, no third-party Python dependencies.
Output directory defaults to this script's directory. Override: -- --output /path
"""
import bpy, math, json, sys
from pathlib import Path
from mathutils import Vector
OUT=Path(__file__).resolve().parent
if '--output' in sys.argv: OUT=Path(sys.argv[sys.argv.index('--output')+1])
OUT.mkdir(parents=True,exist_ok=True)
# EDIT THESE VALUES. Units: meters. No verified physical scale exists in the photo.
HEIGHT=0.800
DIAMETER=0.114
BAND_HEIGHT=0.080  # approx 11–13 px / 16–18 px body width in the left post
TOP_TO_BAND=0.100 # approx 13–16 px / 16–18 px body width; includes cap
CAP_HEIGHT=0.010 # inferred construction, not resolved in the photo
EDGE_RADIUS=0.002 # inferred rounded rim, not a measured detail
SEGMENTS=96
bpy.ops.object.select_all(action='SELECT'); bpy.ops.object.delete(use_global=False)
scene=bpy.context.scene
scene.unit_settings.system='METRIC';scene.unit_settings.scale_length=1.0
scene.unit_settings.length_unit='METERS'
root=bpy.data.objects.new('Bollard_Root_BASE_CENTER',None);scene.collection.objects.link(root)
root['dimension_status']='PROVISIONAL: all absolute dimensions are estimates, not measured'
root['height_m']=HEIGHT;root['diameter_m']=DIAMETER
root['photo_credit']='RuinDig/Yuki Uchida, 2025-07-13, CC BY 4.0 (Commons attribution)'
root['unseen_geometry']='Base and lower shaft inferred; no foundation or fastening details modeled'
def material(name,color,roughness):
 m=bpy.data.materials.new(name);m.diffuse_color=(*color,1);m.use_nodes=True
 bs=m.node_tree.nodes.get('Principled BSDF');bs.inputs['Base Color'].default_value=(*color,1);bs.inputs['Roughness'].default_value=roughness
 return m
white=material('Paint_White_Estimated',(0.82,0.84,0.85),.38)
yellow=material('Yellow_Band_Approximate_Not_Retroreflective',(1.0,.45,.003),.65)
def lathe(name,profile,mat):
 verts=[]
 for r,z in profile:
  for i in range(SEGMENTS):
   a=2*math.pi*i/SEGMENTS;verts.append((r*math.cos(a),r*math.sin(a),z))
 faces=[]
 for j in range(len(profile)-1):
  for i in range(SEGMENTS):
   a=j*SEGMENTS+i;b=j*SEGMENTS+(i+1)%SEGMENTS;faces.append((a,b,b+SEGMENTS,a+SEGMENTS))
 faces.append(tuple(reversed(range(SEGMENTS))));faces.append(tuple((len(profile)-1)*SEGMENTS+i for i in range(SEGMENTS)))
 mesh=bpy.data.meshes.new(name+'_Mesh');mesh.from_pydata(verts,[],faces);mesh.update()
 obj=bpy.data.objects.new(name,mesh);scene.collection.objects.link(obj);obj.parent=root;obj.data.materials.append(mat)
 for p in mesh.polygons:p.use_smooth=(len(p.vertices)==4)
 return obj
r=DIAMETER/2
shaft=lathe('White_Shaft',[(r,0),(r,HEIGHT-CAP_HEIGHT)],white)
# Small rounded edge on a nearly flat cap, not a hemisphere.
profile=[(r,HEIGHT-CAP_HEIGHT),(r,HEIGHT-EDGE_RADIUS)]
for i in range(1,9):
 a=math.pi*.5*i/8;profile.append((r-EDGE_RADIUS+EDGE_RADIUS*math.cos(a),HEIGHT-EDGE_RADIUS+EDGE_RADIUS*math.sin(a)))
cap=lathe('White_Cap_Inferred',profile,white)
# Thin wrap outside body. Its 0.1 mm thickness is a modeling choice only.
band=lathe('Yellow_Band',[(r+.0001,HEIGHT-TOP_TO_BAND-BAND_HEIGHT),(r+.0001,HEIGHT-TOP_TO_BAND)],yellow)
# Export ONLY the product hierarchy. Cameras, lighting, world are not in GLB.
bpy.ops.object.select_all(action='DESELECT')
for o in [root,shaft,cap,band]:o.select_set(True)
bpy.context.view_layer.objects.active=root
bpy.ops.export_scene.gltf(filepath=str(OUT/'shibuya_bollard.glb'),export_format='GLB',use_selection=True,export_cameras=False,export_lights=False,export_extras=True)
# Studio render setup without ground, road or background geometry.
scene.render.engine='CYCLES';scene.cycles.device='CPU';scene.cycles.samples=48;scene.cycles.use_denoising=False
for vl in scene.view_layers:vl.cycles.use_denoising=False
scene.render.film_transparent=True
scene.render.image_settings.file_format='PNG';scene.render.image_settings.color_mode='RGBA'
scene.render.resolution_x=700;scene.render.resolution_y=1100;scene.render.resolution_percentage=100
scene.world.use_nodes=True;scene.world.node_tree.nodes['Background'].inputs[0].default_value=(.7,.75,.8,1);scene.world.node_tree.nodes['Background'].inputs[1].default_value=.45
scene.view_settings.view_transform='Standard';scene.view_settings.look='None';scene.view_settings.exposure=-0.3
def point(obj,target):obj.rotation_euler=(Vector(target)-obj.location).to_track_quat('-Z','Y').to_euler()
for name,loc,energy,size in [('Key',(-2,-3,3),70,3),('Fill',(2,-1,1.5),30,2),('Rim',(1,2,2),44,2)]:
 d=bpy.data.lights.new(name,'AREA');d.energy=energy;d.shape='DISK';d.size=size;o=bpy.data.objects.new(name,d);scene.collection.objects.link(o);o.location=loc;point(o,(0,0,.4))
d=bpy.data.cameras.new('Orthographic_Camera');cam=bpy.data.objects.new('Orthographic_Camera',d);scene.collection.objects.link(cam);d.type='ORTHO';d.ortho_scale=.94;scene.camera=cam
for name,loc in [('front',(0,-3,HEIGHT/2)),('side',(3,0,HEIGHT/2))]:
 cam.location=loc;point(cam,(0,0,HEIGHT/2));scene.render.filepath=str(OUT/(name+'.png'));bpy.ops.render.render(write_still=True)
cam.location=(0,-3,HEIGHT/2);point(cam,(0,0,HEIGHT/2))
bpy.ops.wm.save_as_mainfile(filepath=str(OUT/'shibuya_bollard.blend'),compress=True)
# Independently round-trip GLB in a clean scene; inspect bounds and base-center origin.
bpy.ops.object.select_all(action='SELECT');bpy.ops.object.delete(use_global=False)
bpy.ops.import_scene.gltf(filepath=str(OUT/'shibuya_bollard.glb'))
meshes=[o for o in scene.objects if o.type=='MESH'];points=[o.matrix_world@Vector(v) for o in meshes for v in o.bound_box]
lo=[min(p[i] for p in points) for i in range(3)];hi=[max(p[i] for p in points) for i in range(3)]
roots=[o for o in scene.objects if not o.parent];origin=list(roots[0].matrix_world.translation)
report={'blender':bpy.app.version_string,'status':'PASS','units':'meters','bounds_min':lo,'bounds_max':hi,'dimensions':[hi[i]-lo[i] for i in range(3)],'root_origin':origin,'mesh_count':len(meshes),'camera_count':sum(o.type=='CAMERA' for o in scene.objects),'light_count':sum(o.type=='LIGHT' for o in scene.objects),'note':'Band adds 0.0002 m to shaft diameter. All physical dimensions provisional.'}
assert abs(lo[2])<1e-6 and abs(hi[2]-HEIGHT)<1e-6
assert all(abs(x)<1e-6 for x in origin) and len(meshes)==3
assert report['camera_count']==0 and report['light_count']==0
(OUT/'validation.json').write_text(json.dumps(report,indent=2),encoding='utf-8')
print('VALIDATION_PASS',report)
