"""Blender 4.2.3 strict standalone release check; no scene placement."""
import bpy, sys, json, hashlib, struct, math
from pathlib import Path
assert bpy.app.version[:3] == (4,2,3)
glb,blend,spec,out=map(Path,sys.argv[sys.argv.index('--')+1:])
data=glb.read_bytes(); magic,version,length=struct.unpack_from('<III',data)
assert magic==0x46546c67 and version==2 and length==len(data)
n,kind=struct.unpack_from('<II',data,12); assert kind==0x4e4f534a
j=json.loads(data[20:20+n]); assert not j.get('images') and not j.get('animations') and not j.get('cameras')
assert all('uri' not in x for x in j['buffers'])
assert len(j['meshes'])==1 and len(j['materials'])==3
assert all(p.get('mode',4)==4 for p in j['meshes'][0]['primitives'])
assert not j.get('extensionsRequired')
s=json.loads(spec.read_text()); assert s['lod_ratio']==0
bpy.ops.wm.read_factory_settings(use_empty=True); bpy.ops.import_scene.gltf(filepath=str(glb))
obs=list(bpy.context.scene.objects); assert len(obs)==1 and obs[0].type=='MESH'
o=obs[0]; assert o.name==s['id']; vs=[o.matrix_world@v.co for v in o.data.vertices]
lo=[min(v[i] for v in vs) for i in range(3)]; hi=[max(v[i] for v in vs) for i in range(3)]
assert all(math.isfinite(x) for v in vs for x in v)
assert all(abs(hi[i]-lo[i]-x)<1e-6 for i,x in enumerate([.38,.38,.70]))
assert abs(lo[2])<1e-6 and abs(lo[0]+hi[0])<1e-6 and abs(lo[1]+hi[1])<1e-6
assert all(abs(v)<1e-6 for v in o.location)
o.data.calc_loop_triangles(); assert len(o.data.loop_triangles)==1044 <= s['max_triangles']
assert all(p.area>1e-10 for p in o.data.polygons)
assert all(m.name.startswith('prop_furniture_') for m in o.data.materials)
assert all(m.node_tree.nodes.get('Principled BSDF').inputs['Emission Strength'].default_value==0 for m in o.data.materials)
glb_coords={tuple(round(x,5) for x in v) for v in vs}
bpy.ops.wm.open_mainfile(filepath=str(blend)); c=bpy.data.collections['ASSET']; assert len(c.objects)==3
assert not [i for i in bpy.data.images if i.source=="FILE"] and not bpy.data.libraries
assert bpy.context.scene.unit_settings.system=='METRIC' and bpy.context.scene.unit_settings.scale_length==1
assert bpy.context.scene.render.filepath.startswith('//')
# Re-export editable components with the same joining and triangulation recipe.
bpy.ops.object.select_all(action='DESELECT')
for ob in list(c.objects):
 n=ob.copy(); n.data=ob.data.copy(); c.objects.link(n);n.select_set(True)
bpy.context.view_layer.objects.active=bpy.context.selected_objects[0]; bpy.ops.object.join(); ob=bpy.context.object; ob.name=s['id']
m=ob.modifiers.new('triangulated_export','TRIANGULATE');bpy.ops.object.modifier_apply(modifier=m.name)
# Names can receive Blender suffixes when original mesh datablocks survive; compare geometry, not output bytes.
ob.data.calc_loop_triangles(); assert len(ob.data.loop_triangles)==1044
assert {tuple(round(x,5) for x in ob.matrix_world@v.co) for v in ob.data.vertices}==glb_coords
out.write_text(json.dumps({'status':'PASS','blender':bpy.app.version_string,'glb_sha256':hashlib.sha256(data).hexdigest(),'bytes':len(data),'triangles':1044,'materials':3,'mesh_nodes':1,'bounds_z_up':[lo,hi],'strict_dimensions_m':[.38,.38,.70],'bottom_center_origin':True,'embedded_dependencies':0,'editable_parts':3,'editable_triangle_closure':True,'placement':'none','scene_fps_tested':False},indent=2)+'\n')
