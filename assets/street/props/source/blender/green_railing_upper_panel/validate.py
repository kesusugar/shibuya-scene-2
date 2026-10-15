"""Focused unplaced upper-panel validation. Blender 4.2.3; no runtime checks."""
import bpy,json,hashlib,math,struct,tempfile
from pathlib import Path
from mathutils import Vector
p=Path(__file__).resolve().parent
assert bpy.app.version[:3]==(4,2,3)
data=(p/'green_railing_upper_panel.glb').read_bytes()
assert hashlib.sha256(data).hexdigest()=='b473c5d52294448bb8d9a74b8b183205e1c098d36f76d674dc02c6447f0328fc'
magic,version,total=struct.unpack_from('<III',data);assert magic==0x46546c67 and version==2 and total==len(data)
n,kind=struct.unpack_from('<II',data,12);assert kind==0x4e4f534a
j=json.loads(data[20:20+n]);assert not j.get('images') and not j.get('textures') and not j.get('animations') and not j.get('cameras')
assert all('uri' not in b for b in j['buffers'])
bpy.ops.wm.read_factory_settings(use_empty=True)
bpy.ops.import_scene.gltf(filepath=str(p/'green_railing_upper_panel.glb'))
obs=[o for o in bpy.context.scene.objects if o.type=='MESH'];assert len(obs)==1
ob=obs[0];vs=[ob.matrix_world@v.co for v in ob.data.vertices]
assert all(math.isfinite(x) for v in vs for x in v)
lo=[min(v[i] for v in vs) for i in range(3)];hi=[max(v[i] for v in vs) for i in range(3)]
assert abs(lo[2])<1e-6 and abs(lo[0]+hi[0])<1e-6 and abs(lo[1]+hi[1])<1e-6
for a,b in zip([hi[i]-lo[i] for i in range(3)],[2,.044,.49004223942756653]):assert abs(a-b)<1e-6
assert len(ob.data.polygons)==3448 and all(poly.area>1e-10 for poly in ob.data.polygons)
assert all(m.name.startswith('prop_furniture_') for m in ob.data.materials)
assert not bpy.data.images and not any(o.type in ('CAMERA','LIGHT') for o in bpy.context.scene.objects)
report={'status':'PASS','blender':'4.2.3','sha256':hashlib.sha256(data).hexdigest(),'triangles':3448,'bytes':len(data),'bounds_z_up_m':[lo,hi],'mesh_nodes':1,'materials':[m.name for m in ob.data.materials],'external_resources':0,'scope':'upper fragment only; no placement, full-scene or FPS claim'}
bpy.ops.wm.open_mainfile(filepath=str(p/'green_railing_upper_panel.blend'))
assert bpy.context.scene.unit_settings.system=='METRIC' and bpy.context.scene.unit_settings.scale_length==1
assert not bpy.data.libraries and not [i for i in bpy.data.images if i.source=='FILE']
assert bpy.context.scene.render.filepath=='//photo_like.png'
asset=bpy.data.collections['ASSET'];assert len(asset.objects)==3
bpy.ops.object.select_all(action='DESELECT')
copies=[]
for o in list(asset.objects):
 n=o.copy();n.data=o.data.copy();asset.objects.link(n);copies.append(n);n.select_set(True)
bpy.context.view_layer.objects.active=copies[0];bpy.ops.object.join();exp=bpy.context.object;exp.name='green_railing_upper_panel'
mod=exp.modifiers.new('triangulated_export','TRIANGULATE');bpy.ops.object.modifier_apply(modifier=mod.name)
with tempfile.TemporaryDirectory() as d:
 out=Path(d)/'editable.glb'
 bpy.ops.export_scene.gltf(filepath=str(out),export_format='GLB',use_selection=True,export_yup=True,export_cameras=False,export_lights=False,export_animations=False)
 assert out.read_bytes()==data
report['editable_source_objects']=3;report['editable_export_byte_identical']=True
(p/'validation.json').write_text(json.dumps(report,indent=2)+'\n')
print(json.dumps(report))
