import bpy,json,math,sys,hashlib
from pathlib import Path
from mathutils import Vector
root=Path(sys.argv[sys.argv.index('--')+1]).resolve() if '--' in sys.argv else Path.cwd();out=Path(__file__).resolve().parent
bpy.ops.wm.read_factory_settings(use_empty=True)
inputs=json.loads((out/"assembly-input-manifest.json").read_text())["inputs"]
for item in inputs:
 data=(root/item["path"]).read_bytes()
 assert len(data)==item["bytes"] and hashlib.sha256(data).hexdigest()==item["sha256"], item["path"]
bounds={}
for bid in ['west-block','daiichi-kangin','ekimae']:
 base=root/'assets/buildings'/bid/'web';h=json.loads((base/'viewer.json').read_text());objs=[]
 for item in inputs:
  if not item['path'].startswith('assets/buildings/'+bid+'/web/') or not item['path'].endswith('.glb'):continue
  p=root/item['path']
  old=set(bpy.data.objects);bpy.ops.import_scene.gltf(filepath=str(p));new=set(bpy.data.objects)-old
  for ob in new:
   if ob.parent is None:ob.location.z+=h['groundElevationTP']-15
  objs+=list(new)
 bpy.context.view_layer.update()
 pts=[o.matrix_world@Vector(v) for o in objs if o.type=='MESH' for v in o.bound_box]
 bounds[bid]={'min':[min(v[i] for v in pts) for i in range(3)],'max':[max(v[i] for v in pts) for i in range(3)],'groundElevationTP':h['groundElevationTP']}
for m in bpy.data.materials:
 if m.use_nodes:
  p=m.node_tree.nodes.get('Principled BSDF')
  if p:p.inputs['Emission Strength'].default_value=0
(out/'assembly-bounds.json').write_text(json.dumps(bounds,indent=2))
s=bpy.context.scene;s.render.engine='CYCLES';s.cycles.samples=24;s.cycles.use_denoising=True;s.world=bpy.data.worlds.new('World');s.world.color=(.6,.6,.6);s.render.resolution_x=1400;s.render.resolution_y=1000;s.render.resolution_percentage=100;s.view_settings.view_transform='AgX';s.render.image_settings.file_format='PNG'
bpy.ops.object.light_add(type='SUN',location=(-90,-100,130));l=bpy.context.object;l.rotation_euler=(Vector((-50,0,0))-l.location).to_track_quat('-Z','Y').to_euler();l.data.energy=2
bpy.ops.object.camera_add();cam=bpy.context.object;s.camera=cam;cam.data.type='ORTHO';cam.data.ortho_scale=130
for name,pos,aim in [('assembly-east',(120,-100,95),(-60,5,20)),('assembly-plan',(-60,0,210),(-60,0,0))]:
 cam.data.ortho_scale=175 if name=='assembly-plan' else 130;cam.location=pos;cam.rotation_euler=(Vector(aim)-cam.location).to_track_quat('-Z','Y').to_euler();s.render.filepath=str(out/(name+'.png'));bpy.ops.render.render(write_still=True)
