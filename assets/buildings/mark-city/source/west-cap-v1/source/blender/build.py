"""Portable current source235 stage: Blender 4.2.3 -b -P build.py -- [out.glb].
Append a dark framed10x3 panel and two short glass ribbons; all accepted geometry retained.
All inputs asset-local, no network. Packed editable blend is an exact GLB import.
"""
from pathlib import Path
import importlib.util,sys,json
HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[1]
spec=importlib.util.spec_from_file_location('west_cap',HERE/'build_west_cap.py');m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)
args=sys.argv[sys.argv.index('--')+1:] if '--' in sys.argv else (sys.argv[1:] if 'bpy' not in sys.modules else [])
output=Path(args[0]).resolve() if args else ROOT/'web/mark-city.glb'
if 'bpy' in sys.modules:
 import bpy
 assert bpy.app.version[:3]==(4,2,3),bpy.app.version_string
report=m.build(output);output.with_suffix('.east-stats.json').write_text(json.dumps(report,indent=2)+'\n')
if 'bpy' in sys.modules:
 bpy.ops.wm.read_factory_settings(use_empty=True);bpy.ops.import_scene.gltf(filepath=str(output));sc=bpy.context.scene
 sc['repair_scope']='Append-only source235: one dark framed10x3 panel plus two short glazed ribbons. No true holes or interiors.'
 sc['preservation']='All 25122 accepted triangles, source240/source299 ribbons, EAST185/111, walls, roofs, materials and existing nodes remain exact.'
 sc['prior_stage_sha256']=m.SHA;sc['generated_glb_sha256']=report['sha256'];sc['regeneration']='Adjacent build.py with Blender 4.2.3; only packaged local inputs.'
 sc['photo_source']='Asanagi, Wikimedia Commons, 2025-06-12, CC0 1.0; dimensions/palette/pane count inferred. June is not October-specific proof.'
 bpy.ops.file.pack_all();blend=output.with_suffix('.blend') if args else HERE/'mark-city.blend';bpy.ops.wm.save_as_mainfile(filepath=str(blend))
print(json.dumps({'output':str(output),'sha256':report['sha256'],'triangles':report['triangles'],'primitives':report['primitives'],'bytes':report['bytes']},indent=2))
