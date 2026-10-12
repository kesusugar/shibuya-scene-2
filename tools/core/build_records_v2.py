# Gate C0 supplement: visibility records v2 - PLATEAU LOD2 surfaces instead of full-height prisms, plus the
# PLATEAU buildings that have no OSM way and the bridges/viaducts, all on one datum (z = T.P. - DATUM).
#   python3 tools/core/build_records_v2.py <buildings_c0.json> <plateau_core.json> <out.json>
# Record geometry is either 'polys' (3D rings, datum metres) or 'parts' + 'base_z' + 'height_used' (an extruded
# prism, kept for OSM buildings with no PLATEAU match inside the survey radius).
import json, sys, math
DATUM = 15.0                       # proposed common datum, docs/core/TERRAIN_ALIGNMENT.md (D1)
osm_path, pl_path, out = sys.argv[1:4]
B = json.load(open(osm_path)); P = json.load(open(pl_path))
pl = {b['gml_id']: b for b in P['buildings']}

# road surface elevation for prism bases (inverse-distance over the traffic-area vertices)
road = [p for t in P['traffic_areas'] for r in t['rings'] for p in r]
def road_z(x, y, k=12):
    d = sorted((math.hypot(p[0] - x, p[1] - y), p[2]) for p in road)[:k]
    w = [1 / max(a, .5) ** 2 for a, _ in d]; return sum(z * wi for (_, z), wi in zip(d, w)) / sum(w)
def area(ring):
    return 0.5 * abs(sum(ring[i][0] * ring[i - 1][1] - ring[i - 1][0] * ring[i][1] for i in range(len(ring))))
def to_datum(surfs):
    return [[[p[0], p[1], round(p[2] - DATUM, 3)] for p in s['ring']] for s in surfs]

# one PLATEAU solid per OSM building: if two OSM ways match the same PLATEAU building, the larger footprint keeps it
owner = {}
for b in B:
    pid = b['plateau_id']
    if pid in pl:
        a = sum(area(r) for r in b['parts'])
        if pid not in owner or a > owner[pid][1]: owner[pid] = (b['id'], a)
recs = []
for b in B:
    r = {k: b[k] for k in ('id', 'name', 'name_en', 'building', 'plateau_id', 'centroid', 'dist_from_crossing_m', 'old_status')}
    pid = b['plateau_id']
    if pid in pl and owner[pid][0] == b['id']:
        g = pl[pid]; r.update(kind='building', geometry='plateau_lod2', polys=to_datum(g['surfaces']), ground_tp=g['ground_tp'], top_tp=g['top_tp'],
                             height_used=round(g['top_tp'] - g['ground_tp'], 2), height_source='plateau_lod2_surfaces')
    else:
        base = road_z(*b['centroid']) - DATUM if road else 0.0
        r.update(kind='building', geometry='osm_prism', parts=b['parts'], base_z=round(base, 3), height_used=b['height_used'], height_source=b['height_source'],
                 note=('PLATEAU building shared with ' + owner[pid][0]) if pid in pl else ('no PLATEAU match within the survey radius' if pid else 'no PLATEAU match'))
    recs.append(r)
used = {pid for pid in owner}
for gid, g in pl.items():
    if gid in used: continue
    gs = [p for s in g['surfaces'] if s['kind'] == 'GroundSurface' for p in s['ring']] or [p for s in g['surfaces'] for p in s['ring']]
    cx = sum(p[0] for p in gs) / len(gs); cy = sum(p[1] for p in gs) / len(gs)
    recs.append({'id': 'plateau/' + gid, 'name': '', 'name_en': '', 'building': '', 'plateau_id': gid, 'centroid': [round(cx, 2), round(cy, 2)],
                 'dist_from_crossing_m': round(math.hypot(cx - 6.5, cy + 2.0), 1), 'old_status': 'not_in_old_data (no OSM way)',
                 'kind': 'building', 'geometry': 'plateau_lod2', 'polys': to_datum(g['surfaces']), 'ground_tp': g['ground_tp'], 'top_tp': g['top_tp'],
                 'height_used': round(g['top_tp'] - g['ground_tp'], 2), 'height_source': 'plateau_lod2_surfaces'})
for g in P['bridges']:
    pts = [p for s in g['surfaces'] for p in s['ring']]
    cx = sum(p[0] for p in pts) / len(pts); cy = sum(p[1] for p in pts) / len(pts)
    recs.append({'id': 'brid/' + g['gml_id'], 'name': g['name'] or '', 'name_en': '', 'building': 'bridge:' + (g['function_ja'] or ''), 'plateau_id': g['gml_id'],
                 'centroid': [round(cx, 2), round(cy, 2)], 'dist_from_crossing_m': round(min(math.hypot(p[0] - 6.5, p[1] + 2.0) for p in pts), 1),
                 'old_status': 'rails/footways layer only', 'kind': 'structure', 'geometry': 'plateau_lod2', 'polys': to_datum(g['surfaces']),
                 'ground_tp': g['z_min_tp'], 'top_tp': g['z_max_tp'], 'height_used': round(g['z_max_tp'] - g['z_min_tp'], 2), 'height_source': 'plateau_lod2_surfaces'})
json.dump(recs, open(out, 'w'))
from collections import Counter
print(len(recs), Counter((r['kind'], r['geometry']) for r in recs))
