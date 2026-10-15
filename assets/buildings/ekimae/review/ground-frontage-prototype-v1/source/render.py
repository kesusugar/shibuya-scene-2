import bpy,json,sys,math
from mathutils import Vector
from pathlib import Path
R=Path(__file__).resolve().parents[1];assert bpy.app.version==(4,2,3)
B=Vector((-46.78,-10.647,0));T=Vector((.9991711854627296,-.04070555417880273,0));N=Vector((.04070555417880273,.9991711854627296,0))
def p(u,d,h):return B-T*u+N*d+Vector((0,0,h))
cameras={'front':{'aim':[1,.05,1.65],'eye':[1,15,1.65],'scale':7.8},'oblique-east':{'aim':[.9,-.05,1.65],'eye':[-6,11,3.6],'scale':8.5},'oblique-west':{'aim':[.6,-.05,1.6],'eye':[7,11,3.8],'scale':8.5},'soffit-upward':{'aim':[.9,0,2.7],'eye':[-2,6,.6],'scale':7.4},'plan-section':{'aim':[.75,0,0],'eye':[.75,0,20],'scale':7.4}}
(R/'evidence/render-cameras.json').write_text(json.dumps(cameras,indent=2))
for stage in (['prototype'] if '--diagnostic-only' in sys.argv or '--prototype-only' in sys.argv else ['before','prototype']):
 bpy.ops.wm.read_factory_settings(use_empty=True);bpy.ops.import_scene.gltf(filepath=str(R/('input/ekimae.glb' if stage=='before' else 'web/ekimae.glb')))
 asset=list(bpy.context.scene.objects)
 s=bpy.context.scene;s.render.engine='CYCLES';s.cycles.samples=32;s.cycles.use_denoising=True;s.render.resolution_x=1200;s.render.resolution_y=800;s.render.resolution_percentage=100
 s.world=bpy.data.worlds.new('World');s.world.color=(.7,.7,.7);s.view_settings.view_transform='AgX'
 bpy.ops.object.light_add(type='SUN',location=p(-5,10,20));sun=bpy.context.object;sun.data.energy=2;sun.rotation_euler=(.35,-.5,-.2)
 bpy.ops.object.light_add(type='AREA',location=p(0,5,6));light=bpy.context.object;light.data.energy=900;light.data.shape='DISK';light.data.size=7;light.rotation_euler=(p(1,0,1)-light.location).to_track_quat('-Z','Y').to_euler()
 for name,c in cameras.items():
  if '--diagnostic-only' in sys.argv and name not in ['soffit-upward','plan-section']:continue
  # Only the section diagnostic uses a temporary render-only cutoff at h1.5.
  backups=[]
  if name=='plan-section':
   for ob in asset:
    if ob.type!='MESH':continue
    old=ob.data;new=old.copy();ob.data=new;backups.append((ob,old,new))
    import bmesh
    bm=bmesh.new();bm.from_mesh(new);bmesh.ops.bisect_plane(bm,geom=list(bm.verts)+list(bm.edges)+list(bm.faces),dist=1e-6,plane_co=(0,0,1.5),plane_no=(0,0,1),clear_outer=True,clear_inner=False);bm.to_mesh(new);bm.free()
  bpy.ops.object.camera_add(location=p(*c['eye']));cam=bpy.context.object;cam.rotation_euler=(p(*c['aim'])-cam.location).to_track_quat('-Z','Y').to_euler();cam.data.type='ORTHO';cam.data.ortho_scale=c['scale'];s.camera=cam;s.render.filepath=str(R/'evidence'/f'{stage}-{name}.png');bpy.ops.render.render(write_still=True);bpy.data.objects.remove(cam,do_unlink=True)
  for ob,old,new in backups:ob.data=old;bpy.data.meshes.remove(new)
