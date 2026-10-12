# C2a: where each finished building meets the built ground. Samples the Core ground GLB just outside every street-
# facing edge of the building's PLATEAU footprint and reports the lowest and highest finished-pavement height.
#   blender -b -P ground_anchor.py -- <ground_core.glb> <plateau_core.json> <out anchors.json>
# Rule (docs/core/C2A_PLAN.md, revised): the model's 0 m goes to the LOWEST finished pavement along its street
# frontage, so the base never floats; where the pavement is higher the base is buried by the difference. The roof
# then deviates from PLATEAU's absolute roof height by (anchor - PLATEAU ground); both numbers are reported.
import bpy, json, sys, math
from mathutils import Vector
from mathutils.bvhtree import BVHTree
import bmesh
argv = sys.argv[sys.argv.index('--') + 1:]
glb, pl_path, out = argv[:3]; DATUM = 15.0
bpy.ops.wm.read_factory_settings(use_empty=True)
bpy.ops.import_scene.gltf(filepath=glb)
# glTF import converts back to Blender Z-up plan axes; surfaces only (no kerb/skirt faces) carry the walking height
bm = bmesh.new(); kinds = {}
for ob in bpy.context.scene.objects:
    if ob.type != 'MESH' or not any(ob.name.startswith(p) for p in ('ground_road', 'ground_intersection', 'ground_sidewalk', 'ground_fill')): continue
    me = ob.evaluated_get(bpy.context.evaluated_depsgraph_get()).to_mesh(); me.transform(ob.matrix_world)
    n0 = len(bm.faces); bm.from_mesh(me); bm.faces.index_update()
    for f in list(bm.faces)[n0:]: kinds[f.index] = ob.name.split('.')[0]
bm.faces.ensure_lookup_table(); bvh = BVHTree.FromBMesh(bm)
def ground_at(x, y):
    loc, nor, idx, d = bvh.ray_cast(Vector((x, y, 50.0)), Vector((0, 0, -1)))
    if loc is None: return None, None
    return loc.z + DATUM, kinds.get(idx)
P = json.load(open(pl_path))
TARGETS = {'qfront': 'bldg_5f7ff4f3', 'magnet': 'bldg_d47d8aa9'}
res = {}
for b in P['buildings']:
    name = next((k for k, v in TARGETS.items() if b['gml_id'].startswith(v)), None)
    if not name: continue
    ring = max((s['ring'] for s in b['surfaces'] if s['kind'] == 'GroundSurface'), key=len)
    ring = ring[:-1] if ring[0] == ring[-1] else ring
    area2 = sum(ring[i][0] * ring[i - 1][1] - ring[i - 1][0] * ring[i][1] for i in range(len(ring)))
    s = -1 if area2 > 0 else 1   # area2 > 0 means clockwise; (dy, -dx) is outward for counter-clockwise
    samples = []
    for i in range(len(ring)):
        (x1, y1), (x2, y2) = ring[i - 1][:2], ring[i][:2]
        L = math.hypot(x2 - x1, y2 - y1)
        if L < 0.5: continue
        nx, ny = s * (y2 - y1) / L, -s * (x2 - x1) / L        # outward normal
        for k in range(1, int(L / 0.5)):
            t = k * 0.5 / L; px, py = x1 + (x2 - x1) * t + nx * 0.4, y1 + (y2 - y1) * t + ny * 0.4
            z, kind = ground_at(px, py)
            if z is not None and kind in ('ground_sidewalk', 'ground_road', 'ground_intersection', 'ground_fill'):   # any walking surface
                samples.append({'x': round(px, 2), 'y': round(py, 2), 'z_tp': round(z, 3), 'kind': kind, 'edge': i})
    zs = sorted(r['z_tp'] for r in samples)
    if not zs: continue
    lo = zs[0]; p5 = zs[max(0, int(0.05 * len(zs)) - 1)]
    res[name] = {'plateau_ground_tp': min(p[2] for p in ring), 'frontage_samples': len(samples), 'pavement_min_tp': lo, 'pavement_p05_tp': p5,
                 'pavement_median_tp': zs[len(zs) // 2], 'pavement_max_tp': zs[-1], 'anchor_tp': round(lo, 3),
                 'roof_deviation_vs_plateau_m': round(lo - min(p[2] for p in ring), 3), 'max_burial_m': round(zs[-1] - lo, 3),
                 'lowest_at': min(samples, key=lambda r: r['z_tp']),
                 'samples_by_kind': {k: sum(1 for r in samples if r['kind'] == k) for k in ('ground_sidewalk', 'ground_road', 'ground_intersection', 'ground_fill')},
                 'min_on_measured_pavement_tp': min((r['z_tp'] for r in samples if r['kind'] != 'ground_fill'), default=None)}
json.dump(res, open(out, 'w'), indent=1)
print('ANCHORS', json.dumps(res))
