# Gate C0: road-surface elevation around the crossing from PLATEAU tran (road) GML, compared with each building's 0 m.
#   python3 tools/core/terrain_probe.py <53393596_tran.gml> <out.json>
# PLATEAU posList is "lat lon h" (h = T.P. metres). Elevation at a point = inverse-distance mean of the 12 nearest
# road vertices; the radius of those 12 is reported so sparse areas are visible. Read-only: nothing is moved.
import re, math, json, sys
import numpy as np

gml, out_path = sys.argv[1:3]
lat0, lon0 = 35.6595, 139.7005
kx = math.cos(math.radians(lat0)) * 111320.0; ky = 110574.0
pts = []
for m in re.finditer(r'<gml:posList[^>]*>([^<]+)</gml:posList>', open(gml, encoding='utf-8').read()):
    v = list(map(float, m.group(1).split()))
    for i in range(0, len(v) - 2, 3):
        x = (v[i + 1] - lon0) * kx; y = (v[i] - lat0) * ky; h = v[i + 2]
        if abs(x) < 120 and abs(y) < 120 and h > 5: pts.append((x, y, h))
P = np.array(pts)

def z_at(px, py, k=12):
    d = np.hypot(P[:, 0] - px, P[:, 1] - py); i = np.argsort(d)[:k]; w = 1 / np.maximum(d[i], .5) ** 2
    return float((P[i, 2] * w).sum() / w.sum()), float(d[i].max())

# probe points (Blender X=east, Y=north, m from the origin); building corners from each asset's PLATEAU LOD2 file
PROBES = {
    'C01_crossing_centre': (6.5, -2.0), 'C02_Hachiko': (11.6, -47.0), 'C03_QFRONT_front': (-14.0, 25.5),
    'C04_MAGNET_front': (34.0, 7.5), 'C05_Center_gai': (-25.0, 29.2),
    'QFRONT_front_kerb': (-7.7, 22.0), 'QFRONT_arc_mid': (-7.67, 29.08),
    'MAGNET_south_kerb': (41.0, 6.0), 'MAGNET_SW_corner': (30.0, 12.0),
    'MAGNET_ground_SE_vertex_(49.2,9.9)': (49.2, 9.9), 'MAGNET_ground_SW_vertex_(33.6,11.3)': (33.6, 11.3),
}
out = {}
for name, (px, py) in PROBES.items():
    z, r = z_at(px, py); out[name] = {'x': px, 'y': py, 'road_elev_m': round(z, 3), 'nearest_k_radius_m': round(r, 1)}
    print(f'{name:38s} road {z:7.3f} m (12 nearest within {r:4.1f} m)')
# spread of the road surface within 50 m of the crossing centre (grid every 5 m where vertices are within 6 m)
g = []
for gx in np.arange(-43.5, 57, 5):
    for gy in np.arange(-52, 48, 5):
        if math.hypot(gx - 6.5, gy + 2.0) <= 50:
            z, r = z_at(gx, gy)
            if r <= 6: g.append(z)
out['_core_50m_grid'] = {'n': len(g), 'min': round(min(g), 3), 'max': round(max(g), 3), 'median': round(float(np.median(g)), 3)}
out['_source'] = {'file': gml.split('/')[-1], 'vertices_within_120m': len(P), 'elev_range': [round(float(P[:, 2].min()), 3), round(float(P[:, 2].max()), 3)]}
print('core grid', out['_core_50m_grid'], out['_source'])
json.dump(out, open(out_path, 'w'), indent=1)
