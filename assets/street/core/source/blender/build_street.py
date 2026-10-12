"""C2b street furniture of the Core, Blender 4.2.3 (v2, replaces the shared bus-shelter canopies and blob trees).

blender -b --python-exit-code 1 -t 4 -P build_street.py -- street_input.json street_layout.json ground.glb out.glb stats.json

Positions: entrances and trees from OSM 2025-10 footprints/nodes (street_input.json); signals and railings from the
written rules of tools/street_layout.py; lamps and one sign pair from Codex's Stream 2025 projection. Every height is
sampled from the Core ground (imported for surveying only, never exported).
Shapes are generic Japanese street furniture at standard sizes, not photo-measured models of each object.
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

src, layout_path, ground, output, stats_path = sys.argv[sys.argv.index('--') + 1:][:5]
assert bpy.app.version == (4, 2, 3), 'Use Blender 4.2.3 LTS'
D = json.loads(Path(src).read_text())
L = json.loads(Path(layout_path).read_text())
DATUM = D['datum_tp_m']
CENTRE = Vector(L['centre'])
bpy.ops.wm.read_factory_settings(use_empty=True)
bpy.ops.import_scene.gltf(filepath=ground)
bm = bmesh.new()
for ob in list(bpy.context.scene.objects):
    if ob.type == 'MESH' and ob.name.startswith(('ground_road', 'ground_intersection', 'ground_sidewalk', 'ground_fill')):
        me = ob.data.copy(); me.transform(ob.matrix_world); bm.from_mesh(me); bpy.data.meshes.remove(me)
bvh = BVHTree.FromBMesh(bm)
bm.free()
for ob in list(bpy.context.scene.objects):
    bpy.data.objects.remove(ob, do_unlink=True)


def pavement(x, y):
    hit = bvh.ray_cast(Vector((x, y, 50)), Vector((0, 0, -1)))
    return hit[0].z if hit[0] is not None else None


def ground_at(x, y):
    for r in (0, 0.3, 0.6, 1.0):
        for dx, dy in ((0, 0), (r, 0), (-r, 0), (0, r), (0, -r)):
            z = pavement(x + dx, y + dy)
            if z is not None:
                return z
    raise AssertionError(f'no surveyed ground near {x:.1f},{y:.1f}')


# ---------------------------------------------------------------- materials
MATS = {}


def mat(name, rgb, rough=0.6, metal=0.0, emit=None, strength=0.0, alpha=1.0):
    m = bpy.data.materials.new(name); m.use_nodes = True
    b = m.node_tree.nodes['Principled BSDF']
    b.inputs['Base Color'].default_value = (*rgb, 1)
    b.inputs['Roughness'].default_value = rough
    b.inputs['Metallic'].default_value = metal
    if emit:
        b.inputs['Emission Color'].default_value = (*emit, 1); b.inputs['Emission Strength'].default_value = strength
    if alpha < 1:
        b.inputs['Alpha'].default_value = alpha; m.blend_method = 'BLEND'
    MATS[name] = m


mat('street_concrete', (0.30, 0.30, 0.29), 0.9)              # stair treads and landings (walkable)
mat('street_stair_well', (0.05, 0.05, 0.055), 0.9)           # dark walls of the stair well
mat('street_roof', (0.50, 0.51, 0.51), 0.5, 0.3)            # entrance roof slab and fascia (light grey: 2025-02 photo)
mat('street_panel', (0.55, 0.56, 0.56), 0.45, 0.6)           # entrance parapets, aluminium cladding
mat('street_glass', (0.55, 0.62, 0.64), 0.05, 0.0, alpha=0.35)
mat('street_sign_blue', (0.02, 0.18, 0.55), 0.4, emit=(0.02, 0.18, 0.55), strength=0.6)
mat('street_sign_white', (0.85, 0.86, 0.86), 0.4, emit=(0.9, 0.9, 0.9), strength=0.4)
mat('street_steel', (0.20, 0.21, 0.22), 0.45, 0.7)           # signal and lamp poles (dark grey)
mat('street_signal_body', (0.025, 0.025, 0.028), 0.5)
mat('street_signal_green', (0.0, 0.25, 0.18), 0.3, emit=(0.1, 1.0, 0.75), strength=4.0)
mat('street_signal_red', (0.3, 0.0, 0.0), 0.3, emit=(1.0, 0.12, 0.05), strength=4.0)
mat('street_rail', (0.78, 0.79, 0.78), 0.4, 0.3)             # white kerb railing (横断防止柵)
mat('street_lamp_glass', (0.85, 0.80, 0.70), 0.2)            # emissive set at night by src/world/street.ts
mat('street_tree_bark', (0.11, 0.085, 0.06), 0.95)
mat('street_tree_leaves', (0.045, 0.11, 0.03), 0.85)
mat('street_tree_leaves_light', (0.09, 0.19, 0.045), 0.8)


# ---------------------------------------------------------------- mesh builders (one bmesh per material)
BM = {name: bmesh.new() for name in MATS}


def add_box(material, center, size, angle=0.0):
    b = BM[material]
    m = bmesh.ops.create_cube(b, size=1.0)
    for v in m['verts']:
        v.co = Vector((v.co.x * size[0], v.co.y * size[1], v.co.z * size[2]))
        v.co.rotate(_rot(angle)); v.co += Vector(center)


def _rot(angle):
    from mathutils import Matrix
    return Matrix.Rotation(angle, 3, 'Z')


def add_rod(material, a, b, radius, seg=8):
    a, b = Vector(a), Vector(b); d = b - a
    bb = BM[material]
    m = bmesh.ops.create_cone(bb, cap_ends=True, segments=seg, radius1=radius, radius2=radius, depth=d.length)
    q = d.to_track_quat('Z', 'Y')
    for v in m['verts']:
        v.co.rotate(q); v.co += (a + b) / 2


def add_disc(material, center, normal, radius, seg=16):
    bb = BM[material]
    m = bmesh.ops.create_circle(bb, cap_ends=True, segments=seg, radius=radius)
    q = Vector(normal).to_track_quat('Z', 'Y')
    for v in m['verts']:
        v.co.rotate(q); v.co += Vector(center)


def add_ico(material, center, scale, subdiv=2, noise=0.0, rng=None):
    bb = BM[material]
    m = bmesh.ops.create_icosphere(bb, subdivisions=subdiv, radius=1.0)
    for v in m['verts']:
        k = 1 + (rng.uniform(-noise, noise) if rng else 0)
        v.co = Vector((v.co.x * scale[0] * k, v.co.y * scale[1] * k, v.co.z * scale[2] * k)) + Vector(center)
    for f in {f for v in m['verts'] for f in v.link_faces}:
        f.smooth = True


def add_quad(material, pts):
    bb = BM[material]
    vs = [bb.verts.new(p) for p in pts]
    bb.faces.new(vs)


records = []

# ---------------------------------------------------------------- entrances
for f in [f for f in D['features'] if f['kind'] == 'entrance']:
    ring = [Vector(p) for p in f['ring']]
    edges = [ring[(i + 1) % len(ring)] - p for i, p in enumerate(ring)]
    u = max(edges, key=lambda e: e.length).normalized(); v = Vector((-u.y, u.x))
    lu = [p.dot(u) for p in ring]; lv = [p.dot(v) for p in ring]
    length, width = max(lu) - min(lu), max(lv) - min(lv)
    c = u * ((max(lu) + min(lu)) / 2) + v * ((max(lv) + min(lv)) / 2)
    # open end: the short end nearer to the crossing (pedestrian flow); descent towards the closed end
    if (c + u * length / 2 - CENTRE).length < (c - u * length / 2 - CENTRE).length:
        u = -u; v = -v
    angle = math.atan2(u.y, u.x)
    zs = [z for z in (pavement(*(c + u * a + v * b)) for a in (-length / 2 - 0.5, 0, length / 2 + 0.5) for b in (-width / 2 - 0.5, width / 2 + 0.5)) if z is not None]
    lo, hi = min(zs), max(zs)
    inside = [z for z in (pavement(*(c + u * a + v * b)) for a in (-length * 0.4, 0, length * 0.4) for b in (-width * 0.35, 0, width * 0.35)) if z is not None]
    top = (max(inside) if inside else lo) + 0.02          # surface over the footprint (sidewalk level, not the road)

    def P(a, b, z):
        p = c + u * a + v * b
        return (p.x, p.y, z)

    H, ROOF, PAR = 2.55, 0.28, 1.05
    t = 0.12                                                   # wall thickness
    # stair: from the open end (a = -length/2) down to the closed end, 0.17 m rise per 0.30 m going
    going, rise = 0.30, 0.17
    n = int((length - 0.6) / going)
    for i in range(n):
        a0 = -length / 2 + 0.3 + i * going
        z = top - (i + 1) * rise
        add_box('street_concrete', P(a0 + going / 2, 0, z - 0.1), (going, width - 2 * t, 0.2), angle)
    depth = n * rise + 0.3
    # The Core ground has no holes at the footprints (C2a), so the descent is drawn on top of it: a dark well with a
    # light nosing line per tread, which reads as stairs going down from street level. The treads below stay walkable.
    a_start, a_end = -length / 2 + 0.3, length / 2 - t
    add_box('street_stair_well', P((a_start + a_end) / 2, 0, top + 0.012), (a_end - a_start, width - 2 * t, 0.01), angle)
    for i in range(n):
        a0 = a_start + i * going
        if a0 + 0.05 > a_end:
            break
        shade = max(0.0, 1 - i / 6)                      # nosings fade into the dark further down
        if shade > 0:
            add_box('street_concrete', P(a0 + 0.025, 0, top + 0.02), (0.05, (width - 2 * t) * 0.98, 0.012), angle)
    # well walls below the pavement (inside the footprint) and the landing at the open end
    for b in (-width / 2 + t / 2, width / 2 - t / 2):
        add_box('street_stair_well', P(0, b, top - depth / 2), (length, t, depth), angle)
    add_box('street_stair_well', P(length / 2 - t / 2, 0, top - depth / 2), (t, width, depth), angle)
    add_box('street_concrete', P(-length / 2 + 0.15, 0, top - 0.06), (0.3, width, 0.12), angle)
    # enclosure: solid parapet, glass above, mullions every ~1.2 m on both long sides and the closed end
    for b in (-width / 2 + t / 2, width / 2 - t / 2):
        add_box('street_panel', P(0, b, top + PAR / 2), (length, t, PAR), angle)
        add_box('street_glass', P(0, b, top + (PAR + H) / 2), (length, 0.03, H - PAR), angle)
        m = max(2, round(length / 1.2))
        for i in range(m + 1):
            a = -length / 2 + 0.04 + i * (length - 0.08) / m
            add_box('street_panel', P(a, b, top + H / 2), (0.08, 0.10, H), angle)
    add_box('street_panel', P(length / 2 - t / 2, 0, top + PAR / 2), (t, width, PAR), angle)
    add_box('street_glass', P(length / 2 - t / 2, 0, top + (PAR + H) / 2), (0.03, width, H - PAR), angle)
    # roof slab with a dark fascia and the sign band over the open end
    add_box('street_roof', P(0, 0, top + H + ROOF / 2), (length + 0.4, width + 0.4, ROOF), angle)
    add_box('street_sign_blue', P(-length / 2 - 0.21, 0, top + H + ROOF / 2), (0.02, min(width - 0.2, 2.4), ROOF * 0.8), angle)
    add_box('street_sign_white', P(-length / 2 - 0.22, -min(width - 0.2, 2.4) / 2 + 0.2, top + H + ROOF / 2), (0.02, 0.24, 0.2), angle)
    records.append({**f, 'anchor_tp': round(lo + DATUM, 3), 'survey_min_tp': round(lo + DATUM, 3), 'survey_max_tp': round(hi + DATUM, 3),
                    'max_burial_m': round(hi - lo, 3), 'length_m': round(length, 3), 'width_m': round(width, 3),
                    'open_end': 'rule: short end nearer the crossing centre (not photo-verified)',
                    'shape_status': 'provisional generic Tokyo Metro enclosure (glass sides, flat roof, sign band); not photo-measured'})

# ---------------------------------------------------------------- trees (broad-leaved street trees, generic)
for f in [f for f in D['features'] if f['kind'] == 'tree']:
    x, y = f['point']; z = pavement(x, y)
    assert z is not None, f"{f['id']}: no ground directly at tree node"
    rng = random.Random(f['id'])
    h = rng.uniform(8.5, 10.5); cr = rng.uniform(2.9, 3.5)
    trunk_top = z + h * 0.42
    add_rod('street_tree_bark', (x, y, z - 0.05), (x, y, trunk_top), 0.19, 10)
    cz = z + h * 0.66; crown_h = h * 0.30
    # 3-4 main limbs from the trunk into the crown
    limbs = []
    for i in range(rng.choice((3, 4))):
        ang = i * 2 * math.pi / 4 + rng.uniform(-0.4, 0.4)
        end = (x + math.cos(ang) * cr * 0.55, y + math.sin(ang) * cr * 0.55, cz + rng.uniform(-0.3, 0.6))
        add_rod('street_tree_bark', (x, y, trunk_top - 0.2), end, 0.09, 7); limbs.append(end)
    # crown: overlapping noisy lobes (dark inside, light outside) and leaf cards on the outer shell
    for i in range(16):
        th = rng.uniform(0, 2 * math.pi); ph = rng.uniform(-0.35, 1.0)
        r = rng.uniform(0.35, 0.75)
        p = (x + math.cos(th) * math.cos(ph) * cr * r, y + math.sin(th) * math.cos(ph) * cr * r, cz + math.sin(ph) * crown_h * 0.55)
        s = rng.uniform(1.3, 1.9)
        add_ico('street_tree_leaves' if i % 3 else 'street_tree_leaves_light', p, (s, s, s * 0.8), 2, 0.12, rng)
    for j in range(700):
        d = Vector([rng.gauss(0, 1) for _ in range(3)]).normalized()
        if d.z < -0.55:
            d.z = -d.z * 0.4
        rr = rng.uniform(0.86, 1.05)
        cpt = Vector((x + d.x * cr * rr, y + d.y * cr * rr, cz + d.z * crown_h * 0.85 * rr))
        a = Vector([rng.gauss(0, 1) for _ in range(3)]).normalized(); b = a.cross(d).normalized()
        a = d.cross(b).normalized()
        a *= rng.uniform(0.18, 0.32); b *= rng.uniform(0.14, 0.24)
        add_quad('street_tree_leaves_light' if rng.random() < 0.55 else 'street_tree_leaves', [cpt - a - b, cpt + a - b, cpt + a + b, cpt - a + b])
    records.append({**f, 'anchor_tp': round(z + DATUM, 3), 'survey_min_tp': round(z + DATUM, 3), 'survey_max_tp': round(z + DATUM, 3),
                    'height_m': round(h, 2), 'crown_radius_m': round(cr, 2),
                    'shape_status': 'provisional generic broad-leaved tree; species, height and crown not measured'})

# ---------------------------------------------------------------- signals, lamps, signs
LIGHTS = []


def ped_head(px, py, z0, facing):
    f = Vector((*facing, 0)).normalized(); ang = math.atan2(f.y, f.x)
    o = Vector((px, py, 0)) + f * 0.2
    add_box('street_signal_body', (o.x, o.y, z0 + 0.42), (0.22, 0.36, 0.84), ang)
    # upper lens (stop) lit, lower dark: a single fixed state for a still scene
    front = o + f * 0.115
    add_box('street_signal_red', (front.x, front.y, z0 + 0.63), (0.01, 0.28, 0.28), ang)
    add_box('street_signal_body', (front.x + f.x * 0.005, front.y + f.y * 0.005, z0 + 0.22), (0.01, 0.28, 0.28), ang)


for it in L['items']:
    x, y = it['xy']; z = ground_at(x, y)
    if it['kind'] == 'ped_signal':
        if 'shared_with' not in it:
            add_rod('street_steel', (x, y, z - 0.1), (x, y, z + 3.3), 0.07, 10)
        ped_head(x, y, z + 2.3, it['facing'])
    elif it['kind'] == 'vehicle_signal':
        top = z + 6.2
        add_rod('street_steel', (x, y, z - 0.1), (x, y, top), 0.14, 12)
        ad = Vector((*it['arm_dir'], 0)).normalized()
        end = Vector((x, y, z + 5.6)) + ad * it['arm_m']
        add_rod('street_steel', (x, y, z + 5.6), tuple(end), 0.07, 8)
        add_rod('street_steel', (x, y, z + 6.05), tuple(Vector((x, y, z + 5.62)) + ad * it['arm_m'] * 0.45), 0.035, 6)  # brace
        # flat LED head (Japan: green left, amber centre, red right as seen by the driver), hung under the arm end
        fc = Vector((*it['facing'], 0)).normalized(); ang = math.atan2(fc.y, fc.x)
        hc = end - ad * 0.75 + Vector((0, 0, -0.35))
        add_box('street_signal_body', tuple(hc), (0.16, 1.25, 0.42), ang)
        add_rod('street_steel', tuple(hc + Vector((0, 0, 0.21))), tuple(hc + Vector((0, 0, 0.36))), 0.03, 6)
        side = Vector((-fc.y, fc.x, 0))   # driver's right when looking at the head = head's left
        for k, m_ in ((-1, 'street_signal_green'), (0, 'street_signal_body'), (1, 'street_signal_body')):
            # the driver faces -fc; their left is -side... green is on the driver's left
            p = hc + fc * 0.085 + side * (0.4 * k)
            add_disc(m_, tuple(p), tuple(fc), 0.14)
        records.append({'id': it['id'], 'kind': 'vehicle_signal', 'anchor_tp': round(z + DATUM, 3), 'placement': it['placement'], 'osm_node': it['osm_node']})
        continue
    elif it['kind'] == 'lamp':
        add_rod('street_steel', (x, y, z - 0.1), (x, y, z + 4.6), 0.075, 10)
        add_box('street_steel', (x, y, z + 4.62), (0.36, 0.36, 0.06))
        add_box('street_lamp_glass', (x, y, z + 4.97), (0.32, 0.32, 0.62))
        for dx in (-0.16, 0.16):
            for dy in (-0.16, 0.16):
                add_rod('street_steel', (x + dx, y + dy, z + 4.64), (x + dx, y + dy, z + 5.3), 0.018, 5)
        add_box('street_steel', (x, y, z + 5.36), (0.46, 0.46, 0.12))
        e = bpy.data.objects.new('light_' + it['id'], None); e.location = (x, y, z + 5.0); bpy.context.collection.objects.link(e)
        LIGHTS.append({'id': it['id'], 'tp': round(z + 5.0 + DATUM, 3)})
    elif it['kind'] == 'sign_pair':
        add_rod('street_steel', (x, y, z - 0.1), (x, y, z + 3.2), 0.04, 8)
        toward = (CENTRE - Vector((x, y))).normalized()
        for hz in (2.35, 2.95):
            add_disc('street_sign_blue', (x + toward.x * 0.05, y + toward.y * 0.05, z + hz), (toward.x, toward.y, 0), 0.3, 20)
            add_disc('street_sign_white', (x + toward.x * 0.045, y + toward.y * 0.045, z + hz), (toward.x, toward.y, 0), 0.32, 20)
    records.append({'id': it['id'], 'kind': it['kind'], 'anchor_tp': round(z + DATUM, 3), 'placement': it['placement']})

# ---------------------------------------------------------------- kerb railings (横断防止柵, H 0.8 m, posts every 2 m)
rail_len = 0.0
for run in L['rail_runs']:
    pts = [Vector((p[0], p[1], ground_at(*p))) for p in run]
    dense = [pts[0]]
    for a, b in zip(pts, pts[1:]):
        k = max(1, math.ceil((b - a).length / 2.0))
        for i in range(1, k + 1):
            q = a.lerp(b, i / k); q.z = ground_at(q.x, q.y); dense.append(q)
    for i, p in enumerate(dense):
        add_rod('street_rail', tuple(p - Vector((0, 0, 0.05))), tuple(p + Vector((0, 0, 0.8))), 0.03, 6)
        if i:
            q = dense[i - 1]; rail_len += (p - q).length
            for hz in (0.78, 0.25):
                add_rod('street_rail', tuple(q + Vector((0, 0, hz))), tuple(p + Vector((0, 0, hz))), 0.024, 6)
    # vertical balusters every 0.25 m between the rails
    for a, b in zip(dense, dense[1:]):
        k = max(1, int((b - a).length / 0.25))
        for i in range(1, k):
            q = a.lerp(b, i / k)
            add_rod('street_rail', tuple(q + Vector((0, 0, 0.25))), tuple(q + Vector((0, 0, 0.78))), 0.009, 4)

# ---------------------------------------------------------------- objects and export
for name, b in BM.items():
    if not b.verts:
        continue
    me = bpy.data.meshes.new(name); b.to_mesh(me); b.free()
    me.materials.append(MATS[name])
    ob = bpy.data.objects.new(name, me); bpy.context.collection.objects.link(ob)

stats = {'version': 2, 'blender': bpy.app.version_string, 'datum_tp_m': DATUM, 'features': records, 'lights': LIGHTS,
         'rail_length_m': round(rail_len, 1), 'unresolved': D['unresolved'], 'missing_sources': D['missing_sources'], 'objects': {}}
for ob in bpy.context.scene.objects:
    if ob.type == 'MESH':
        ob.data.calc_loop_triangles()
        stats['objects'][ob.name] = {'triangles': len(ob.data.loop_triangles), 'vertices': len(ob.data.vertices)}
stats['triangles'] = sum(m['triangles'] for m in stats['objects'].values())
Path(output).parent.mkdir(parents=True, exist_ok=True)
bpy.ops.export_scene.gltf(filepath=output, export_format='GLB', export_yup=True, export_cameras=False, export_lights=False)
Path(stats_path).write_text(json.dumps(stats, ensure_ascii=False, indent=2) + '\n')
print('STREET v2', len(records), 'items,', stats['triangles'], 'triangles,', round(rail_len), 'm railing')
