import bpy,bmesh,json,sys
from pathlib import Path
src,out=sys.argv[sys.argv.index('--')+1:][:2];D=json.load(open(src));bpy.ops.wm.read_factory_settings(use_empty=True);bm=bmesh.new()
for t in D['triangles']:
 ps=[(p[0],p[1],p[2]-15) for p in t]
 bm.faces.new([bm.verts.new(p) for p in ps])
bmesh.ops.remove_doubles(bm,verts=bm.verts[:],dist=.00001);bmesh.ops.recalc_face_normals(bm,faces=bm.faces[:]);me=bpy.data.meshes.new('ground_fill_extension');bm.to_mesh(me);bm.free()
m=bpy.data.materials.new('ground_fill_provisional');m.use_nodes=True;m.node_tree.nodes['Principled BSDF'].inputs['Base Color'].default_value=(.22,.20,.19,1);m.node_tree.nodes['Principled BSDF'].inputs['Roughness'].default_value=.95;me.materials.append(m)
o=bpy.data.objects.new('ground_fill_extension',me);bpy.context.collection.objects.link(o)
bpy.ops.export_scene.gltf(filepath=out,export_format='GLB',export_yup=True)
