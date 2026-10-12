# Measures each marked crosswalk's width and centre line on the GSI orthophoto (seamless aerial photo, zoom 18,
# 0.485 m/px), starting from the OSM crossing way. The photo is a measurement reference only, never a texture.
#   python3 measure_crosswalks.py <old shibuya-scene-data.json> <gsi_tile_dir> <out.json> [debug.png]
# Method: brightness profiles across the way (-10..+10 m, 0.25 m steps) at 1 m stations, averaged along the way and
# smoothed over 1 m (zebra bars are about 0.45 m and only half resolved). The band is the contiguous run around the
# brightest offset where the profile is above base + 50 % of (peak - base); base = 20th percentile of the profile.
# Width = band extent; the OSM line is moved sideways to the band centre. Low contrast -> "not measured".
import json, math, sys, os
from PIL import Image, ImageDraw
import numpy as np

data_path, tiles, out = sys.argv[1:4]; dbg = sys.argv[4] if len(sys.argv) > 4 else None
Z = 18; N = 2 ** Z; T = 256
lat0, lon0 = 35.6595, 139.7005; kx = math.cos(math.radians(lat0)) * 111320.0; ky = 110574.0
CX, CY = 6.5, -2.0
def tile_xy(x, y):
    lon = lon0 + x / kx; lat = lat0 + y / ky
    return (lon + 180) / 360 * N, (1 - math.log(math.tan(math.radians(lat)) + 1 / math.cos(math.radians(lat))) / math.pi) / 2 * N
cache = {}
def tile(ix, iy):
    if (ix, iy) not in cache:
        p = os.path.join(tiles, f's18_{ix}_{iy}.jpg')
        cache[(ix, iy)] = np.asarray(Image.open(p).convert('L'), dtype=np.float32) if os.path.exists(p) else None
    return cache[(ix, iy)]
def sample(x, y):
    tx, ty = tile_xy(x, y); ix, iy = int(tx), int(ty); a = tile(ix, iy)
    if a is None: return np.nan
    px, py = (tx - ix) * T - .5, (ty - iy) * T - .5
    x0, y0 = int(math.floor(px)), int(math.floor(py)); fx, fy = px - x0, py - y0
    x0 = min(max(x0, 0), T - 2); y0 = min(max(y0, 0), T - 2)
    return (a[y0, x0] * (1 - fx) * (1 - fy) + a[y0, x0 + 1] * fx * (1 - fy) + a[y0 + 1, x0] * (1 - fx) * fy + a[y0 + 1, x0 + 1] * fx * fy)

D = json.load(open(data_path)); res = []
OFF = np.arange(-10, 10.001, 0.25)
for w in D['footways']:
    t = w['tags']
    if t.get('footway') != 'crossing': continue
    pts = [(p[0], -p[1]) for p in w['points']]
    if min(math.hypot(x - CX, y - CY) for x, y in pts) > 150: continue
    marked = t.get('crossing:markings') not in ('no',) and t.get('crossing') != 'unmarked'
    prof = []; stations = []
    for (x1, y1), (x2, y2) in zip(pts, pts[1:]):
        L = math.hypot(x2 - x1, y2 - y1)
        if L < 0.5: continue
        ux, uy = (x2 - x1) / L, (y2 - y1) / L; nx, ny = -uy, ux
        for s in np.arange(1.0, max(L - 1.0, 1.01), 1.0):
            px, py = x1 + ux * s, y1 + uy * s
            prof.append([sample(px + nx * o, py + ny * o) for o in OFF]); stations.append((px, py, nx, ny))
    r = {'id': w['id'], 'osm_markings': t.get('crossing:markings'), 'osm_crossing': t.get('crossing'), 'points': [list(map(lambda v: round(v, 3), p)) for p in pts],
         'length_m': round(sum(math.hypot(b[0] - a[0], b[1] - a[1]) for a, b in zip(pts, pts[1:])), 2)}
    if not prof:
        r.update(status='not measured (too short)'); res.append(r); continue
    P = np.nanmean(np.array(prof), axis=0)
    k = np.ones(4) / 4; Ps = np.convolve(P, k, mode='same')
    base = np.nanpercentile(Ps, 20); i0 = int(np.nanargmax(Ps[20:61]) + 20)     # peak within +-5 m of the OSM line
    peak = Ps[i0]; thr = base + 0.5 * (peak - base)
    lo = i0
    while lo > 0 and Ps[lo - 1] > thr: lo -= 1
    hi = i0
    while hi < len(Ps) - 1 and Ps[hi + 1] > thr: hi += 1
    width = (hi - lo + 1) * 0.25; centre = (OFF[lo] + OFF[hi]) / 2; contrast = float(peak - base)
    ok = contrast >= 25 and 2.0 <= width <= 14 and lo > 0 and hi < len(Ps) - 1
    r.update(status='measured' if ok else 'not measured (low contrast or open band)', marked_osm=marked, width_m=round(width, 2), centre_offset_m=round(float(centre), 2),
             contrast=round(contrast, 1), profile_base=round(float(base), 1), profile_peak=round(float(peak), 1))
    if ok:   # shift the line to the band centre (offset is along the left normal of each segment)
        sh = []
        for (x1, y1), (x2, y2) in zip(pts, pts[1:]):
            L = math.hypot(x2 - x1, y2 - y1) or 1; nx, ny = -(y2 - y1) / L, (x2 - x1) / L
            sh.append((nx * centre, ny * centre))
        sh = [sh[0]] + [((a[0] + b[0]) / 2, (a[1] + b[1]) / 2) for a, b in zip(sh, sh[1:])] + [sh[-1]]
        r['points_measured'] = [[round(x + dx, 3), round(y + dy, 3)] for (x, y), (dx, dy) in zip(pts, sh)]
    res.append(r)
json.dump({'source': 'GSI seamless aerial photo (国土地理院 シームレス空中写真) zoom 18; capture year not stated per tile', 'licence': '国土地理院コンテンツ利用規約 (CC BY 4.0 compatible); measurement only, not redistributed as texture',
           'osm': 'old project data, OSM fetched 2026-09-08', 'crosswalks': res}, open(out, 'w'), ensure_ascii=False, indent=1)
for r in res: print(r['id'], r['status'], r.get('width_m'), r.get('centre_offset_m'), r.get('contrast'), r['length_m'], r['osm_crossing'], r['osm_markings'])
if dbg:
    # 4 x 4 tiles around the crossing, scaled 3x, measured bands drawn as outlines
    xs, ys = tile_xy(CX, CY); X0, Y0 = int(xs) - 1, int(ys) - 1; SC = 3
    mos = Image.new('RGB', (3 * T, 3 * T))
    for i in range(3):
        for j in range(3):
            p = os.path.join(tiles, f's18_{X0 + i}_{Y0 + j}.jpg')
            if os.path.exists(p): mos.paste(Image.open(p), (i * T, j * T))
    big = mos.resize((3 * T * SC, 3 * T * SC), Image.LANCZOS); d = ImageDraw.Draw(big)
    def px(x, y): tx, ty = tile_xy(x, y); return ((tx - X0) * T * SC, (ty - Y0) * T * SC)
    for r in res:
        line = r.get('points_measured') or r['points']
        col = (0, 255, 120) if r['status'] == 'measured' else (255, 60, 60)
        d.line([px(*p) for p in r['points']], fill=(255, 0, 255), width=1)
        if r['status'] == 'measured':
            hw = r['width_m'] / 2
            for (x1, y1), (x2, y2) in zip(line, line[1:]):
                L = math.hypot(x2 - x1, y2 - y1) or 1; nx, ny = -(y2 - y1) / L * hw, (x2 - x1) / L * hw
                d.polygon([px(x1 + nx, y1 + ny), px(x2 + nx, y2 + ny), px(x2 - nx, y2 - ny), px(x1 - nx, y1 - ny)], outline=col)
    cx, cy = px(CX, CY)
    big.crop((int(cx - 450), int(cy - 450), int(cx + 450), int(cy + 450))).save(dbg)
