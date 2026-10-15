"""Optional isolated inspection views. Blender 4.2.3, no external assets."""
import bpy,json,struct
from pathlib import Path
from mathutils import Vector
R=Path(__file__).resolve().parent
bpy.ops.wm.open_mainfile(filepath=str(R/'asset/source/blender/takagi.blend'))
s=bpy.context.scene;c=s.camera;E=R/'renders';E.mkdir(exist_ok=True)
A=Vector((-59.952,89.353,0));t=Vector((7.496,17.711,0)).normalized();n=Vector((t.y,-t.x,0));target=A+t*9.616-n*5.8+Vector((0,0,43.8))
views={'after_full':((-2,20,52),(-69,98,25),61),'after_front':((-20,80,30),(-62,98,26),61),'after_side':((-100,30,40),(-65,95,26),61),'after_sign_normal':(tuple(target+n*85),tuple(target),24)}
def strip_text_metadata(path):
 data=path.read_bytes();out=data[:8];pos=8
 while pos<len(data):
  length=struct.unpack_from('>I',data,pos)[0];chunk=data[pos:pos+length+12]
  if chunk[4:8] not in (b'tEXt',b'zTXt',b'iTXt'):out+=chunk
  pos+=length+12
 path.write_bytes(out)
def render(name,view):
 loc,tar,scale=view;c.location=loc;c.rotation_euler=(Vector(tar)-c.location).to_track_quat('-Z','Y').to_euler();c.data.ortho_scale=scale;s.render.filepath=str(E/(name+'.png'));bpy.ops.render.render(write_still=True);strip_text_metadata(E/(name+'.png'))
for name,view in views.items():render(name,view)
for o in list(s.objects):
 if o.type=='MESH':bpy.data.objects.remove(o,do_unlink=True)
bpy.ops.import_scene.gltf(filepath=str(R/'stages/facade/source/data/baseline.glb'))
render('oldest_before_full',views['after_full'])
(E/'camera_lighting.json').write_text(json.dumps({'views':views,'oldest_before_full':'identical to after_full','engine':'CYCLES','samples':24,'resolution':[1000,1000],'world_color':[.65,.65,.65],'view_transform':'Standard','look':'Medium High Contrast','area_light':{'location':[-10,35,95],'energy':170000,'shape':'DISK','size':70},'scope':'Isolated model views; photographic camera not calibrated.'},indent=2))
