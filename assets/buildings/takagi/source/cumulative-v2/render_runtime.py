"""Same-camera isolated actual main/default/January comparison, Blender 4.2.3."""
import bpy,json,struct
from pathlib import Path
from mathutils import Vector
R=Path(__file__).resolve().parent;A=R.parents[1];E=R/'review';assert bpy.app.version[:3]==(4,2,3)
bpy.ops.wm.open_mainfile(filepath=str(R/'asset/source/blender/takagi.blend'))
s=bpy.context.scene;c=s.camera;c.location=(-2,20,52);c.rotation_euler=(Vector((-69,98,25))-c.location).to_track_quat('-Z','Y').to_euler();c.data.ortho_scale=61
for name,files in [('main',[E/'main-b678e936.glb']),('default',[A/'web/takagi.glb']),('january',[A/'web/takagi.glb',A/'web/signs-2025-01.glb'])]:
 for o in list(s.objects):
  if o.type=='MESH':bpy.data.objects.remove(o,do_unlink=True)
 for p in files:bpy.ops.import_scene.gltf(filepath=str(p))
 if name=='default':bpy.ops.wm.save_as_mainfile(filepath=str(A/'source/blender/takagi.blend'))
 s.render.filepath=str(E/(name+'.png'));bpy.ops.render.render(write_still=True)
 p=E/(name+'.png');b=p.read_bytes();out=b[:8];i=8
 while i<len(b):
  n=struct.unpack_from('>I',b,i)[0];chunk=b[i:i+n+12]
  if chunk[4:8] not in (b'tEXt',b'zTXt',b'iTXt'):out+=chunk
  i+=n+12
 p.write_bytes(out)
(E/'camera.json').write_text(json.dumps({'location':[-2,20,52],'target':[-69,98,25],'ortho_scale':61,'resolution':[1000,1000],'samples':24,'main':'b678e9364a2cb6fd8dd2869b3b5ee195c86bbe39 actual web/takagi.glb','default':'web/takagi.glb only; old 24-triangle generic billboard removed','january':'default plus optional unregistered signs-2025-01.glb','scope':'isolated model, not browser/full-scene/FPS; camera and lighting fixed'},indent=2)+'\n')
