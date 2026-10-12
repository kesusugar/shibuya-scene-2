"""C2b layout: rule-derived positions for signals, pedestrian signals and kerb railings (plus photo-projected lamps).

python3 street_layout.py ground_input.json street_input.json furniture_register.csv street_layout.json

No 2025 survey of the Core's poles or railings exists in the sources we may use (PLATEAU city furniture does not
cover the Core; OSM has only four road signal nodes). Instead of leaving the crossing empty, every item here is
placed by a written rule from data that *is* surveyed (PLATEAU LOD3 kerbs, orthophoto crosswalks, OSM signal
nodes) and is flagged `placement: rule` in the output. A photo or survey that contradicts a rule wins; change the
rule or add an override, never hand-nudge one pole to fit one photograph.

Rules (Japanese practice; see docs/core/CODEX_C2B_REVIEW.md for the reasoning and the gaps):
  R1 pedestrian signal  — one pole at each end of every Core crosswalk, 0.6 m behind the kerb, 0.5 m outside the
                          crosswalk edge on the side nearer the crossing centre; the head faces the far end.
  R2 vehicle signal     — one mast-arm pole per OSM approach node, at the crosswalk end on the driver's left
                          (Japan drives on the left); the arm reaches over the approach lanes and the head faces
                          the oncoming driver.  The pedestrian head of R1 at that corner shares the mast pole.
  R3 kerb railing       — 横断防止柵 (H 0.8 m) along PLATEAU kerb lines inside the Core, 0.35 m behind the kerb,
                          with openings of 1.5 m beyond each crosswalk edge, 1 m around entrances and trees.
  R4 lamps / signs      — only the photo-projected points P01–P04 (Codex C2b, Stream 2025); not invented.
"""
import csv
import json
import math
import sys

from shapely.geometry import LineString, MultiLineString, Point, Polygon
from shapely.ops import linemerge, unary_union

ground_path, street_path, register_path, out_path = sys.argv[1:5]
G = json.load(open(ground_path))
S = json.load(open(street_path))
CENTRE = (6.5, -2.0)
CORE_R = 52.0                    # assets must stay inside 55 m of the crossing centre (tests/street.test.ts)
KERB_BACK = 0.6                  # R1/R2 pole offset behind the kerb
RAIL_BACK = 0.35


def near(ring, r=80):
    return any(math.hypot(x - CENTRE[0], y - CENTRE[1]) < r for x, y, *_ in ring)


def poly(ring):
    p = Polygon([(x, y) for x, y, *_ in ring])
    return p if p.is_valid else p.buffer(0)


walk = unary_union([poly(s['ring']) for s in G['surfaces'] if s['class'] in ('sidewalk', 'island') and near(s['ring'])]).buffer(0.05).buffer(-0.05)
road = unary_union([poly(s['ring']) for s in G['surfaces'] if s['class'] in ('road', 'intersection') and near(s['ring'])]).buffer(0.05).buffer(-0.05)
kerb = walk.boundary.intersection(road.buffer(0.3))


def unit(v):
    n = math.hypot(*v)
    return (v[0] / n, v[1] / n)


def into_walk(p, normal_guess, back):
    """Point `back` metres onto the pavement from kerb point p (tries both sides of the given direction)."""
    for s in (1, -1):
        q = (p[0] + normal_guess[0] * back * s, p[1] + normal_guess[1] * back * s)
        if walk.contains(Point(q)):
            return q
    return None


crosswalks = []
for c in G['crosswalks']:
    bars = c['bars']
    if not bars:
        continue
    # bars are closed stripe outlines; stripes run in the walking direction, so the longest side of a stripe's
    # rotated bounding box is the crosswalk axis and the extent of all stripes along it gives the two ends
    rect = list(Polygon(bars[len(bars) // 2]).buffer(0).minimum_rotated_rectangle.exterior.coords)
    e0, e1 = (rect[1][0] - rect[0][0], rect[1][1] - rect[0][1]), (rect[2][0] - rect[1][0], rect[2][1] - rect[1][1])
    ax = unit(max(e0, e1, key=lambda e: math.hypot(*e)))
    pts = [q for bar in bars for q in bar]
    t = [q[0] * ax[0] + q[1] * ax[1] for q in pts]
    n = [-q[0] * ax[1] + q[1] * ax[0] for q in pts]
    nc = (max(n) + min(n)) / 2
    a = (ax[0] * min(t) - ax[1] * nc, ax[1] * min(t) + ax[0] * nc)
    b = (ax[0] * max(t) - ax[1] * nc, ax[1] * max(t) + ax[0] * nc)
    m = ((a[0] + b[0]) / 2, (a[1] + b[1]) / 2)
    if math.hypot(m[0] - CENTRE[0], m[1] - CENTRE[1]) > 40:
        continue
    axis = unit((b[0] - a[0], b[1] - a[1]))
    across = (-axis[1], axis[0])
    crosswalks.append({'id': c['id'], 'a': a, 'b': b, 'mid': m, 'axis': axis, 'across': across, 'width': c['width_m'],
                       'band': Polygon(c['band']).buffer(0)})

items = []


def kerb_end(cw, end):
    """Kerb point where the crosswalk centre line meets the pavement, walking outwards from the given end."""
    p = cw[end]
    d = cw['axis'] if end == 'b' else (-cw['axis'][0], -cw['axis'][1])
    for k in range(0, 80):
        q = (p[0] + d[0] * (k * 0.25 - 4), p[1] + d[1] * (k * 0.25 - 4))
        if walk.contains(Point(q)):
            return q, d
    return None, d


# R1 pedestrian signals
for cw in crosswalks:
    for end, other in (('a', 'b'), ('b', 'a')):
        k, d = kerb_end(cw, end)
        if k is None:
            continue
        side = cw['across'] if ((k[0] + cw['across'][0] - CENTRE[0]) ** 2 + (k[1] + cw['across'][1] - CENTRE[1]) ** 2
                                < (k[0] - cw['across'][0] - CENTRE[0]) ** 2 + (k[1] - cw['across'][1] - CENTRE[1]) ** 2) else (-cw['across'][0], -cw['across'][1])
        off = cw['width'] / 2 + 0.5
        p = (k[0] + d[0] * KERB_BACK + side[0] * off, k[1] + d[1] * KERB_BACK + side[1] * off)
        if not walk.contains(Point(p)):
            p = (k[0] + d[0] * KERB_BACK, k[1] + d[1] * KERB_BACK)   # narrow island: centre line, behind the kerb
        face = cw[other]
        items.append({'id': f"PED_{cw['id'].split('/')[1]}_{end}", 'kind': 'ped_signal', 'xy': [round(p[0], 3), round(p[1], 3)],
                      'facing': list(unit((face[0] - p[0], face[1] - p[1]))), 'crosswalk': cw['id'], 'placement': 'rule R1'})

# R2 vehicle signals: one per OSM approach node (S['unresolved'] keeps the four nodes Codex left unresolved)
for node in [u for u in S['unresolved'] if u['kind'] == 'signal']:
    n = node['point']
    drive = unit((CENTRE[0] - n[0], CENTRE[1] - n[1]))
    left = (-drive[1], drive[0])
    cw = min(crosswalks, key=lambda c: Point(n).distance(LineString([c['a'], c['b']])))
    ends = sorted(('a', 'b'), key=lambda e: -((cw[e][0] - cw['mid'][0]) * left[0] + (cw[e][1] - cw['mid'][1]) * left[1]))
    k, d = kerb_end(cw, ends[0])
    # the mast stands at the R1 pedestrian pole of that corner when there is one (shared pole), else behind the kerb
    ped = next((i for i in items if i['kind'] == 'ped_signal' and i['crosswalk'] == cw['id'] and i['id'].endswith('_' + ends[0])), None)
    p = tuple(ped['xy']) if ped else (k[0] + d[0] * KERB_BACK, k[1] + d[1] * KERB_BACK)
    if ped:
        ped['shared_with'] = 'VEH_' + node['id'].split('/')[1]
    # the arm reaches over the approach (the driver's left half of the road, i.e. towards the road centre line)
    road_half = math.hypot(cw['b'][0] - cw['a'][0], cw['b'][1] - cw['a'][1]) / 2
    arm = min(max(road_half * 0.75, 3.0), 9.0)
    arm_dir = (-left[0], -left[1])
    items.append({'id': 'VEH_' + node['id'].split('/')[1], 'kind': 'vehicle_signal', 'xy': [round(p[0], 3), round(p[1], 3)],
                  'arm_dir': [round(arm_dir[0], 4), round(arm_dir[1], 4)], 'arm_m': round(arm, 2),
                  'facing': [round(-drive[0], 4), round(-drive[1], 4)], 'osm_node': node['id'], 'crosswalk': cw['id'], 'placement': 'rule R2'})

# R4 photo-projected lamps and signs (Codex C2b register)
for r in csv.DictReader(open(register_path)):
    if r['kind'] in ('lamp', 'lamp_signal', 'sign') and r['x_m']:
        items.append({'id': r['id'], 'kind': 'lamp' if r['kind'].startswith('lamp') else 'sign_pair', 'xy': [float(r['x_m']), float(r['y_m'])],
                      'placement': 'photo projection (Stream 2025, Codex C2b)', 'uncertainty_m': float(r['camera_variant_difference_m'] or 0)})

# R3 kerb railings
keepout = [cw['band'].buffer(1.5) for cw in crosswalks]
keepout += [Polygon(f['ring']).buffer(1.0) for f in S['features'] if f['kind'] == 'entrance']
keepout += [Point(f['point']).buffer(1.2) for f in S['features'] if f['kind'] == 'tree']
keepout += [Point(i['xy']).buffer(0.6) for i in items]
core = Point(CENTRE).buffer(CORE_R - 2)
lines = linemerge(kerb) if kerb.geom_type == 'MultiLineString' else kerb
rail_src = lines.intersection(core).difference(unary_union(keepout))
runs = []
for seg in getattr(rail_src, 'geoms', [rail_src]):
    if seg.geom_type != 'LineString' or seg.length < 2.5:
        continue
    seg = seg.simplify(0.15)
    pts = []
    for i, (x, y) in enumerate(seg.coords):
        j0, j1 = max(i - 1, 0), min(i + 1, len(seg.coords) - 1)
        t = unit((seg.coords[j1][0] - seg.coords[j0][0], seg.coords[j1][1] - seg.coords[j0][1]))
        q = into_walk((x, y), (-t[1], t[0]), RAIL_BACK)
        if q:
            pts.append([round(q[0], 3), round(q[1], 3)])
    if len(pts) >= 2 and LineString(pts).length >= 2.5:
        runs.append(pts)

out = {'rules': __doc__.split('Rules')[1].strip(), 'centre': CENTRE, 'core_radius_m': CORE_R, 'items': items,
       'rail_runs': runs, 'rail_length_m': round(sum(LineString(r).length for r in runs), 1),
       'kerb_length_in_core_m': round(lines.intersection(core).length, 1)}
json.dump(out, open(out_path, 'w'), ensure_ascii=False, indent=1)
from collections import Counter
print(Counter(i['kind'] for i in items), len(runs), 'rail runs', out['rail_length_m'], 'm of', out['kerb_length_in_core_m'])
