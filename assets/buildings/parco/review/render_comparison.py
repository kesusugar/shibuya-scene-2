from pathlib import Path
import bpy,json,hashlib
from mathutils import Vector
R=Path(__file__).resolve().parents[1];O=R/'review/generated';O.mkdir(parents=True,exist_ok=True)
views={'north-east':{'location':[-74,354,10.1],'target':[-126,296,37],'lens':50},'whole':{'location':[80,480,135],'target':[-150,282,53],'scale':130}}
rows=[]
for state,path in [('main',R/'source/inputs/baseline.glb'),('final',R/'web/parco.glb')]:
 for name,v in views.items():
  bpy.ops.wm.read_factory_settings(use_empty=True);bpy.ops.import_scene.gltf(filepath=str(path));s=bpy.context.scene
  s.render.engine='CYCLES';s.cycles.samples=32;s.cycles.use_denoising=True;s.render.resolution_x=1200;s.render.resolution_y=1100;s.render.resolution_percentage=100;s.view_settings.view_transform='AgX'
  s.world=bpy.data.worlds.new('Review_sky');s.world.use_nodes=True;s.world.node_tree.nodes['Background'].inputs[0].default_value=(.68,.74,.80,1);s.world.node_tree.nodes['Background'].inputs[1].default_value=.8
  bpy.ops.object.light_add(type='SUN');sun=bpy.context.object;sun.rotation_euler=Vector((-.65,-.55,-1)).to_track_quat('-Z','Y').to_euler();sun.data.energy=2.1;sun.data.angle=.12
  bpy.ops.object.camera_add();cam=bpy.context.object;s.camera=cam;cam.location=v['location'];cam.rotation_euler=(Vector(v['target'])-cam.location).to_track_quat('-Z','Y').to_euler();cam.data.type='ORTHO' if 'scale' in v else 'PERSP';cam.data.ortho_scale=v.get('scale',50);cam.data.lens=v.get('lens',50)
  s.render.image_settings.file_format='JPEG';s.render.image_settings.quality=93;f=O/f'{state}-{name}.jpg';s.render.filepath=str(f);bpy.ops.render.render(write_still=True)
  rows.append({'state':state,'file':f.name,'asset_sha256':hashlib.sha256(path.read_bytes()).hexdigest(),'camera':v,'native_materials':True,'blender':'4.2.3','same_lighting':True})
(O/'render-manifest.json').write_text(json.dumps(rows,indent=2)+'\n')
