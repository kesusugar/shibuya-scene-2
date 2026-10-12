# C2a: prepares the Core ground from PLATEAU 2025 road surfaces, OSM/orthophoto crosswalks and PLATEAU footprints.
#   python3 prepare_ground.py <plateau_core.json> <crosswalks_measured.json> <out ground_input.json> [radius_m=150]
# plateau_core.json comes from tools/core/plateau_core.py (PLATEAU 2025 Shibuya, tile 53393596).
# Output (plan metres X east / Y north, heights T.P.):
#   surfaces: road / intersection / sidewalk / island polygons straight from PLATEAU (LOD3; LOD2 only where no LOD3
#             covers the spot), with their 3D vertices
#   crosswalks: zebra bars (0.45 m bar / 0.45 m gap, parallel to the walking direction) clipped to the carriageway
#   landings: crosswalk band ends, where the kerb drops to the low (barrier-free) height
#   fill: 2D triangles for ground that PLATEAU's road data leaves out (forecourts, plazas), minus building footprints
# Every value that is not measured is a named parameter in PARAMS and is written to the output.
import json, sys, math
import numpy as np
from shapely.geometry import Polygon, LineString, Point, MultiPolygon, GeometryCollection
from shapely.ops import unary_union, triangulate
from shapely import segmentize

pl_path, cw_path, out = sys.argv[1:4]; R = float(sys.argv[4]) if len(sys.argv) > 4 else 150.0
CX, CY = 6.5, -2.0
PARAMS = {
    'radius_m': R,
    'kerb_height_m': 0.15,          # 道路構造令 standard kerb; PLATEAU LOD3 has no kerb step (checked: 2,125 shared vertices, max 0.008 m)
    'kerb_low_m': 0.02,             # barrier-free drop at crosswalk landings (移動等円滑化 guideline value)
    'landing_flat_m': 1.0,          # low kerb within this distance of a crosswalk band
    'landing_ramp_m': 1.5,          # then ramps back to the full kerb over this distance
    'zebra_bar_m': 0.45, 'zebra_gap_m': 0.45,   # Japanese road-marking standard values; to be checked on photos
    'default_crosswalk_width_m': 4.0,           # only for OSM-marked crosswalks the orthophoto could not measure
    'fill_grid_m': 3.0,
}
P = json.load(open(pl_path)); CW = json.load(open(cw_path))
focus = Point(CX, CY).buffer(R, 64)
CLASS = {'車道部': 'road', '車道交差部': 'intersection', '歩道部': 'sidewalk', '島': 'island'}

def poly(r):
    try:
        p = Polygon([(q[0], q[1]) for q in r])
        return p if p.is_valid else p.buffer(0)
    except Exception:
        return Polygon()
# LOD3 first; a LOD2 surface is kept only where it adds area that LOD3 does not cover
lod3 = [t for t in P['traffic_areas'] if t['lod'] == 'lod3']; lod2 = [t for t in P['traffic_areas'] if t['lod'] == 'lod2']
cover3 = unary_union([poly(r) for t in lod3 for r in t['rings']])
surfaces = []; dropped_lod2 = 0
for t in lod3 + lod2:
    cls = CLASS.get(t['function_ja'])
    if not cls: continue
    for r in t['rings']:
        g = poly(r)
        if g.is_empty or not g.intersects(focus): continue
        if t['lod'] == 'lod2':
            if g.area == 0 or g.intersection(cover3).area / g.area > 0.2: dropped_lod2 += 1; continue
        surfaces.append({'class': cls, 'lod': t['lod'], 'ring': r[:-1] if r[0] == r[-1] else r})
road_union = unary_union([poly(s['ring']) for s in surfaces if s['class'] in ('road', 'intersection')])
walk_union = unary_union([poly(s['ring']) for s in surfaces if s['class'] in ('sidewalk', 'island')])
paved = unary_union([road_union, walk_union])

# crosswalk bands: OSM-marked ways only; measured width and centre line where the orthophoto allowed it
bands = []
for c in CW['crosswalks']:
    marked = c.get('osm_markings') not in (None, 'no') and c.get('osm_crossing') != 'unmarked'
    if not marked and c.get('osm_crossing') == 'traffic_signals' and c.get('osm_markings') is None: marked = True
    if not marked: continue
    line = LineString(c.get('points_measured') or c['points'])
    if not line.intersects(focus): continue
    w = c['width_m'] if c['status'] == 'measured' else PARAMS['default_crosswalk_width_m']
    # extend the line 3 m each way so the band reaches the kerb; the road clip trims it back
    (x0, y0), (x1, y1) = line.coords[0], line.coords[1]; L = math.hypot(x1 - x0, y1 - y0) or 1
    (a0, b0), (a1, b1) = line.coords[-2], line.coords[-1]; M = math.hypot(a1 - a0, b1 - b0) or 1
    ext = LineString([(x0 - (x1 - x0) / L * 3, y0 - (y1 - y0) / L * 3)] + list(line.coords)[1:-1] + [(a1 + (a1 - a0) / M * 3, b1 + (b1 - b0) / M * 3)])
    band = ext.buffer(w / 2, cap_style='flat', join_style='mitre')
    bands.append({'id': c['id'], 'width_m': w, 'width_source': 'orthophoto' if c['status'] == 'measured' else 'default (not measured)',
                  'line': ext, 'band': band, 'area_on_road': band.intersection(road_union).area})
# two OSM ways that describe the same painted band: keep the one with more band on the road
bands.sort(key=lambda b: -b['area_on_road']); kept = []
for b in bands:
    if any(b['band'].intersection(k['band']).area > 0.5 * min(b['band'].area, k['band'].area) for k in kept): b['dropped'] = 'duplicate of ' + next(k['id'] for k in kept if b['band'].intersection(k['band']).area > 0.5 * min(b['band'].area, k['band'].area)); continue
    kept.append(b)
def parts(g):
    if g.is_empty: return []
    if isinstance(g, Polygon): return [g]
    if isinstance(g, (MultiPolygon, GeometryCollection)): return [q for x in g.geoms for q in parts(x)]
    return []
crosswalks = []
bar, gap = PARAMS['zebra_bar_m'], PARAMS['zebra_gap_m']
for b in kept:
    line = b['line']; w = b['width_m']; n = int((w + gap) // (bar + gap)); start = -((n * (bar + gap) - gap) / 2) + bar / 2
    bars = []
    for i in range(n):
        o = start + i * (bar + gap)
        off = line.offset_curve(o, join_style='mitre') if abs(o) > 1e-6 else line
        g = off.buffer(bar / 2, cap_style='flat', join_style='mitre').intersection(road_union).difference(walk_union)
        for p in parts(g):
            if p.area < 0.05: continue
            p = segmentize(p, 1.0)
            bars.append([list(map(lambda v: round(v, 3), xy)) for xy in list(p.exterior.coords)[:-1]])
    crosswalks.append({'id': b['id'], 'width_m': w, 'width_source': b['width_source'], 'bars': bars,
                       'band': [list(map(lambda v: round(v, 3), xy)) for xy in list(b['band'].exterior.coords)[:-1]]})
# ground PLATEAU's road data leaves out: inside the focus circle, not paved, not under a building or bridge pier
foot = unary_union([poly(s['ring']) for bl in P['buildings'] for s in bl['surfaces'] if s['kind'] == 'GroundSurface'])
gaps = focus.difference(paved).difference(foot).buffer(-0.05).buffer(0.05)
fill = []
G = PARAMS['fill_grid_m']
for p in parts(gaps):
    if p.area < 1.0: continue
    p = segmentize(p, G)
    xs0, ys0, xs1, ys1 = p.bounds
    pts = [Point(x, y) for x in np.arange(xs0, xs1, G) for y in np.arange(ys0, ys1, G) if p.contains(Point(x, y))]
    cloud = unary_union([p.boundary] + pts) if pts else p.boundary
    for tri in triangulate(cloud):
        if p.contains(tri.representative_point()) and tri.area > 1e-3:
            fill.append([list(map(lambda v: round(v, 3), xy)) for xy in list(tri.exterior.coords)[:-1]])
stats = {'surfaces': {k: sum(1 for s in surfaces if s['class'] == k) for k in ('road', 'intersection', 'sidewalk', 'island')},
         'lod3_surfaces': sum(1 for s in surfaces if s['lod'] == 'lod3'), 'lod2_surfaces_kept': sum(1 for s in surfaces if s['lod'] == 'lod2'), 'lod2_surfaces_dropped_overlap': dropped_lod2,
         'paved_area_m2': round(paved.intersection(focus).area), 'fill_area_m2': round(sum(Polygon(t).area for t in fill)), 'focus_area_m2': round(focus.area),
         'core50_fill_share': round(focus.intersection(Point(CX, CY).buffer(50, 64)).difference(paved).difference(foot).area / Point(CX, CY).buffer(50, 64).area, 4),
         'crosswalks_kept': len(crosswalks), 'crosswalks_dropped': [{'id': b['id'], 'why': b['dropped']} for b in bands if 'dropped' in b],
         'zebra_bars': sum(len(c['bars']) for c in crosswalks)}
json.dump({'params': PARAMS, 'stats': stats, 'source': {'plateau': P['_meta']['source'], 'crosswalks': CW['source'], 'osm': CW['osm']},
           'surfaces': surfaces, 'crosswalks': crosswalks, 'landings': [c['band'] for c in crosswalks], 'fill': fill}, open(out, 'w'))
print(json.dumps(stats, ensure_ascii=False, indent=1))
