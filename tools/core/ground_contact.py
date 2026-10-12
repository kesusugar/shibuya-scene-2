# Gate C0 supplement: where does each finished/in-progress building meet the PLATEAU pavement?
#   python3 tools/core/ground_contact.py <plateau_core.json> <out.json>
# For every vertex of a building's PLATEAU GroundSurface, find the nearest traffic-area surface within 6 m (outward
# normal first, then 16 directions at 1-6 m) and compare heights. The traffic-area height at a point is the plane of the polygon that contains it
# (LOD3 preferred over LOD2). Output per building: building ground (T.P.), pavement at each corner, differences.
import json, sys, math
P = json.load(open(sys.argv[1])); out = sys.argv[2]
TARGETS = {'QFRONT': 'bldg_5f7ff4f3', 'MAGNET': 'bldg_d47d8aa9', 'SEIBU_A': 'bldg_46f3cd1c'}
def inside(x, y, ring):
    c = False
    for i in range(len(ring)):
        x1, y1 = ring[i][0], ring[i][1]; x2, y2 = ring[i - 1][0], ring[i - 1][1]
        if (y1 > y) != (y2 > y) and x < (x2 - x1) * (y - y1) / (y2 - y1) + x1: c = not c
    return c
def plane_z(ring, x, y):
    # least-squares plane through the ring
    n = len(ring); sx = sum(p[0] for p in ring) / n; sy = sum(p[1] for p in ring) / n; sz = sum(p[2] for p in ring) / n
    a11 = sum((p[0] - sx) ** 2 for p in ring); a12 = sum((p[0] - sx) * (p[1] - sy) for p in ring); a22 = sum((p[1] - sy) ** 2 for p in ring)
    b1 = sum((p[0] - sx) * (p[2] - sz) for p in ring); b2 = sum((p[1] - sy) * (p[2] - sz) for p in ring)
    det = a11 * a22 - a12 * a12
    if abs(det) < 1e-9: return sz
    gx = (b1 * a22 - b2 * a12) / det; gy = (a11 * b2 - a12 * b1) / det
    return sz + gx * (x - sx) + gy * (y - sy)
TA = sorted(P['traffic_areas'], key=lambda t: t['lod'] != 'lod3')
def pave(x, y):
    for t in TA:
        for r in t['rings']:
            if inside(x, y, r): return round(plane_z(r, x, y), 3), t['function_ja'], t['lod']
    return None, None, None
res = {}
for b in P['buildings']:
    name = next((k for k, v in TARGETS.items() if b['gml_id'].startswith(v)), None)
    if name is None: continue
    g = [s['ring'] for s in b['surfaces'] if s['kind'] == 'GroundSurface']
    ring = max(g, key=len)[:-1] if g[0][0] == g[0][-1] else max(g, key=len)
    area2 = sum(ring[i][0] * ring[i - 1][1] - ring[i - 1][0] * ring[i][1] for i in range(len(ring)))   # sign = orientation
    rows = []
    for i, p in enumerate(ring):
        a, c = ring[i - 1], ring[(i + 1) % len(ring)]
        # outward normal: average of the two edge normals (sign from orientation)
        nx = ny = 0.0
        for (x1, y1), (x2, y2) in (((a[0], a[1]), (p[0], p[1])), ((p[0], p[1]), (c[0], c[1]))):
            ex, ey = x2 - x1, y2 - y1; L = math.hypot(ex, ey) or 1
            s = 1 if area2 > 0 else -1
            nx += s * ey / L; ny += -s * ex / L
        # nearest pavement around the corner: rings of 16 directions at 1, 2, 3, 4, 6 m (outward first)
        L = math.hypot(nx, ny) or 1; z = fn = lod = None; dist = None
        for rad in (1.0, 2.0, 3.0, 4.0, 6.0):
            dirs = [(nx / L, ny / L)] + [(math.cos(k * math.pi / 8), math.sin(k * math.pi / 8)) for k in range(16)]
            for ux, uy in dirs:
                z, fn, lod = pave(p[0] + rad * ux, p[1] + rad * uy)
                if z is not None: dist = rad; break
            if z is not None: break
        rows.append({'x': p[0], 'y': p[1], 'building_ground_tp': p[2], 'pavement_tp': z, 'pavement_kind': fn, 'lod': lod, 'search_radius_m': dist,
                     'pavement_minus_building': round(z - p[2], 3) if z is not None else None})
    res[name] = {'gml_id': b['gml_id'], 'ground_min_tp': min(p[2] for p in ring), 'ground_max_tp': max(p[2] for p in ring), 'corners': rows}
json.dump(res, open(out, 'w'), ensure_ascii=False, indent=1)
for k, v in res.items():
    d = [r['pavement_minus_building'] for r in v['corners'] if r['pavement_minus_building'] is not None]
    print(k, 'ground', v['ground_min_tp'], '-', v['ground_max_tp'], '| corners with pavement', len(d), '/', len(v['corners']),
          '| pavement - building: min %.3f median %.3f max %.3f' % (min(d), sorted(d)[len(d) // 2], max(d)) if d else '')
    for r in v['corners']: print('   ', round(r['x'], 1), round(r['y'], 1), r['building_ground_tp'], r['pavement_tp'], r['pavement_kind'], r['lod'], r['search_radius_m'], r['pavement_minus_building'])
