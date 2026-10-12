# Gate C0 self-review: does the priority ranking survive other weights, a walker's view band, or losing one viewpoint?
#   python3 tools/core/sensitivity.py <vis_dir> [ids...]
# Re-scores from the ID panoramas (<cam>_ids.npy) with the same formula as build_register.py, varying one thing at a time.
import json, csv, glob, sys, os
import numpy as np

vis = sys.argv[1]; watch = sys.argv[2:] or ['way/136690966', 'way/60739635', 'way/55896465', 'way/355250634', 'way/142438894']
HERE = os.path.dirname(os.path.abspath(__file__)); DOCS = os.path.join(HERE, '..', '..', 'docs', 'core')
B = json.load(open(os.path.join(DOCS, 'coverage', 'buildings_c0.json'))); idx = {i + 1: b['id'] for i, b in enumerate(B)}
rows = {r['source_building_id']: r for r in csv.DictReader(open(os.path.join(DOCS, 'ASSET_REGISTER.csv'), encoding='utf-8-sig'))}
cams = sorted(os.path.basename(p)[:-8] for p in glob.glob(os.path.join(vis, '*_ids.npy')))
H, W = np.load(os.path.join(vis, cams[0] + '_ids.npy')).shape
lat = (0.5 - (np.arange(H) + .5) / H) * 180
WEIGHT = {'sphere': np.cos(np.radians(lat)),                                        # as build_register.py
          'band': np.where((lat > -15) & (lat < 35), np.cos(np.radians(lat)), 0)}  # what a walker looks at
INC = {'finished_verified': 0, 'in_review': .3, 'in_progress': .7, 'not_started': 1}

def shares(w):
    out = {}; tot = w.sum() * W
    for c in cams:
        ids = np.load(os.path.join(vis, c + '_ids.npy'))
        for k in np.unique(ids[ids > 0]): out.setdefault(idx[k], {})[c] = float(((ids == k) * w[:, None]).sum() / tot)
    return out

def rank(sh, wa=.45, wc=.25, ws=.20, wi=.10, views=None):
    views = views or cams; best = max(max(v.get(c, 0) for c in views) for v in sh.values()); sc = {}
    for i, v in sh.items():
        mx = max(v.get(c, 0) for c in views); n = sum(v.get(c, 0) >= .001 for c in views)
        sc[i] = wa * mx / best + wc * n / len(views) + ws * float(rows[i]['salience']) + wi * INC[rows[i]['ss2_status']]
    return [i for i, _ in sorted(sc.items(), key=lambda x: -x[1])]

SPH, BAND = shares(WEIGHT['sphere']), shares(WEIGHT['band'])
variants = [('base (.45/.25/.20/.10)', rank(SPH)), ('no salience (.6/.3/0/.1)', rank(SPH, .6, .3, 0, .1)), ('area only', rank(SPH, 1, 0, 0, 0)),
            ('coverage-heavy (.3/.5/.1/.1)', rank(SPH, .3, .5, .1, .1)), ('walker band -15..35 deg', rank(BAND)), ('band, no salience', rank(BAND, .6, .3, 0, .1))]
variants += [('without ' + c, rank(SPH, views=[x for x in cams if x != c])) for c in cams]
out = {}
for name, r in variants:
    out[name] = {'top10': r[:10], 'watch': {w: r.index(w) + 1 if w in r else None for w in watch}}
    print(f'{name:34s}', out[name]['watch'])
json.dump(out, open(os.path.join(DOCS, 'coverage', 'sensitivity.json'), 'w'), indent=1, ensure_ascii=False)
