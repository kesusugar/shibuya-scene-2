# C3a: re-solve a reference photo's camera against the 2.0 model (common datum, plan metres).
#   python3 scripts/solve-ref-camera.py draw <cam.json> <photo> <out.png>        overlay of known 3D features
#   python3 scripts/solve-ref-camera.py fit  <landmarks.json> <out cam.json>      least squares on hand-read points
# Camera: pos (x, y, z datum), yaw (compass, deg), pitch (deg, up +), roll (deg, clockwise +), vfov (deg), W, H.
# Features: crosswalk band corners (assets/ground/core/source/data/ground_input.json, heights on the PLATEAU road),
# QFRONT and MAGNET PLATEAU roof corners lifted by each model's measured anchor offset (ground_anchors.json).
import sys, json, math
import numpy as np
from PIL import Image, ImageDraw, ImageFont

def basis(yaw, pitch, roll):
    y, p, r = map(math.radians, (yaw, pitch, roll))
    f = np.array([math.sin(y) * math.cos(p), math.cos(y) * math.cos(p), math.sin(p)])
    rt = np.array([math.cos(y), -math.sin(y), 0.0]); up = np.cross(rt, f)
    return f, rt * math.cos(r) - up * math.sin(r), up * math.cos(r) + rt * math.sin(r)

def project(cam, X):
    f, rt, up = basis(cam['yaw'], cam['pitch'], cam['roll'])
    fpx = cam['H'] / 2 / math.tan(math.radians(cam['vfov']) / 2)
    d = np.asarray(X, float) - np.asarray(cam['pos'], float); z = d @ f
    return np.stack([cam['W'] / 2 + fpx * (d @ rt) / z, cam['H'] / 2 - fpx * (d @ up) / z], -1), z

def features():
    G = json.load(open('assets/ground/core/source/data/ground_input.json'))
    road = np.array([p for s in G['surfaces'] if s['class'] in ('road', 'intersection') for p in s['ring']])
    def rz(x, y):
        d = np.hypot(road[:, 0] - x, road[:, 1] - y); i = np.argsort(d)[:8]; w = 1 / np.maximum(d[i], .3) ** 2
        return float((road[i, 2] * w).sum() / w.sum()) - 15.0
    F = {}
    for c in G['crosswalks']:
        for k, (x, y) in enumerate(c['band']): F[f"{c['id'].split('/')[1]}_c{k}"] = [x, y, rz(x, y)]
        # painted corners: the two ends of the first and of the last zebra bar (what a photo actually shows)
        if len(c['bars']) >= 2:
            b = np.array(c['band']); ax = b[1] - b[0]; ax = ax / (np.linalg.norm(ax) or 1)
            for tag, bar in (('a', c['bars'][0]), ('b', c['bars'][-1])):
                q = np.array(bar)[:, :2]; t = q @ ax
                for end, j in (('0', int(np.argmin(t))), ('1', int(np.argmax(t)))):
                    x, y = q[j]; F[f"{c['id'].split('/')[1]}_{tag}{end}"] = [float(x), float(y), rz(x, y) + 0.012]
    A = json.load(open('assets/ground/core/source/data/ground_anchors.json'))
    P = json.load(open(sys.argv[-1])) if sys.argv[-1].endswith('plateau_core.json') else None
    return F

if __name__ == '__main__':
    cmd = sys.argv[1]
    if cmd == 'draw':
        cam = json.load(open(sys.argv[2])); im = Image.open(sys.argv[3]).convert('RGB').resize((cam['W'], cam['H']))
        d = ImageDraw.Draw(im); F = features()
        try: font = ImageFont.truetype('/usr/share/fonts/opentype/ipafont-gothic/ipag.ttf', 11)
        except OSError: font = ImageFont.load_default()
        ids = [i for i in F if not i.split('_')[-1].startswith('c')]; uv, z = project(cam, [F[i] for i in ids])
        for i, (u, v), zz in zip(ids, uv, z):
            if zz <= 0 or not (-50 < u < cam['W'] + 50 and -50 < v < cam['H'] + 50): continue
            d.ellipse([u - 3, v - 3, u + 3, v + 3], outline=(0, 255, 0)); d.text((u + 4, v - 6), i, font=font, fill=(0, 255, 0))
        G = json.load(open('assets/ground/core/source/data/ground_input.json'))
        for c in G['crosswalks']:
            pts = [F[f"{c['id'].split('/')[1]}_c{k}"] for k in range(len(c['band']))]
            uv2, z2 = project(cam, pts)
            if (z2 > 0).all(): d.polygon([tuple(p) for p in uv2], outline=(255, 0, 255))
        im.save(sys.argv[4])
    elif cmd == 'fit':
        from scipy.optimize import least_squares
        L = json.load(open(sys.argv[2])); F = features(); F.update(L.get('extra_points', {}))
        pts = [p for p in L['points'] if not p.get('skip')]
        X = np.array([F[p['id']] if 'xyz' not in p else p['xyz'] for p in pts], float); U = np.array([p['px'] for p in pts], float)
        c0 = L['init']; keys = ['x', 'y', 'z', 'yaw', 'pitch', 'roll', 'vfov']; fixed = L.get('fix', {})
        v0 = {'x': c0['pos'][0], 'y': c0['pos'][1], 'z': c0['pos'][2], **c0}
        free = [k for k in keys if k not in fixed]
        def cam_of(v):
            d = {**{k: fixed[k] for k in fixed}, **dict(zip(free, v))}
            return {'pos': [d['x'], d['y'], d['z']], 'yaw': d['yaw'], 'pitch': d['pitch'], 'roll': d['roll'], 'vfov': d['vfov'], 'W': L['W'], 'H': L['H']}
        def resid(v): uv, _ = project(cam_of(v), X); return (uv - U).ravel()
        r = least_squares(resid, [v0[k] for k in free], loss='soft_l1', f_scale=8.0)
        cam = cam_of(r.x); uv, _ = project(cam, X); e = np.hypot(*(uv - U).T)
        cam.update(rms_px=round(float(np.sqrt((e ** 2).mean())), 2), max_px=round(float(e.max()), 2), n=len(pts), photo=L['photo'],
                   per_point={p['id']: round(float(x), 1) for p, x in zip(pts, e)})
        f, rt, up = basis(cam['yaw'], cam['pitch'], cam['roll']); tgt = np.array(cam['pos']) + 100 * f
        cam['target'] = [round(float(t), 2) for t in tgt]
        json.dump(cam, open(sys.argv[3], 'w'), indent=1)
        print(json.dumps({k: cam[k] for k in ('pos', 'yaw', 'pitch', 'roll', 'vfov', 'rms_px', 'max_px', 'n')}))
