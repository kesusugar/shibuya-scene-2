"""Normalise an externally generated prop model (e.g. ChatGPT dots, any GLB/FBX/OBJ) for the Core, Blender 4.2.3.

blender -b --python-exit-code 1 -P tools/props/import_prop.py -- <spec.json> <in model> <out.glb> <report.json>

spec.json (one per prop, in assets/street/props/source/data/specs/):
  {"id": "vending_machine", "target": {"height_m": 1.83, "width_m": 1.0, "depth_m": 0.75},   # any subset; height wins
   "max_triangles": 4000, "lod_ratio": 0.25,                      # LOD1 for distance, 0 = no LOD
   "materials": {"default": "furniture", "glass": "glass"},       # class per material-name pattern (see look.ts)
   "source": {"tool": "ChatGPT dots", "author": "...", "date": "2026-10-14", "terms": "..."}}
What it does, in this order (each step is reported):
  1. imports, applies all transforms, joins into one object (multi-object models become one mesh, materials kept);
  2. Z-up, base at z=0, centred on x/y (pivot = centre of the footprint at ground level);
  3. scales uniformly so the height matches target.height_m (else the largest given dimension); records the
     resulting other dimensions and their error against the targets - a large error means the generated
     proportions are wrong and the model should be regenerated, not stretched;
  4. removes loose geometry, recalculates normals outward (vertex merging only with "merge_vertices": true);
  5. decimates to max_triangles if needed; writes LOD1 (lod_ratio) as a second node '<id>_lod1';
  6. renames materials to 'prop_<class>_<n>' so the viewer's look classes apply (no photo textures are created);
  7. exports GLB (Y-up) with the original textures, and a report with dimensions, triangles, and warnings.
"""
import bpy, bmesh, json, sys, re
from pathlib import Path
from mathutils import Vector

spec_path, src, out, report_path = sys.argv[sys.argv.index('--') + 1:][:4]
S = json.loads(Path(spec_path).read_text()); R = {'id': S['id'], 'source_file': Path(src).name, 'warnings': []}
bpy.ops.wm.read_factory_settings(use_empty=True)
ext = Path(src).suffix.lower()
if ext in ('.glb', '.gltf'): bpy.ops.import_scene.gltf(filepath=src)
elif ext == '.fbx': bpy.ops.import_scene.fbx(filepath=src)
elif ext == '.obj': bpy.ops.wm.obj_import(filepath=src)
else: raise SystemExit(f'unsupported format {ext}')
meshes = [o for o in bpy.context.scene.objects if o.type == 'MESH']
assert meshes, 'no mesh in the model'
for o in bpy.context.scene.objects: o.select_set(o in meshes)
bpy.context.view_layer.objects.active = meshes[0]
bpy.ops.object.transform_apply(location=True, rotation=True, scale=True)
if len(meshes) > 1: bpy.ops.object.join()
ob = bpy.context.view_layer.objects.active; ob.name = S['id']
for o in list(bpy.context.scene.objects):
    if o is not ob: bpy.data.objects.remove(o, do_unlink=True)
me = ob.data
# glTF imports are Y-up converted to Z-up by the importer; FBX/OBJ may not be - detect a lying model
dims = ob.dimensions.copy(); R['input_dimensions'] = [round(v, 4) for v in dims]
# 2. pivot: footprint centre at ground level
bb = [Vector(c) for c in ob.bound_box]; lo = Vector((min(c.x for c in bb), min(c.y for c in bb), min(c.z for c in bb))); hi = Vector((max(c.x for c in bb), max(c.y for c in bb), max(c.z for c in bb)))
shift = Vector(((lo.x + hi.x) / 2, (lo.y + hi.y) / 2, lo.z))
me.transform(__import__('mathutils').Matrix.Translation(-shift))
# 3. uniform scale
T = S.get('target', {}); size = hi - lo
if 'height_m' in T: k = T['height_m'] / max(size.z, 1e-6)
else:
    pairs = [(T[key], v) for key, v in (('width_m', size.x), ('depth_m', size.y)) if key in T]
    k = max(pairs, key=lambda p: p[0])[0] / max(max(pairs, key=lambda p: p[0])[1], 1e-6) if pairs else 1.0
me.transform(__import__('mathutils').Matrix.Scale(k, 4)); size *= k
# footprint: width = larger horizontal side
w, d = (size.x, size.y) if size.x >= size.y else (size.y, size.x)
R['scale_factor'] = round(k, 5); R['dimensions_m'] = {'width': round(w, 3), 'depth': round(d, 3), 'height': round(size.z, 3)}
for key, v in (('width_m', w), ('depth_m', d)):
    if key in T and abs(v - T[key]) / T[key] > 0.15:
        R['warnings'].append(f'{key}: {v:.2f} m vs target {T[key]:.2f} m ({(v / T[key] - 1) * 100:+.0f} %) - proportions differ; regenerate rather than stretch')
# 4. cleanup
bm = bmesh.new(); bm.from_mesh(me)
before = len(bm.verts)
# merging would discard the split normals of hard edges (boxes turn smooth); only when the spec asks for it
if S.get('merge_vertices'): bmesh.ops.remove_doubles(bm, verts=bm.verts, dist=0.0005)
loose = [v for v in bm.verts if not v.link_faces]; bmesh.ops.delete(bm, geom=loose, context='VERTS')
bmesh.ops.recalc_face_normals(bm, faces=bm.faces); bm.to_mesh(me); bm.free()
R['merged_vertices'] = before - len(me.vertices)
me.calc_loop_triangles(); tri = len(me.loop_triangles); R['input_triangles'] = tri
# 5. decimate
limit = S.get('max_triangles', 4000)
if tri > limit:
    m = ob.modifiers.new('decimate', 'DECIMATE'); m.ratio = limit / tri
    bpy.context.view_layer.objects.active = ob; bpy.ops.object.modifier_apply(modifier=m.name)
    me.calc_loop_triangles(); R['warnings'].append(f'decimated {tri} -> {len(me.loop_triangles)} triangles')
R['triangles'] = len(me.loop_triangles)
# 6. material classes
rules = S.get('materials', {'default': 'furniture'})
for i, mat in enumerate(me.materials):
    if mat is None: continue
    cls = next((c for pat, c in rules.items() if pat != 'default' and re.search(pat, mat.name, re.I)), rules.get('default', 'furniture'))
    mat.name = f'prop_{cls}_{i}'
R['materials'] = [m.name for m in me.materials if m]
if not me.uv_layers: R['warnings'].append('no UVs: textures cannot be used, solid colours only')
lod = S.get('lod_ratio', 0.25)
if lod:
    l1 = ob.copy(); l1.data = me.copy(); l1.name = S['id'] + '_lod1'; bpy.context.collection.objects.link(l1)
    m = l1.modifiers.new('decimate', 'DECIMATE'); m.ratio = lod
    bpy.context.view_layer.objects.active = l1; bpy.ops.object.modifier_apply(modifier=m.name)
    l1.data.calc_loop_triangles(); R['lod1_triangles'] = len(l1.data.loop_triangles)
Path(out).parent.mkdir(parents=True, exist_ok=True)
bpy.ops.export_scene.gltf(filepath=out, export_format='GLB', export_yup=True)
R['bytes'] = Path(out).stat().st_size; R['source'] = S.get('source', {})
Path(report_path).write_text(json.dumps(R, ensure_ascii=False, indent=1) + '\n')
print('PROP', S['id'], R['dimensions_m'], R['triangles'], R['warnings'])
