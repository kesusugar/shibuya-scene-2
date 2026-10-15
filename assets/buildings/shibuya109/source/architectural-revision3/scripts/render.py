import bpy,sys,json,math,os,hashlib
from pathlib import Path
from mathutils import Vector
ROOT=Path(__file__).resolve().parents[1];MODE=sys.argv[-1] if sys.argv[-1]in ['entrance','combined','before'] else'entrance';OUT=ROOT/'evidence'/os.environ.get('RENDER_SET',MODE);OUT.mkdir(exist_ok=True,parents=True)
P=ROOT/'inputs/prior.glb' if MODE=='before' else ROOT/'output'/MODE/'shibuya109.glb'
bpy.ops.wm.read_factory_settings(use_empty=True);bpy.ops.import_scene.gltf(filepath=str(P))
s=bpy.context.scene;s.render.engine='CYCLES';s.cycles.samples=int(os.environ.get('SAMPLES','24'));s.cycles.use_denoising=True;s.render.resolution_x=1400;s.render.resolution_y=1100;s.render.resolution_percentage=100;s.render.image_settings.file_format='PNG';s.view_settings.view_transform='AgX';s.view_settings.look='AgX - Medium High Contrast';s.view_settings.exposure=-1.5
w=bpy.data.worlds.new('Daylight environment');s.world=w;w.use_nodes=True;n=w.node_tree.nodes;n.clear();sky=n.new('ShaderNodeTexSky');sky.sky_type='NISHITA';sky.sun_elevation=math.radians(38);sky.sun_rotation=math.radians(120);sky.altitude=.05;sky.air_density=1.2;bg=n.new('ShaderNodeBackground');bg.inputs['Strength'].default_value=.45;o=n.new('ShaderNodeOutputWorld');w.node_tree.links.new(sky.outputs['Color'],bg.inputs['Color']);w.node_tree.links.new(bg.outputs['Background'],o.inputs['Surface'])
# Studio ground is excluded from asset and explicitly not claimed as source scene contact.
bpy.ops.mesh.primitive_plane_add(size=180,location=(-148,8,1.2));floor=bpy.context.object;floor.name='RenderOnly_ProvisionalSlopedStage_NotSourcePavement';floor.location=(-129.0380165,6.9354801,1.5053656);floor.rotation_euler=(math.atan(-.049117),math.atan(.025095),-.050724);m=bpy.data.materials.new('RenderOnly ground');m.diffuse_color=(.22,.22,.21,1);floor.data.materials.append(m)
bpy.ops.object.camera_add();cam=bpy.context.object;s.camera=cam;cam.data.lens=46
views={'entry-front':((-107,5.8,5.6),(-128,7,4.7)),'entry-side':((-110,-9,6.6),(-127.5,7,4.9)),'entry-stair':((-111,24,9),(-129,9,4.9)),'entry-under':((-119.5,3,3.1),(-128,7,6.0))}
if MODE in ['combined','before']:views.update({'overall':((-72,-70,69),(-153,8,25)),'front':((-35,7,26),(-153,7,26)),'left':((-151,-110,27),(-151,8,27)),'right':((-151,125,27),(-151,8,27)),'rear':((-260,8,28),(-153,8,28)),'wing-up':((-133,-15,6),(-140,-2,22)),'stair-landing':((-128.0,15.8,7.2),(-134.1,13.5,6.5))})
if os.environ.get('VIEWS'):views={k:views[k] for k in os.environ['VIEWS'].split(',')}
for name,(loc,tgt) in views.items():
 if os.environ.get('VIEWS') and name not in os.environ['VIEWS'].split(','):continue
 if name.startswith('entry') or name=='stair-landing':
  floor.location=(-129.0380165,6.9354801,1.5053656);floor.rotation_euler=(math.atan(-.049117),math.atan(.025095),-.050724)
 else:
  floor.location=(-148,8,1.17);floor.rotation_euler=(0,0,0)
 cam.data.type='PERSP';cam.location=loc;target=Vector(tgt);cam.rotation_euler=(target-cam.location).to_track_quat('-Z','Y').to_euler();cam.data.lens=46 if name.startswith('entry') else (42 if name=='overall' else 52);s.render.filepath=str(OUT/(name+'.png'));bpy.ops.render.render(write_still=True)
(OUT/'camera-config.json').write_text(json.dumps({'views':views,'model_sha256':hashlib.sha256(P.read_bytes()).hexdigest(),'render_stage':'Entry views: simple staging plane fitted to existing-fill fourpoint heights; wholebuilding: neutral flat1.17datum. Renderstage is not surveyed pavement; actual footcontact verified independently against unchanged extension mesh','lighting':'Nishita sun38deg rotation120deg strength0.45; exposure-1.5; AgX MediumHighContrast'},indent=2))
