"""Render actual corrected baseline and candidate, with matched material and uniform-clay views."""
from pathlib import Path
import bpy,json,sys,hashlib,datetime
from mathutils import Vector
ROOT=Path(__file__).resolve().parents[1];OUT=ROOT/'renders';args=sys.argv[sys.argv.index('--')+1:] if '--' in sys.argv else[]
views={'ne-photo-angle':{'location':[-74,354,10.1],'target':[-126,296,37],'lens':50,'mode':'PERSP'},'north-matched':{'location':[-150,480,48],'target':[-137,301,40],'scale':58,'mode':'ORTHO'},'east-matched':{'location':[20,355,48],'target':[-121,289,40],'scale':51,'mode':'ORTHO'},'depth-eye-level':{'location':[-85,326,29],'target':[-128,296,30.8],'lens':52,'mode':'PERSP'},'roof-context':{'location':[80,480,135],'target':[-150,282,53],'scale':130,'mode':'ORTHO'}}
(OUT/'cameras.json').write_text(json.dumps({'views':views,'notes':'Firstfourcamera transforms match independently reviewed prototype. Roofcontext added. Approximate photographic direction, not calibrated survey. Bothstates rendered using same lighting; clay is a single opaque material on everymesh.'},indent=2)+'\n')
for state,path in [('before',ROOT/'inputs/roof22-corrected-base.glb'),('candidate',ROOT/'parco_terrace_candidate.glb')]:
 if args and state not in args:continue
 mp=OUT/f'render-manifest-{state}.json';rows=json.loads(mp.read_text())['renders']if mp.exists()else[]
 for mode in ['material','clay']:
  if args and any(k in args for k in ['material','clay'])and mode not in args:continue
  inputhash=hashlib.sha256(path.read_bytes()).hexdigest();bpy.ops.wm.read_factory_settings(use_empty=True);bpy.ops.import_scene.gltf(filepath=str(path));s=bpy.context.scene
  if mode=='clay':
   mat=bpy.data.materials.new('Review_uniform_clay');mat.use_nodes=True;bs=mat.node_tree.nodes.get('Principled BSDF');bs.inputs['Base Color'].default_value=(.64,.64,.64,1);bs.inputs['Roughness'].default_value=.7;bs.inputs['Metallic'].default_value=0;bs.inputs['Alpha'].default_value=1
   for o in bpy.context.scene.objects:
    if o.type=='MESH':o.data.materials.clear();o.data.materials.append(mat)
  s.render.engine='CYCLES';s.cycles.samples=32;s.cycles.use_denoising=True;s.render.resolution_x=1200;s.render.resolution_y=1100;s.render.resolution_percentage=100;s.view_settings.view_transform='AgX'
  s.world=bpy.data.worlds.new('Review_sky');s.world.use_nodes=True;s.world.node_tree.nodes['Background'].inputs[0].default_value=(.68,.74,.80,1);s.world.node_tree.nodes['Background'].inputs[1].default_value=.65
  bpy.ops.object.light_add(type='SUN');sun=bpy.context.object;sun.rotation_euler=Vector((-.65,-.55,-1)).to_track_quat('-Z','Y').to_euler();sun.data.angle=.12;sun.data.energy=2.1
  bpy.ops.object.camera_add();cam=bpy.context.object;s.camera=cam
  for name,v in views.items():
   if args and any(k in args for k in views)and name not in args:continue
   cam.location=v['location'];cam.rotation_euler=(Vector(v['target'])-cam.location).to_track_quat('-Z','Y').to_euler();cam.data.type=v['mode'];cam.data.lens=v.get('lens',50);cam.data.ortho_scale=v.get('scale',50)
   file=f'{state}-{mode}-{name}.png';s.render.filepath=str(OUT/file);bpy.ops.render.render(write_still=True)
   assert hashlib.sha256(path.read_bytes()).hexdigest()==inputhash,'Input changed during render'
   row={'file':file,'state':state,'mode':mode,'camera':name,'asset_sha256':inputhash,'image_sha256':hashlib.sha256((OUT/file).read_bytes()).hexdigest(),'rendered_utc':datetime.datetime.now(datetime.timezone.utc).isoformat()};rows=[r for r in rows if r['file']!=file]+[row];mp.write_text(json.dumps({'renders':rows},indent=2)+'\n')
print('RENDER_FINISHED')
