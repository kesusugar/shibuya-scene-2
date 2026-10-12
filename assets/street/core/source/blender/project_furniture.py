"""Back-project observed ground pixels onto the existing C2a ground, Blender 4.2.3.

blender -b --python-exit-code 1 -P project_furniture.py -- observations.json ground.glb out.json
Camera position/points use plan X east/Y north/Z datum. No fallback plane or guessed height.
Reported pixel sensitivity is not a confidence interval for the whole camera calibration.
"""
import bpy
import bmesh
import json
import math
import sys
from pathlib import Path
from mathutils import Vector
from mathutils.bvhtree import BVHTree

source, ground, output = sys.argv[sys.argv.index('--') + 1:][:3]
D = json.loads(Path(source).read_text())
C = D['camera']
assert C['W'] > 0 and C['H'] > 0
assert all(math.isfinite(x) for x in C['pos'])
bpy.ops.wm.read_factory_settings(use_empty=True)
bpy.ops.import_scene.gltf(filepath=ground)
bm = bmesh.new()
for ob in bpy.context.scene.objects:
    if ob.type == 'MESH' and ob.name.startswith(('ground_road', 'ground_intersection', 'ground_sidewalk', 'ground_fill')):
        mesh = ob.data.copy()
        mesh.transform(ob.matrix_world)
        bm.from_mesh(mesh)
        bpy.data.meshes.remove(mesh)
bvh = BVHTree.FromBMesh(bm)
bm.free()
yaw, pitch, roll = map(math.radians, (C['yaw'], C['pitch'], C['roll']))
forward = Vector((math.sin(yaw) * math.cos(pitch), math.cos(yaw) * math.cos(pitch), math.sin(pitch)))
right0 = Vector((math.cos(yaw), -math.sin(yaw), 0))
up0 = right0.cross(forward)
right = right0 * math.cos(roll) - up0 * math.sin(roll)
up = up0 * math.cos(roll) + right0 * math.sin(roll)
focal = C.get('fpx') or C['H'] / 2 / math.tan(math.radians(C['vfov']) / 2)
origin = Vector(C['pos'])
origin.z += C.get('datum_offset_m', 0)


def hit(px):
    ray = (forward + right * ((px[0] - C['W'] / 2) / focal) - up * ((px[1] - C['H'] / 2) / focal)).normalized()
    loc, _, _, distance = bvh.ray_cast(origin, ray)
    return loc, distance


results = []
for row in D['observations']:
    out = {**row, 'source': 'photo-projection', 'photo': D['photo'], 'camera_status': D['camera_status']}
    if not row.get('ground_base_visible', False):
        out.update(status='unresolved', reason='Base occluded: no projection of an invented foot point')
        results.append(out)
        continue
    px = row['px']
    assert 0 <= px[0] < C['W'] and 0 <= px[1] < C['H'], row['id']
    point, distance = hit(px)
    if point is None:
        out.update(status='unresolved', reason='Ray misses surveyed ground; no fallback plane was used')
        results.append(out)
        continue
    sigma = row.get('pixel_read_error_px', 2) + C.get('rms_px', 0)
    shifts = []
    for du, dv in [(-sigma, 0), (sigma, 0), (0, -sigma), (0, sigma), (-sigma, -sigma), (sigma, sigma)]:
        p, _ = hit((px[0] + du, px[1] + dv))
        if p is not None:
            shifts.append(math.hypot(p.x - point.x, p.y - point.y))
    radius = max(shifts) if len(shifts) == 6 else None
    out.update(point=[round(point.x, 3), round(point.y, 3)], anchor_tp=round(point.z + 15, 3),
               ray_distance_m=round(distance, 2), pixel_error_ground_radius_m=round(radius, 3) if radius is not None else None,
               status='provisional', reason='Photo-derived position; camera and feature identity still require independent validation')
    if radius is None or radius > 1:
        out['reason'] += '; pixel sensitivity exceeds the 1m verification limit or sampled rays miss ground'
    results.append(out)
Path(output).write_text(json.dumps({**D, 'observations': results}, ensure_ascii=False, indent=2) + '\n')
print('PROJECTED', sum('point' in r for r in results), 'of', len(results))
