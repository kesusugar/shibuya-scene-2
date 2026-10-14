"""Local Blender 4.2.3 verification. Args: output_directory imported_glb"""
import bpy,json,math,sys
from pathlib import Path
from mathutils import Vector
args=sys.argv[sys.argv.index('--')+1:];p=Path(args[0]);imported=Path(args[1]);assert bpy.app.version[:3]==(4,2,3)
bpy.ops.wm.open_mainfile(filepath=str(p/'standing_notice_sign.blend'))
assert bpy.context.scene.unit_settings.scale_length==1
obs=list(bpy.data.collections['ASSET | sign only'].objects);assert len(obs)==64
v=obs[0].data.vertices[0];old=v.co.copy();v.co.x+=.001;obs[0].data.update();assert abs(v.co.x-old.x-.001)<1e-6;v.co=old;obs[0].data.update()
r={'blender':bpy.app.version_string,'blend_reopened':True,'reversible_edit_verified':True,'editable_asset_parts':len(obs),'glbs':[]}
for path in [p/'standing_notice_sign.glb',imported]:
 bpy.ops.wm.read_factory_settings(use_empty=True);bpy.ops.import_scene.gltf(filepath=str(path));meshes=[o for o in bpy.context.scene.objects if o.type=='MESH'];assert len(meshes)==1 and len(bpy.context.scene.objects)==1;ob=meshes[0]
 vs=[ob.matrix_world@v.co for v in ob.data.vertices];lo=[min(v[i] for v in vs) for i in range(3)];hi=[max(v[i] for v in vs) for i in range(3)];dims=[b-a for a,b in zip(lo,hi)]
 assert abs(lo[2])<1e-5 and abs(lo[0]+hi[0])<1e-5 and abs(lo[1]+hi[1])<1e-5,(lo,hi)
 assert all(abs(a-b)<.005 for a,b in zip(dims,[.56,.29,1.10])),dims
 assert all(math.isfinite(x) for v in vs for x in v)
 assert all(abs(v-1)<1e-6 for v in ob.scale)
 ob.data.calc_loop_triangles();tri=len(ob.data.loop_triangles);assert tri==2499 and tri<=4000,tri
 assert len(ob.data.materials)==6,len(ob.data.materials)
 assert not any(n.type=='TEX_IMAGE' for m in ob.data.materials for n in m.node_tree.nodes)
 if path==imported:assert all(m.name.startswith('prop_furniture_') for m in ob.data.materials)
 r['glbs'].append({'file':path.name,'bounds_min_m':lo,'bounds_max_m':hi,'dimensions_m':dims,'triangles':tri,'materials':[m.name for m in ob.data.materials],'single_mesh_only':True,'base_origin_verified':True,'no_image_textures':True})
(p/'validation_qa.json').write_text(json.dumps(r,ensure_ascii=False,indent=2)+'\n');print(json.dumps(r))
