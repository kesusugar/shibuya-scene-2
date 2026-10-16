"""Inventory each existing station-north dark plane without modifying the model.

Run with Blender: blender -b -P scripts/audit-station-louvres.py -- INPUT.glb OUTPUT.json
Coordinates in the output use the project's X-east/Y-north/Z-up metres.
"""
import bpy
import json
import sys
from pathlib import Path
from mathutils import Vector

source, target = sys.argv[sys.argv.index('--') + 1:][:2]
bpy.ops.wm.read_factory_settings(use_empty=True)
bpy.ops.import_scene.gltf(filepath=source)
mesh_object = next(ob for ob in bpy.context.scene.objects if ob.name.startswith('stn_louvre') and ob.type == 'MESH')
mesh = mesh_object.data
mesh.calc_loop_triangles()
assert len(mesh.loop_triangles) == 28, len(mesh.loop_triangles)
planes = []
triangle_points = [
    {tuple(round(v, 5) for v in mesh_object.matrix_world @ mesh.vertices[vertex].co)
     for vertex in tri.vertices}
    for tri in mesh.loop_triangles
]
groups = []
remaining = set(range(28))
while remaining:
    first = min(remaining)
    pair = next((i for i in remaining if i != first and len(triangle_points[first] & triangle_points[i]) >= 2), None)
    assert pair is not None, first
    remaining.remove(first)
    remaining.remove(pair)
    groups.append((first, pair))
assert len(groups) == 14
for index, pair in enumerate(groups):
    triangles = [mesh.loop_triangles[i] for i in pair]
    unique = {}
    for tri in triangles:
        for vertex in tri.vertices:
            point = mesh_object.matrix_world @ mesh.vertices[vertex].co
            unique[tuple(round(v, 5) for v in point)] = point
    assert len(unique) == 4, (index, list(unique))
    points = list(unique.values())
    # Blender import is Z-up. The source polygons are vertical rectangles.
    bounds = [[min(p[j] for p in points), max(p[j] for p in points)] for j in range(3)]
    center = sum(points, Vector()) / 4
    edge = max((b - a for a in points for b in points if abs(a.z - b.z) < .01), key=lambda v: v.length)
    normal = edge.cross(Vector((0, 0, 1))).normalized()
    source_normal = triangles[0].normal
    if normal.dot(source_normal) < 0:
        normal.negate()
    planes.append({
        'id': f'stn_louvre_{index + 1:02d}',
        'triangle_indices': list(pair),
        'center_xyz_m': [round(v, 3) for v in center],
        'normal_xyz': [round(v, 4) for v in normal],
        'width_m': round(edge.length, 3),
        'height_m': round(bounds[2][1] - bounds[2][0], 3),
        'bounds_xyz_m': [[round(v, 3) for v in pair] for pair in bounds],
    })
Path(target).parent.mkdir(parents=True, exist_ok=True)
Path(target).write_text(json.dumps({'source': source.replace('\\', '/').split('/assets/')[-1], 'planes': planes}, indent=2) + '\n')
print('14 station louvre planes inventoried')
