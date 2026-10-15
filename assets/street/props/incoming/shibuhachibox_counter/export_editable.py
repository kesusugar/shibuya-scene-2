"""Blender 4.2.3: open editable source and produce the same 2-batch GLB."""
import bpy,os,sys,runpy
D=os.path.dirname(os.path.abspath(__file__));args=sys.argv[sys.argv.index('--')+1:] if '--' in sys.argv else []
out=os.path.abspath(args[0]) if args else os.path.join(D,'counter_editable_export.glb')
bpy.ops.wm.open_mainfile(filepath=os.path.join(D,'shibuhachibox_counter.blend'));bpy.ops.object.select_all(action='DESELECT')
for o in bpy.context.scene.objects:
 if o.type in ('MESH','EMPTY'):o.select_set(True)
bpy.ops.export_scene.gltf(filepath=out,export_format='GLB',use_selection=True,export_yup=True,export_apply=True)
runpy.run_path(os.path.join(D,'batch_export.py'))['batch_glb'](out)
