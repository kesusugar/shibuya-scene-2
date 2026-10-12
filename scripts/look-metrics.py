# C3a: photo vs WebGL render, class by class, for every photograph with a solved camera.
#   python3 scripts/look-metrics.py <render_dir> <out.json> [--refs refs.json]
# The class pass (?pass=class) is the mask: each class region is eroded (the camera fits are 11-28 px off at full
# size), then the mean colour inside it is measured in the photograph and in the beauty render, both resized to the
# render's size. Colours are compared in CIE L*a*b* (D65, sRGB input). A class needs >= 400 px to count.
# The point is a common look: a material change is judged by the mean error over all views and both times of day,
# never by one photograph.
import json, sys, os
import numpy as np
from PIL import Image, ImageFilter

rdir, out = sys.argv[1:3]
REFS = {
    'm027': {'photo': 'assets/buildings/magnet/source/refs/raw/M027.jpg', 'time': 'day', 'year': 2025, 'licence': 'CC0 (Taufik)', 'aligned': True},
    'q032': {'photo': 'assets/buildings/qfront/source/refs/raw/Q032.jpg', 'time': 'day', 'year': 2018, 'licence': 'CC BY-SA 4.0 (Kakidai)', 'aligned': True},
    'refa': {'photo': 'evidence/c3a/refs/In_Front_of_Shibuya_Station.jpg', 'time': 'day', 'year': 2010, 'licence': 'CC BY 2.0 (Dick Johnson)', 'aligned': False},
    'refb': {'photo': 'evidence/c3a/refs/Shibuya_scramble_av_night_from_Stream.jpg', 'time': 'night', 'year': 2024, 'licence': 'CC0 (Syced)', 'aligned': False},
}
CLASSES = {'glass': (0, 0, 255), 'sign': (255, 255, 0), 'interior': (255, 0, 255), 'wall': (255, 0, 0), 'road': (0, 255, 0),
           'sidewalk': (0, 255, 255), 'kerb': (128, 128, 0), 'marking': (255, 255, 255), 'fill': (0, 128, 128),
           'vegetation': (0, 128, 0), 'furniture': (128, 0, 128)}
# classes the photo can stand for: signs/screens change with the era and are reported but not used for the score
SCORED = ['glass', 'wall', 'road', 'sidewalk']

def lab(rgb):
    c = rgb / 255.0
    c = np.where(c <= 0.04045, c / 12.92, ((c + 0.055) / 1.055) ** 2.4)
    M = np.array([[0.4124, 0.3576, 0.1805], [0.2126, 0.7152, 0.0722], [0.0193, 0.1192, 0.9505]])
    xyz = c @ M.T / np.array([0.95047, 1.0, 1.08883])
    f = np.where(xyz > 0.008856, np.cbrt(xyz), 7.787 * xyz + 16 / 116)
    return np.stack([116 * f[..., 1] - 16, 500 * (f[..., 0] - f[..., 1]), 200 * (f[..., 1] - f[..., 2])], -1)

res = {}
for v, ref in REFS.items():
    cp, bp = os.path.join(rdir, f'{v}_class.png'), os.path.join(rdir, f'{v}_beauty.png')
    if not (os.path.exists(cp) and os.path.exists(bp) and os.path.exists(ref['photo'])): continue
    cls = np.asarray(Image.open(cp).convert('RGB')).astype(int)
    H, W = cls.shape[:2]
    beauty = np.asarray(Image.open(bp).convert('RGB').resize((W, H))).astype(float)
    photo = np.asarray(Image.open(ref['photo']).convert('RGB').resize((W, H), Image.LANCZOS)).astype(float)
    # aligned cameras (M027 11 px, Q032 13 px): 4 px at 640 wide; the old REF-A/REF-B cameras are 20-40 px off
    # against the 2.0 model, so their masks lose 13 px and they count half in the score
    er = max(3, round(W / 160)) if ref['aligned'] else round(W / 50)
    v_res = {'time': ref['time'], 'year': ref['year'], 'aligned': ref['aligned'], 'size': [W, H], 'classes': {}}
    for c, col in CLASSES.items():
        m = (np.abs(cls - np.array(col)).sum(-1) < 30).astype(np.uint8) * 255
        m = np.asarray(Image.fromarray(m).filter(ImageFilter.MinFilter(2 * er + 1))) > 0
        n = int(m.sum())
        if n < 400: continue
        p, r = photo[m].mean(0), beauty[m].mean(0)
        lp, lr = lab(p[None])[0], lab(r[None])[0]
        v_res['classes'][c] = {'px': n, 'photo_rgb': [round(x) for x in p], 'render_rgb': [round(x) for x in r],
                               'photo_lab': [round(x, 1) for x in lp], 'render_lab': [round(x, 1) for x in lr],
                               'dL': round(float(lr[0] - lp[0]), 1), 'dE': round(float(np.linalg.norm(lr - lp)), 1)}
    res[v] = v_res
# summary: mean |dL| and mean dE per class over views, and over everything scored
summ = {}
for c in CLASSES:
    rows = [r['classes'][c] for r in res.values() if c in r['classes']]
    if rows: summ[c] = {'views': len(rows), 'mean_abs_dL': round(float(np.mean([abs(x['dL']) for x in rows])), 1), 'mean_dE': round(float(np.mean([x['dE'] for x in rows])), 1),
                        'mean_dL': round(float(np.mean([x['dL'] for x in rows])), 1)}
def score(sel):
    rows = [(r['classes'][c], 1.0 if r['aligned'] else 0.5) for r in sel for c in SCORED if c in r['classes']]
    if not rows: return None
    w = np.array([x[1] for x in rows])
    return {'n': len(rows), 'mean_abs_dL': round(float((w * [abs(x[0]['dL']) for x in rows]).sum() / w.sum()), 2),
            'mean_dE': round(float((w * [x[0]['dE'] for x in rows]).sum() / w.sum()), 2)}
summ['_score'] = {'scored_classes': SCORED, 'weights': 'aligned views 1.0, REF-A/REF-B 0.5',
                  'all': score(list(res.values())), 'day': score([r for r in res.values() if r['time'] == 'day']),
                  'night': score([r for r in res.values() if r['time'] == 'night']), 'aligned_only': score([r for r in res.values() if r['aligned']])}
json.dump({'views': res, 'summary': summ, 'refs': REFS}, open(out, 'w'), indent=1, ensure_ascii=False)
for v, r in res.items():
    print(v, r['time'], ' '.join(f"{c}:dL{x['dL']:+.0f}/dE{x['dE']:.0f}" for c, x in r['classes'].items()))
print('SUMMARY', json.dumps(summ))
