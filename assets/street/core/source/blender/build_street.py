"""C2b first assets: registered entrance footprints and tree nodes, Blender 4.2.3.

blender -b --python-exit-code 1 -t 4 -P build_street.py -- input.json ground.glb out.glb stats.json
Dimensions are provisional. Unresolved signal/lighting positions are not invented.
Ground is imported only for surveying and is not included in the export.
"""
import bpy
import bmesh
import json
import math
import random
import sys
from pathlib import Path

from mathutils import Vector
from mathutils.bvhtree import BVHTree

src, ground, output, stats_path = sys.argv[sys.argv.index('--') + 1:][:4]
assert bpy.app.version == (4, 2, 3), 'Use Blender 4.2.3 LTS'
D = json.loads(Path(src).read_text())
P = D['parameters']
foliage_mode = sys.argv[sys.argv.index('--') + 5:][0] if len(sys.argv[sys.argv.index('--') + 5:]) else P.get('foliage_mode', 'coarse')
assert foliage_mode in ('leaves', 'coarse')
DATUM = D['datum_tp_m']
bpy.ops.wm.read_factory_settings(use_empty=True)
bpy.ops.import_scene.gltf(filepath=ground)
bm = bmesh.new()
for ob in list(bpy.context.scene.objects):
    if ob.type == 'MESH' and ob.name.startswith(('ground_road', 'ground_intersection', 'ground_sidewalk', 'ground_fill')):
        me = ob.data.copy()
        me.transform(ob.matrix_world)
        bm.from_mesh(me)
        bpy.data.meshes.remove(me)
bvh = BVHTree.FromBMesh(bm)
bm.free()
for ob in list(bpy.context.scene.objects):
    bpy.data.objects.remove(ob, do_unlink=True)


def pavement(x, y):
    hit = bvh.ray_cast(Vector((x, y, 50)), Vector((0, 0, -1)))
    return hit[0].z if hit[0] is not None else None


def anchor(points):
    samples = []
    for x, y in points:
        # Entrance footprints may be holes in ground_fill. Survey beside the footprint too.
        for dx, dy in [(0, 0), (0.4, 0), (-0.4, 0), (0, 0.4), (0, -0.4), (0.8, 0), (-0.8, 0), (0, 0.8), (0, -0.8)]:
            z = pavement(x + dx, y + dy)
            if z is not None:
                samples.append(z)
    assert samples, f'No surveyed ground around {points}'
    return min(samples), max(samples)


MATS = {}


def mat(name, rgb, rough=0.6, metal=0):
    m = bpy.data.materials.new(name)
    m.use_nodes = True
    b = m.node_tree.nodes['Principled BSDF']
    b.inputs['Base Color'].default_value = (*rgb, 1)
    b.inputs['Roughness'].default_value = rough
    b.inputs['Metallic'].default_value = metal
    MATS[name] = m
    return m


mat('street_roof', (0.35, 0.38, 0.4), 0.45, 0.4)
mat('street_steel', (0.28, 0.3, 0.32), 0.35, 0.75)
mat('street_concrete', (0.26, 0.27, 0.28), 0.9)
mat('street_tree_bark', (0.09, 0.065, 0.04), 0.95)
mat('street_tree_leaves', (0.035, 0.10, 0.025), 0.95)


def finish(ob, material):
    ob.data.materials.clear()
    ob.data.materials.append(MATS[material])
    return ob


def box(name, center, size, material, angle=0):
    bpy.ops.mesh.primitive_cube_add(size=1, location=center)
    ob = bpy.context.object
    ob.name = name
    ob.dimensions = size
    ob.rotation_euler.z = angle
    bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
    return finish(ob, material)


def rod(name, a, b, radius, material, vertices=10):
    a, b = Vector(a), Vector(b)
    d = b - a
    bpy.ops.mesh.primitive_cylinder_add(vertices=vertices, radius=radius, depth=d.length, location=(a + b) / 2)
    ob = bpy.context.object
    ob.name = name
    ob.rotation_euler = d.to_track_quat('Z', 'Y').to_euler()
    return finish(ob, material)


records = []
for f in D['features']:
    tag = f['id'].replace('/', '_')
    if f['kind'] == 'tree':
        x, y = f['point']
        lo, hi = anchor([(x, y)])
        # A tree node itself must have a sampled surface, not an arbitrary default elevation.
        z = pavement(x, y)
        assert z is not None, f"{f['id']}: no ground directly at tree node"
        h = P['tree_height_m']
        rod(tag + '_trunk', (x, y, z - 0.05), (x, y, z + h * 0.72), P['tree_trunk_radius_m'], 'street_tree_bark')
        rng = random.Random(f['id'])
        for i in range(5):
            dx, dy = (rng.uniform(-1.2, 1.2) for _ in range(2))
            cz = z + h * (0.64 + i * 0.035)
            rod(tag + '_branch', (x, y, z + h * 0.4), (x + dx, y + dy, cz), 0.065, 'street_tree_bark', 8)
            if foliage_mode == 'coarse':
                bpy.ops.mesh.primitive_ico_sphere_add(subdivisions=2, radius=1, location=(x + dx, y + dy, cz))
                ob = bpy.context.object; ob.name = tag + '_crown'
                ob.scale = (P['tree_crown_radius_m'] * 0.65, P['tree_crown_radius_m'] * 0.65, h * 0.22)
                finish(ob, 'street_tree_leaves')
            else:
                core_scale = P.get('tree_crown_core_scale', 0)
                if core_scale:
                    # Interior canopy volume compensates for under-sampling by the finite leaf-card budget.
                    bpy.ops.mesh.primitive_ico_sphere_add(subdivisions=2, radius=1, location=(x + dx, y + dy, cz))
                    core = bpy.context.object; core.name = tag + '_canopy_core'
                    core.scale = (P['tree_crown_radius_m'] * 0.65 * core_scale,
                                  P['tree_crown_radius_m'] * 0.65 * core_scale, h * 0.22 * core_scale)
                    for polygon in core.data.polygons: polygon.use_smooth = True
                    finish(core, 'street_tree_leaves')
                # Original procedural leaves: individual double-sided quads, no photo texture or external model.
                verts, faces = [], []
                leaf_rng = random.Random(f"{f['id']}:leaf:{i}")
                for j in range(500):
                    direction = Vector([leaf_rng.gauss(0, 1) for _ in range(3)]).normalized()
                    radius = leaf_rng.random() ** (1 / 3)
                    local = direction * radius
                    crown_half = P.get('tree_crown_depth_m', h * 0.44) / 2
                    center = Vector((x + dx + local.x * P['tree_crown_radius_m'] * 0.65,
                                     y + dy + local.y * P['tree_crown_radius_m'] * 0.65,
                                     cz + h * 0.22 - crown_half + local.z * crown_half))
                    u = Vector([leaf_rng.gauss(0, 1) for _ in range(3)]).normalized()
                    normal = Vector([leaf_rng.gauss(0, 1) for _ in range(3)]).normalized()
                    v = u.cross(normal).normalized()
                    u *= leaf_rng.uniform(0.12, 0.22); v *= leaf_rng.uniform(0.04, 0.085)
                    n = len(verts)
                    verts.extend([center-u-v, center+u-v, center+u+v, center-u+v])
                    faces.append((n, n+1, n+2, n+3))
                mesh = bpy.data.meshes.new(tag + '_leaf_mesh'); mesh.from_pydata(verts, [], faces)
                ob = bpy.data.objects.new(tag + '_leaves', mesh); bpy.context.collection.objects.link(ob)
                finish(ob, 'street_tree_leaves')
        records.append({**f, 'anchor_tp': round(z + DATUM, 3), 'survey_min_tp': round(lo + DATUM, 3), 'survey_max_tp': round(hi + DATUM, 3)})
        continue

    ring = [Vector(p) for p in f['ring']]
    edges = [ring[(i + 1) % len(ring)] - p for i, p in enumerate(ring)]
    u = max(edges, key=lambda e: e.length).normalized()
    v = Vector((-u.y, u.x))
    lu = [p.dot(u) for p in ring]
    lv = [p.dot(v) for p in ring]
    length, width = max(lu) - min(lu), max(lv) - min(lv)
    center = u * ((max(lu) + min(lu)) / 2) + v * ((max(lv) + min(lv)) / 2)
    angle = math.atan2(u.y, u.x)
    lo, hi = anchor([tuple(p) for p in ring])

    def xy(a, b):
        p = center + u * a + v * b
        return p.x, p.y

    clearance = P['canopy_clearance_m']
    # Foundations and a shallow visible landing, not an invented underground station.
    box(tag + '_landing', (*center, lo - 0.06), (length, width, 0.12), 'street_concrete', angle)
    for a in (-length / 2 + 0.2, length / 2 - 0.2):
        for b in (-width / 2 + 0.15, width / 2 - 0.15):
            x, y = xy(a, b)
            rod(tag + '_post', (x, y, lo - 0.08), (x, y, lo + clearance), P['canopy_post_radius_m'], 'street_steel')
    # Shared curved metal canopy. Shape/height are explicitly provisional.
    for i in range(12):
        b0 = width * (i / 12 - 0.5)
        b1 = width * ((i + 1) / 12 - 0.5)
        z0 = lo + clearance + P['canopy_arch_m'] * math.cos(math.pi * b0 / width)
        z1 = lo + clearance + P['canopy_arch_m'] * math.cos(math.pi * b1 / width)
        pts = [(*xy(a, b), z) for a, b, z in [(-length / 2, b0, z0), (length / 2, b0, z0), (length / 2, b1, z1), (-length / 2, b1, z1)]]
        me = bpy.data.meshes.new(tag + '_roof')
        me.from_pydata(pts, [], [(0, 1, 2, 3)])
        ob = bpy.data.objects.new(tag + '_roof', me)
        bpy.context.collection.objects.link(ob)
        finish(ob, 'street_roof')
        solid = ob.modifiers.new('roof_thickness', 'SOLIDIFY')
        solid.thickness = 0.045
    # Handrails are attached to the mapped entrance, not guessed along road edges.
    for b in (-width / 2 + 0.15, width / 2 - 0.15):
        a0, a1 = -length / 2 + 0.25, length / 2 - 0.25
        for a in (a0, 0, a1):
            x, y = xy(a, b)
            rod(tag + '_rail_post', (x, y, lo), (x, y, lo + P['handrail_height_m']), 0.025, 'street_steel')
        rod(tag + '_handrail', (*xy(a0, b), lo + P['handrail_height_m']), (*xy(a1, b), lo + P['handrail_height_m']), 0.025, 'street_steel')
    records.append({**f, 'anchor_tp': round(lo + DATUM, 3), 'survey_min_tp': round(lo + DATUM, 3), 'survey_max_tp': round(hi + DATUM, 3), 'max_burial_m': round(hi - lo, 3), 'length_m': round(length, 3), 'width_m': round(width, 3), 'stairs': 'not exported: descent direction and interior not verified'})

# Bake modifiers and combine static geometry by material to stay within the draw budget.
for name in MATS:
    bpy.ops.object.select_all(action='DESELECT')
    objs = [o for o in bpy.context.scene.objects if o.type == 'MESH' and o.data.materials and o.data.materials[0].name == name]
    for ob in objs:
        bpy.context.view_layer.objects.active = ob
        for mod in list(ob.modifiers):
            bpy.ops.object.modifier_apply(modifier=mod.name)
        ob.select_set(True)
    if objs:
        bpy.context.view_layer.objects.active = objs[0]
        bpy.ops.object.join()
        bpy.context.object.name = name

stats = {'foliage_mode': foliage_mode, 'blender': bpy.app.version_string, 'datum_tp_m': DATUM, 'features': records, 'unresolved': D['unresolved'], 'missing_sources': D['missing_sources'], 'objects': {}}
for ob in bpy.context.scene.objects:
    if ob.type == 'MESH':
        ob.data.calc_loop_triangles()
        stats['objects'][ob.name] = {'triangles': len(ob.data.loop_triangles), 'vertices': len(ob.data.vertices)}
stats['triangles'] = sum(m['triangles'] for m in stats['objects'].values())
Path(output).parent.mkdir(parents=True, exist_ok=True)
bpy.ops.export_scene.gltf(filepath=output, export_format='GLB', export_yup=True, export_cameras=False, export_lights=False)
Path(stats_path).write_text(json.dumps(stats, ensure_ascii=False, indent=2) + '\n')
print('STREET', len(records), 'features,', stats['triangles'], 'triangles')
