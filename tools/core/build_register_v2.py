# Gate C0 supplement: register v2 from the PLATEAU-LOD2 panoramas (5 ground views + 2 photo-solved elevated views),
# plus a structure register (viaducts, decks, corridor, subway entrances) and status panoramas for the new views.
#   python3 tools/core/build_register_v2.py <records_v2.json> <docs/core> <cam_id>=<vis_dir>[:<records.json>] ...
# Score is the C0 formula (0.45 area + 0.25 views + 0.20 salience + 0.10 incompleteness) over 7 views. For the
# elevated photo cameras the area term uses the share of the photo's field, not of the whole sphere, so a view
# that looks one way is not penalised for the building behind it.
import json, sys, os, csv, math
import numpy as np
from PIL import Image, ImageDraw, ImageFont

rpath, out = sys.argv[1:3]; views = {}
for a in sys.argv[3:]:
    cid, rest = a.split('=', 1); vis, _, rec = rest.partition(':'); views[cid] = (vis, rec or rpath)
R = json.load(open(rpath)); byid = {r['id']: r for r in R}
HERE = os.path.dirname(os.path.abspath(__file__))
IDN = json.load(open(os.path.join(HERE, 'identity_notes.json'), encoding='utf-8'))
old = {r['source_building_id']: r for r in csv.DictReader(open(os.path.join(out, 'ASSET_REGISTER.csv'), encoding='utf-8-sig'))}
cov = {cid: json.load(open(os.path.join(v, f'{cid}_coverage.json'))) for cid, (v, _) in views.items()}
ELEV = [c for c in cov if c.startswith('X')]

def share(cid, bid):
    e = cov[cid]['buildings'].get(bid)
    if not e: return 0.0
    return e.get('share_of_photo_field', e['share_of_sphere']) if cid in ELEV else e['share_of_sphere']
INC = {'finished_verified': 0.0, 'in_review': 0.3, 'in_progress': 0.7, 'not_started': 1.0}
STATUS = {'way/136691386': 'finished_verified', 'way/116806281': 'in_review', 'way/55896465': 'in_progress'}
best = max(share(c, b) for c in cov for b in byid if b in cov[c]['buildings'])
rows = []
for r in R:
    st = STATUS.get(r['id'], 'not_started')
    s = {c: share(c, r['id']) for c in cov}; mx = max(s.values()); n = sum(v >= 0.001 for v in s.values())
    o = old.get(r['id'], {})
    sal = float(o['salience']) if o else (0.5 if r['kind'] == 'structure' else 0.2)
    score = 0.45 * mx / best + 0.25 * n / len(cov) + 0.20 * sal + 0.10 * INC[st]
    rows.append({'source_id': r['id'], 'kind': r['kind'], 'name': r['name'] or '(名称なし)', 'identity_note': IDN.get(r['id'], o.get('identity_note', '')),
                 'geometry_v2': r['geometry'], 'ground_tp': r.get('ground_tp', ''), 'top_tp': r.get('top_tp', ''), 'height_m': r['height_used'], 'height_source': r['height_source'],
                 'dist_from_crossing_m': r['dist_from_crossing_m'], 'ss2_status': st, 'c0_rank': o.get('rank', ''),
                 **{f'share_{c}': round(v, 5) for c, v in s.items()}, 'visible_views': n, 'visible_area_max': round(mx, 5),
                 'salience': sal, 'priority_score': round(score, 4)})
rows.sort(key=lambda x: -x['priority_score'])
for i, x in enumerate(rows): x['rank_v2'] = i + 1
cols = ['rank_v2'] + [k for k in rows[0] if k != 'rank_v2']
with open(os.path.join(out, 'ASSET_REGISTER_V2.csv'), 'w', newline='', encoding='utf-8-sig') as f:
    w = csv.DictWriter(f, fieldnames=cols); w.writeheader(); w.writerows(rows)

# status panoramas for every view (v2 geometry); labels for the 8 largest
try: FONT = ImageFont.truetype('/usr/share/fonts/opentype/ipafont-gothic/ipag.ttf', 15)
except OSError: FONT = ImageFont.load_default()
COL = {'finished_verified': (60, 170, 80), 'in_review': (230, 190, 40), 'in_progress': (240, 140, 30), 'not_started': (200, 60, 60)}
st_of = {x['source_id']: x['ss2_status'] for x in rows}
os.makedirs(os.path.join(out, 'coverage_v2'), exist_ok=True)
for cid, (vis, rec) in views.items():
    RR = json.load(open(rec)); idx = {i + 1: r['id'] for i, r in enumerate(RR)}
    ids = np.load(os.path.join(vis, f'{cid}_ids.npy')); H, W = ids.shape
    img = np.zeros((H, W, 3), np.uint8); img[ids == 0] = (150, 190, 235); img[ids == -1] = (110, 110, 105)
    for k in np.unique(ids[ids > 0]):
        bid = idx[k]; base = np.array((90, 60, 160) if byid[bid]['kind'] == 'structure' and st_of[bid] == 'not_started' else COL[st_of[bid]])
        img[ids == k] = np.clip(base * (0.75 + 0.25 * ((k * 37) % 7) / 6), 0, 255)
    edge = np.zeros_like(ids, bool); edge[:, 1:] |= ids[:, 1:] != ids[:, :-1]; edge[1:, :] |= ids[1:, :] != ids[:-1, :]
    img[edge & (ids != 0)] = (30, 30, 30)
    band = (int(H * .25), int(H * .62)) if cid not in ELEV else (int(H * .30), int(H * .75))
    im = Image.fromarray(img[band[0]:band[1]]); d = ImageDraw.Draw(im)
    top = sorted(cov[cid]['buildings'].items(), key=lambda kv: -kv[1].get('share_of_photo_field', kv[1]['share_of_sphere']))[:8]
    for bid, _ in top:
        k = [i for i, x in idx.items() if x == bid][0]; ys, xs = np.where(ids == k)
        lab = byid[bid]['name'] or (IDN.get(bid, '').split('：')[-1].split('（')[0][:12] if bid in IDN else ('高架・橋梁' if byid[bid]['kind'] == 'structure' else bid[:16]))
        d.text((int(np.median(xs)) - 30, max(2, int(np.median(ys)) - band[0])), lab[:14], font=FONT, fill=(0, 0, 0))
    for b_ in range(0, 360, 60):
        x = int((b_ / 360 + 0.5) % 1 * W); d.line([(x, 0), (x, 8)], fill=(0, 0, 0)); d.text((x + 2, 0), f'{b_}°', font=FONT, fill=(0, 0, 0))
    if 'view_bearing_deg' in cov[cid]['camera']:
        c = cov[cid]['camera']; h = c.get('half_hfov_deg', 33)
        for e in (c['view_bearing_deg'] - h, c['view_bearing_deg'] + h):
            x = int((e / 360 + 0.5) % 1 * W); d.line([(x, 0), (x, im.height)], fill=(255, 255, 255), width=2)
    im.save(os.path.join(out, 'coverage_v2', f'{cid}_status.png'))
json.dump({cid: {'camera': c['camera'], 'burial_check': c['burial_check'], 'sky_share': c['sky_share'], 'ground_share': c['ground_share']} for cid, c in cov.items()},
          open(os.path.join(out, 'coverage_v2', 'views.json'), 'w'), ensure_ascii=False, indent=1)
print('rows', len(rows)); [print(x['rank_v2'], x['c0_rank'], x['source_id'], x['name'][:16], x['identity_note'][:20], x['priority_score']) for x in rows[:30]]
