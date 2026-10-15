import bpy,json,hashlib
from pathlib import Path
A=Path(__file__).resolve().parents[2]
def signature():
 records=[];mats={};nv=0
 for ob in bpy.context.scene.objects:
  if ob.type!='MESH':continue
  mesh=ob.data;mesh.calc_loop_triangles();nv+=len(mesh.vertices)
  for tr in mesh.loop_triangles:
   vs=[]
   for vi,li in zip(tr.vertices,tr.loops):
    p=ob.matrix_world@mesh.vertices[vi].co;n=mesh.corner_normals[li].vector;vs.append(tuple(round(float(x),6) for x in (*p,*n)))
   records.append((mesh.materials[tr.material_index].name,min(tuple(vs[i:]+vs[:i]) for i in range(3))))
  for m in mesh.materials:
   ns=[n for n in m.node_tree.nodes if n.type=='BSDF_PRINCIPLED'] if m.use_nodes else []
   mats[m.name]={'diffuse':list(m.diffuse_color),'bsdf':{k:list(ns[0].inputs[k].default_value) if k=='Base Color' else float(ns[0].inputs[k].default_value) for k in ['Base Color','Metallic','Roughness','Alpha']} if ns else None}
 return {'hash':hashlib.sha256(json.dumps(sorted(records),separators=(',',':')).encode()).hexdigest(),'triangles':len(records),'vertices':nv,'materials':mats,'meshes':sum(o.type=='MESH' for o in bpy.context.scene.objects)}
bpy.ops.wm.read_factory_settings(use_empty=True);bpy.ops.import_scene.gltf(filepath=str(A/'web/fukuras.glb'));glb=signature();bpy.ops.wm.open_mainfile(filepath=str(A/'source/blender/fukuras.blend'));blend=signature();assert glb==blend,(glb,blend)
assert len(bpy.data.libraries)==0;assert not any(i.source=='FILE' for i in bpy.data.images)
r={'passed':True,'blender':bpy.app.version_string,'source_glb_sha256':hashlib.sha256((A/'web/fukuras.glb').read_bytes()).hexdigest(),'chosen_delivery_blend_sha256':hashlib.sha256((A/'source/blender/fukuras.blend').read_bytes()).hexdigest(),'signature':blend,'signature_definition':'Oriented world triangle positions and corner normals rounded 1e-6, material BSDF values, mesh/vertex/triangle counts. Exact chosen delivered blend reopened versus final GLB import.','external_images':0,'linked_libraries':0}
(A/'evidence/tessellation-v4/editable-parity.json').write_text(json.dumps(r,indent=2)+'\n');print('PASS editable parity')
