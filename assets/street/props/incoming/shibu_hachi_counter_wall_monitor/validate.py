"""Read-only final model audit, run with Blender 4.2.3.
blender -b -t 2 --python validate.py -- /path/to/v001
Writes validation.json; does not alter models or regenerate them.
"""
import bpy, json, math, struct, sys, hashlib, time
from pathlib import Path
from datetime import datetime, timezone
from mathutils import Vector

P = Path(sys.argv[sys.argv.index('--')+1]).resolve() if '--' in sys.argv else Path(__file__).resolve().parent
NAME = 'shibu_hachi_counter_wall_monitor'
start = time.perf_counter()
utc = lambda: datetime.now(timezone.utc).isoformat()
report = {'started_utc':utc(), 'audit_scope':'One frozen isolated GLB and editable blend; no regeneration or scene integration', 'tests':{}}
tests = report['tests']
b = (P/(NAME+'.glb')).read_bytes()
magic, version, size = struct.unpack_from('<III',b)
n, kind = struct.unpack_from('<II',b,12)
doc = json.loads(b[20:20+n])
tests['valid_glb_header'] = magic == 0x46546C67 and version == 2 and size == len(b) and kind == 0x4E4F534A
tests['two_meshes_two_primitives'] = len(doc.get('meshes',[])) == 2 and sum(len(m['primitives']) for m in doc['meshes']) == 2
tests['two_standard_pbr_materials'] = len(doc.get('materials',[])) == 2 and all('pbrMetallicRoughness' in m for m in doc['materials'])
tests['no_external_resources'] = all('uri' not in x for x in doc.get('buffers',[])) and not doc.get('images')
tests['no_lights_or_cameras'] = not doc.get('cameras') and 'KHR_lights_punctual' not in doc.get('extensionsUsed',[])
tests['non_emissive_opaque_materials'] = all(m.get('emissiveFactor',[0,0,0]) == [0,0,0] and m.get('alphaMode','OPAQUE') == 'OPAQUE' for m in doc['materials'])
report['glb'] = {'sha256':hashlib.sha256(b).hexdigest(),'bytes':len(b),'meshes':len(doc['meshes']), 'materials':[m['name'] for m in doc['materials']], 'extensions_used':doc.get('extensionsUsed',[])}

bpy.ops.wm.open_mainfile(filepath=str(P/(NAME+'.blend')))
original = [o for o in bpy.context.scene.objects if o.type=='MESH']
roots = [o for o in bpy.context.scene.objects if o.type=='EMPTY']
tests['three_editable_components'] = len(original) == 3
tests['bottom_center_root'] = len(roots)==1 and roots[0].location.length<1e-8 and roots[0].rotation_euler.to_matrix() == roots[0].rotation_euler.to_matrix().Identity(3)
tests['editable_resources_self_contained'] = not bpy.data.libraries and all(im.packed_file or im.source in {'GENERATED','VIEWER'} for im in bpy.data.images)
tests['metric_authoring_units'] = bpy.context.scene.unit_settings.system == 'METRIC' and bpy.context.scene.unit_settings.scale_length == 1.0
report['blend'] = {'sha256':hashlib.sha256((P/(NAME+'.blend')).read_bytes()).hexdigest(),'editable_mesh_names':[o.name for o in original], 'root_names':[o.name for o in roots], 'external_libraries':len(bpy.data.libraries), 'images':len(bpy.data.images)}

bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete(use_global=False)
bpy.ops.import_scene.gltf(filepath=str(P/(NAME+'.glb')))
meshes = [o for o in bpy.context.scene.objects if o.type=='MESH']
verts = [o.matrix_world@v.co for o in meshes for v in o.data.vertices]
low = [min(v[i] for v in verts) for i in range(3)]
high = [max(v[i] for v in verts) for i in range(3)]
dimensions = [high[i]-low[i] for i in range(3)]
triangles = 0
degenerate = 0
for o in meshes:
    o.data.calc_loop_triangles()
    for t in o.data.loop_triangles:
        triangles += 1
        a,c,d = [o.matrix_world@o.data.vertices[i].co for i in t.vertices]
        if (c-a).cross(d-a).length < 1e-14:
            degenerate += 1
tests['finite_geometry'] = all(math.isfinite(c) for v in verts for c in v)
tests['expected_dimensions_blender_xyz'] = all(abs(a-z)<1e-5 for a,z in zip(dimensions,[1.55,.07,.9]))
tests['bottom_zero_centered_xy'] = abs(low[2])<1e-5 and abs(low[0]+high[0])<1e-5 and abs(low[1]+high[1])<1e-5
tests['triangle_budget'] = triangles <= 2000
tests['no_degenerate_triangles'] = degenerate == 0
report['geometry'] = {'triangles':triangles, 'degenerate_triangles':degenerate, 'bounds_after_glb_reimport_blender_xyz_m':[low,high], 'dimensions_width_depth_height_m':dimensions, 'glb_axis_order':'X width, Y height, Z depth; exporter uses Y-up'}
for name in ['front','side','oblique']:
    f = P/'renders'/(name+'.png')
    im = bpy.data.images.load(str(f), check_existing=False)
    tests[name+'_png_1200x800_rgba'] = list(im.size) == [1200,800] and im.channels == 4
    bpy.data.images.remove(im)
report['visual_inspection'] = {'reviewed_utc':'2026-10-15T15:39:24Z', 'views':['front','side','oblique'], 'result':'All three final views inspected. Full silhouette with margins; narrow continuous bezel, recessed blank panel and thin closed cabinet visible. No source images, letters, logos or invented display content.', 'reviewer':'asset author'}
report['warnings'] = ['Build log contains a harmless single-object join warning for the screen batch; final GLB import, primitive count and geometry are checked here.', 'Hidden rear and all dimensions are estimates.', 'No independent regeneration or Three.js/full-scene validation was performed.']
report['passed'] = all(tests.values())
report['finished_utc'] = utc()
report['seconds'] = round(time.perf_counter()-start,4)
json.dump(report,open(P/'validation.json','w'),indent=2)
print('VALIDATION',json.dumps(report))
assert report['passed'], report
