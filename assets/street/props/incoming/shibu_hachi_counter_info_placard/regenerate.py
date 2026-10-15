import bpy, math, json, sys
from pathlib import Path
from mathutils import Vector
P=Path(__file__).resolve().parent
args=sys.argv[sys.argv.index('--')+1:] if '--' in sys.argv else []
O=Path(args[0]).resolve() if args else P
O.mkdir(parents=True,exist_ok=True);(O/'renders').mkdir(exist_ok=True)
bpy.ops.object.select_all(action='SELECT');bpy.ops.object.delete(use_global=False)
s=bpy.context.scene;s.unit_settings.system='METRIC';s.unit_settings.scale_length=1
# Front faces toward -Y. Dimensions are inferred, not surveyed.
def mat(name,color):
 m=bpy.data.materials.new(name);m.diffuse_color=(*color,1);m.use_nodes=True
 bs=m.node_tree.nodes.get('Principled BSDF');bs.inputs['Base Color'].default_value=(*color,1);bs.inputs['Roughness'].default_value=.7
 return m
edge=mat('Warm white thin sign edge',(.78,.78,.74))
bpy.ops.mesh.primitive_cube_add(size=1,location=(0,.00005,.225));board=bpy.context.object;board.name='Information placard thin backing';board.dimensions=(.34,.003,.45);bpy.ops.object.transform_apply(location=False,rotation=False,scale=True);board.data.materials.append(edge)
# Flat own-authored image, no source-photo pixels.
mesh=bpy.data.meshes.new('Front quad');mesh.from_pydata([(-.17,-.00155,0),(.17,-.00155,0),(.17,-.00155,.45),(-.17,-.00155,.45)],[],[(0,1,2,3)]);mesh.update()
front=bpy.data.objects.new('Tourist Information face',mesh);bpy.context.collection.objects.link(front)
uv=mesh.uv_layers.new(name='UVMap')
for i,p in enumerate([(0,0),(1,0),(1,1),(0,1)]):uv.data[i].uv=p
m=mat('Own authored information artwork',(.8,.8,.8));n=m.node_tree.nodes.new('ShaderNodeTexImage');im=bpy.data.images.load(str(P/'placard_albedo.png'));im.pack();n.image=im;m.node_tree.links.new(n.outputs['Color'],m.node_tree.nodes.get('Principled BSDF').inputs['Base Color']);front.data.materials.append(m)
bpy.ops.object.select_all(action='DESELECT');board.select_set(True);front.select_set(True);bpy.context.view_layer.objects.active=board;bpy.ops.object.join();board.name='shibu_hachi_counter_info_placard';s.cursor.location=(0,0,0);bpy.ops.object.origin_set(type='ORIGIN_CURSOR')
board['reference_date']='2024; present-day persistence unverified';board['dimensions_status']='estimated .34 x .0031 x .45 m';board['placement_status']='unplaced; front attachment only'
bpy.ops.export_scene.gltf(filepath=str(O/'shibu_hachi_counter_info_placard.glb'),export_format='GLB',use_selection=True,export_yup=True,export_extras=True)
s.render.engine='CYCLES';s.cycles.samples=16;s.render.resolution_x=700;s.render.resolution_y=700;s.render.resolution_percentage=100
s.world.color=(.35,.35,.35);s.view_settings.view_transform='Standard';s.render.image_settings.file_format='PNG';s.render.film_transparent=True
bpy.ops.object.light_add(type='AREA',location=(-1,-2,2));bpy.context.object.data.energy=130;bpy.context.object.data.shape='DISK';bpy.context.object.data.size=3
bpy.context.object.rotation_euler=(Vector((0,0,.225))-bpy.context.object.location).to_track_quat('-Z','Y').to_euler()
bpy.ops.object.camera_add();cam=bpy.context.object;s.camera=cam;cam.data.type='ORTHO';cam.data.ortho_scale=.62
for name,loc in [('front',(0,-2,.225)),('side',(2,0,.225)),('oblique',(.75,-1.7,.6))]:
 cam.location=loc;cam.rotation_euler=(Vector((0,0,.225))-cam.location).to_track_quat('-Z','Y').to_euler();s.render.filepath=str(O/'renders'/f'{name}.png');bpy.ops.render.render(write_still=True)
bpy.ops.wm.save_as_mainfile(filepath=str(O/'shibu_hachi_counter_info_placard.blend'))
json.dump({'blender':bpy.app.version_string,'triangles':14,'materials':2,'dimensions_m':list(board.dimensions),'origin':list(board.location),'image_source':'own typeset artwork, not a photograph','runtime_placement':False},open(O/'validation.json','w'),indent=2)
