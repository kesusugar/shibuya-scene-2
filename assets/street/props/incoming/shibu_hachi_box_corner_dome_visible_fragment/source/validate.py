"""Blender 4.2.3: -b -P source/validate.py -- OUTPUT_DIR"""
import bpy,sys,json,hashlib,struct,math,bmesh
from pathlib import Path
root=Path(sys.argv[sys.argv.index('--')+1]).resolve()
bpy.ops.wm.open_mainfile(filepath=str(root/'corner_dome_visible_fragment.blend'))
objs=[o for o in bpy.context.scene.objects if o.type=='MESH'];assert len(objs)==4
pts=[o.matrix_world@v.co for o in objs for v in o.data.vertices]
mins=[min(p[i] for p in pts) for i in range(3)];maxs=[max(p[i] for p in pts) for i in range(3)]
assert all(math.isfinite(c) for p in pts for c in p)
assert max(abs(mins[i]+.08) for i in [0,1])<1e-7
assert max(abs(maxs[i]-.08) for i in [0,1])<1e-7
assert abs(mins[2])<1e-7 and abs(maxs[2]-.23)<1e-7
assert all(o.location.length<1e-9 and tuple(o.scale)==(1,1,1) for o in objs)
assert not [o for o in bpy.context.scene.objects if o.type in {'LIGHT','CAMERA'}]
assert not [im for im in bpy.data.images if im.source=='FILE']
assert len({m.name for o in objs for m in o.data.materials})==2
for o in objs:
 bm=bmesh.new();bm.from_mesh(o.data)
 assert all(e.is_manifold for e in bm.edges)
 assert bm.calc_volume(signed=True)>0
 assert all(f.calc_area()>1e-12 for f in bm.faces)
 bm.free()
bpy.ops.object.select_all(action='SELECT')
bpy.ops.export_scene.gltf(filepath=str(root/'editable_check.glb'),export_format='GLB',use_selection=True,export_yup=True,export_extras=False,export_cameras=False,export_lights=False)
original=(root/'corner_dome_visible_fragment.glb').read_bytes();editable=(root/'editable_check.glb').read_bytes();assert original==editable
magic,version,length=struct.unpack_from('<III',original);assert magic==0x46546c67 and version==2 and length==len(original)
jslen,jstype=struct.unpack_from('<II',original,12);assert jstype==0x4e4f534a
j=json.loads(original[20:20+jslen]);assert j['asset']['version']=='2.0';assert not j.get('extensionsRequired');assert not j.get('images');assert not j.get('textures');assert all('uri' not in b for b in j['buffers'])
assert all(p.get('mode',4)==4 for m in j['meshes'] for p in m['primitives'])
assert sum(j['accessors'][p['indices']]['count']//3 for m in j['meshes'] for p in m['primitives'])==896
json.dump({'pass':True,'blender':bpy.app.version_string,'mesh_count':4,'materials':2,'triangles':896,'bbox_min':mins,'bbox_max':maxs,'origin_bottom_centre':True,'closed_positive_volume_meshes':True,'editable_export_byte_exact':True,'glb_2_self_contained_core_pbr':True,'three_js_runtime_test':'not run; core glTF format checks only','glb_sha256':hashlib.sha256(original).hexdigest()},open(root/'validation.json','w'),indent=2)
(root/'editable_check.glb').unlink()
