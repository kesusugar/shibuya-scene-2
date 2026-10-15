"""Export the loaded editable blend as five material batches without changing saved source."""
import bpy,sys
s=bpy.context.scene
originals=[o for o in s.objects if o.type=='MESH']
materials=sorted({o.data.materials[0] for o in originals},key=lambda x:x.name)
exports=[]
for m in materials:
 bpy.ops.object.select_all(action='DESELECT');copies=[]
 for original in originals:
  if original.data.materials[0]==m:
   o=original.copy();o.data=original.data.copy();s.collection.objects.link(o);o.select_set(True);copies.append(o)
 bpy.context.view_layer.objects.active=copies[0];bpy.ops.object.join();o=bpy.context.object;o.name='Batch_'+m.name;o.data.name=o.name+'_mesh';exports.append(o)
bpy.ops.object.select_all(action='DESELECT')
for o in exports:o.select_set(True)
bpy.ops.export_scene.gltf(filepath=sys.argv[sys.argv.index('--')+1],export_format='GLB',use_selection=True,export_yup=True,export_extras=False,export_cameras=False,export_lights=False,export_materials='EXPORT')
