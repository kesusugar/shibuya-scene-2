# Pinhole camera fit for MAGNET reference photos, and an overlay of the PLATEAU LOD2 edges on the photo.
#
#   python3 camfit.py fit  <landmarks.json> <out_fit.json>
#   python3 camfit.py draw <fit.json> <photo> <lod2.json> <out.jpg> [landmarks.json] [model_edges.json]
#
# landmarks.json: {"photo": "M002.jpg", "W": 1280, "H": 960, "init": {pos, yaw, pitch, roll, fpx},
#                  "points": [{"id": "tower_sw_top", "xyz": [x, y, z], "px": [u, v]}, ...]}
# Axes: Blender X=east, Y=north, Z=up (m above the south-west pavement, 14.561 m elevation).
# yaw: compass bearing of the optical axis (deg from north, clockwise); pitch up positive; roll clockwise positive.
import sys, json, math
import numpy as np

def basis(yaw, pitch, roll):
    y, p, r = map(math.radians, (yaw, pitch, roll))
    f = np.array([math.sin(y)*math.cos(p), math.cos(y)*math.cos(p), math.sin(p)])
    rt = np.array([math.cos(y), -math.sin(y), 0.])
    up = np.cross(rt, f)
    rt2 = rt*math.cos(r) - up*math.sin(r); up2 = up*math.cos(r) + rt*math.sin(r)
    return f, rt2, up2

def project(cam, xyz, W, H):
    f, rt, up = basis(cam['yaw'], cam['pitch'], cam['roll'])
    d = np.asarray(xyz, float) - np.asarray(cam['pos'], float)
    z = d @ f
    if np.ndim(z) == 0:
        return np.array([W/2 + cam.get('dx', 0) + cam['fpx']*(d @ rt)/z, H/2 + cam.get('dy', 0) - cam['fpx']*(d @ up)/z]), z
    return np.stack([W/2 + cam.get('dx', 0) + cam['fpx']*(d @ rt)/z, H/2 + cam.get('dy', 0) - cam['fpx']*(d @ up)/z], 1), z

KEYS = ['x', 'y', 'z', 'yaw', 'pitch', 'roll', 'fpx']

def to_cam(v): return {'pos': [v[0], v[1], v[2]], 'yaw': v[3], 'pitch': v[4], 'roll': v[5], 'fpx': v[6]}

def fit(lm_path, out_path):
    from scipy.optimize import least_squares
    L = json.load(open(lm_path)); W, H = L['W'], L['H']; I = L['init']
    pts = [p for p in L['points'] if not p.get('skip')]
    X = np.array([p['xyz'] for p in pts], float); U = np.array([p['px'] for p in pts], float)
    fixed = L.get('fix', {})                      # e.g. {"z": 1.6} for a hand-held street photo
    free = [k for k in KEYS if k not in fixed]
    v0 = {**{'x': I['pos'][0], 'y': I['pos'][1], 'z': I['pos'][2]}, **I}
    def full(v):
        d = dict(fixed); d.update(dict(zip(free, v))); return [d[k] for k in KEYS]
    lines = L.get('lines', [])
    def vp_res(cam):
        # line constraints: an image segment along a known 3D direction must point at that direction's vanishing point
        f, rt, up = basis(cam['yaw'], cam['pitch'], cam['roll']); out = []
        for ln in lines:
            d = np.asarray(ln['dir'], float); a = np.asarray(ln['p1'], float); b = np.asarray(ln['p2'], float)
            # homogeneous VP: (cx*dz + F*dx, cy*dz - F*dy, dz) with dx,dy,dz in camera axes
            dx, dy, dz = d @ rt, d @ up, d @ f; cx, cy = W/2, H/2; F = cam['fpx']
            vp = np.array([cx*dz + F*dx, cy*dz - F*dy, dz])
            l = np.cross(np.append(a, 1), vp); n = np.hypot(l[0], l[1])
            out.append(w_line * (l @ np.append(b, 1)) / max(n, 1e-9))
        return np.array(out)
    w_line = L.get('line_weight', 1.0)
    def res(v):
        cam = to_cam(full(v)); uv, z = project(cam, X, W, H)
        hz = []
        if 'horizon_y' in L:   # eye-level line read off distant pedestrians' heads (camera height ~ eye height)
            f_, rt_, up_ = basis(cam['yaw'], cam['pitch'], cam['roll']); fl = np.array([f_[0], f_[1], 0.]); fl /= np.linalg.norm(fl)
            q, _ = project(cam, np.asarray(cam['pos']) + fl*1e4, W, H); hz = [L.get('horizon_weight', 3.0)*(q[1] - L['horizon_y'])]
        return np.concatenate([(uv - U).ravel(), np.where(z < 1, 1e3, 0), vp_res(cam), hz])
    r = least_squares(res, [v0[k] for k in free], loss='soft_l1', f_scale=20)
    cam = to_cam(full(r.x)); uv, _ = project(cam, X, W, H); e = np.linalg.norm(uv - U, axis=1)
    out = {**cam, 'W': W, 'H': H, 'photo': L['photo'], 'rms_px': float(np.sqrt((e**2).mean())), 'n_points': len(pts),
           'residuals_px': {p['id']: round(float(x), 1) for p, x in zip(pts, e)}, 'fixed': fixed, 'note': L.get('note', '')}
    json.dump(out, open(out_path, 'w'), indent=1)
    print(json.dumps({k: (round(v, 3) if isinstance(v, float) else v) for k, v in out.items() if k != 'residuals_px'}))
    for p, x in zip(pts, e): print(f"  {p['id']:28s} {x:6.1f} px")
    lr = vp_res(cam) / w_line if lines else []
    for ln, x in zip(lines, lr): print(f"  line {ln['id']:23s} {x:6.1f} px")
    out['line_residuals_px'] = {ln['id']: round(float(x), 1) for ln, x in zip(lines, lr)}
    json.dump(out, open(out_path, 'w'), indent=1)

def draw(fit_path, photo, lod2_path, out, lm_path=None, edges_path=None):
    from PIL import Image, ImageDraw
    C = json.load(open(fit_path)); W, H = C['W'], C['H']
    im = Image.open(photo).convert('RGB').resize((W, H)); d = ImageDraw.Draw(im)
    lod = json.load(open(lod2_path))
    def seg(a, b, col, w=2):
        (pa, za), (pb, zb) = project(C, a, W, H), project(C, b, W, H)
        if za > .5 and zb > .5: d.line([tuple(pa), tuple(pb)], fill=col, width=w)
    for k, col in (('WallSurface', (255, 60, 60)), ('RoofSurface', (255, 230, 0))):
        for s in lod[k]:
            for i in range(len(s) - 1): seg(s[i], s[i+1], col, 1)
    if edges_path:
        for a, b in json.load(open(edges_path)): seg(a, b, (0, 255, 255), 2)
    if lm_path:
        for p in json.load(open(lm_path))['points']:
            q, z = project(C, p['xyz'], W, H); u, v = p['px']
            d.ellipse([u-5, v-5, u+5, v+5], outline=(0, 255, 0), width=2)
            if z > 0: d.line([(u, v), tuple(q)], fill=(0, 255, 0), width=2); d.rectangle([q[0]-3, q[1]-3, q[0]+3, q[1]+3], fill=(255, 0, 255))
            d.text((u+7, v-7), p['id'], fill=(0, 255, 0))
    d.text((8, H-18), f"{C['photo']}  rms {C.get('rms_px', 0):.1f} px", fill=(255, 255, 255))
    im.save(out, quality=88)

if __name__ == '__main__':
    if sys.argv[1] == 'fit': fit(sys.argv[2], sys.argv[3])
    else: draw(*sys.argv[2:7]) if len(sys.argv) > 6 else draw(*sys.argv[2:])
