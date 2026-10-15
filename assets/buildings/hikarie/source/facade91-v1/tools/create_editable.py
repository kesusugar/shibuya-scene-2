"""Run using Blender 4.2.3 --background --python this_file."""
import bpy,json,hashlib
from pathlib import Path
R=Path(__file__).resolve().parents[1]
assert bpy.app.version[:3]==(4,2,3),bpy.app.version_string
EXPECTED='2f4e95126c0d126c8db2d7d8aad4a54d5d0010ba7af0734b357a939077a87721'
assert hashlib.sha256((R/'web/hikarie.glb').read_bytes()).hexdigest()==EXPECTED

def signature():
 records=[];materials={};vertex_count=0;tri_count=0
 for ob in bpy.context.scene.objects:
  if ob.type!='MESH':continue
  mesh=ob.data;mesh.calc_loop_triangles();vertex_count+=len(mesh.vertices)
  for tr in mesh.loop_triangles:
   tri_count+=1;mat=mesh.materials[tr.material_index].name
   verts=[]
   for vi,li in zip(tr.vertices,tr.loops):
    p=ob.matrix_world@mesh.vertices[vi].co;n=mesh.corner_normals[li].vector;verts.append(tuple(round(float(v),6) for v in (*p,*n)))
   # Cyclic rotation keeps winding while ignoring starting corner.
   verts=min(tuple(verts[i:]+verts[:i]) for i in range(3));records.append((mat,verts))
  for mat in mesh.materials:
   nodes=[n for n in mat.node_tree.nodes if n.type=='BSDF_PRINCIPLED'] if mat.use_nodes else []
   materials[mat.name]={'diffuse':list(mat.diffuse_color),'bsdf':{k:list(nodes[0].inputs[k].default_value) if k=='Base Color' else float(nodes[0].inputs[k].default_value) for k in ['Base Color','Metallic','Roughness','Alpha']} if nodes else None}
 records.sort();return {'triangle_signature_sha256':hashlib.sha256(json.dumps(records,separators=(',',':')).encode()).hexdigest(),'triangles':tri_count,'vertices':vertex_count,'materials':materials,'mesh_count':sum(o.type=='MESH' for o in bpy.context.scene.objects)}

bpy.ops.wm.read_factory_settings(use_empty=True);bpy.ops.import_scene.gltf(filepath=str(R/'web/hikarie.glb'));before=signature();assert before['triangles']==30562
bpy.context.scene['canonical_glb_sha256']=EXPECTED;bpy.context.scene['source91_status']='Validated bounded source91 cleanup. 906 selected generic overlay triangles omitted;204 retained. See docs/REPORT.md.'
t=bpy.data.texts.new('READ_ME');t.write('Editable Blender4.2.3 scene imported from the pinned candidate GLB. Save/reopen parity is checked. Canonical byte-exact GLB build uses tools/regenerate.py and source/overlay_contract.json. Do not overwrite the baseline. Dark vertical bay and occluded lower rows are estimates, not surveyed construction. No image textures.\n')
bpy.ops.file.pack_all();bpy.ops.wm.save_as_mainfile(filepath=str(R/'source/hikarie.blend'),compress=True);bpy.ops.wm.open_mainfile(filepath=str(R/'source/hikarie.blend'));after=signature();assert before==after,(before,after);assert not any(i.source=='FILE' and not i.packed_file for i in bpy.data.images)
receipt={'passed':True,'blender':bpy.app.version_string,'source_glb_sha256':EXPECTED,'blend_sha256':hashlib.sha256((R/'source/hikarie.blend').read_bytes()).hexdigest(),'strict_import_save_reopen_signature_equal':True,'signature_definition':'Sorted material plus oriented triangle world positions and corner normals rounded1e-6; material BSDF values, mesh/vertex/triangle counts exact before/after save.','signature':after,'external_texture_count':0,'canonical_glb_regeneration':'tools/regenerate.py; .blend is editable semantic source, not a promise of byte-identical Blender exporter serialization'}
(R/'evidence/blend-parity.json').write_text(json.dumps(receipt,indent=2));print('BLEND_PARITY_PASSED',receipt['blend_sha256'])
