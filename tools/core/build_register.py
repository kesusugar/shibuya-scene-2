# Gate C0: master building register, view coverage table, priority ranking and status panoramas.
#   python3 tools/core/build_register.py <buildings.json> <vis_dir> <docs/core>
# Score (pack 01, provisional): 0.45*visible_area + 0.25*viewpoint_coverage + 0.20*salience + 0.10*incompleteness,
# each 0..1. visible_area = best single-view solid-angle share / best share of any building; coverage = views with
# >= 0.1 % of the sphere / 5; salience = see SALIENCE below (documented proxy, not a measurement).
import json, sys, os, csv, glob
import numpy as np
from PIL import Image, ImageDraw, ImageFont

bpath, vis, out = sys.argv[1:4]; os.makedirs(os.path.join(out, 'coverage'), exist_ok=True)
IDN = json.load(open(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'identity_notes.json'), encoding='utf-8'))
B = json.load(open(bpath)); byid = {b['id']: b for b in B}
VIEWS = sorted(glob.glob(os.path.join(vis, '*_coverage.json')))
cov = {json.load(open(p))['camera']['camera_id']: json.load(open(p)) for p in VIEWS}

# 2.0 status, checked against the files in this repository (assets/buildings/*) - see ASSET_REGISTER notes
SS2 = {
    'way/136691386': ('finished_verified', 'QFRONT v5 (owner-approved final, 2018 signage; 2025 sign layer not split yet) - assets/buildings/qfront'),
    'way/116806281': ('in_review', 'MAGNET v2 in PR #3 (assets/buildings/magnet); the Eiraku building inside this PLATEAU footprint is assets/buildings/eiraku'),
    'way/55896465': ('in_progress', 'Seibu A: reference photos + PLATEAU LOD2 extracted on branch claude/g4-seibu-a (uncommitted), no model yet'),
}
OLD_SIGN_PARENTS = {'way/136690966': 'Taiseido roof sign frame (Hisamitsu / サロンパス boards) in old src/signs/sign-structures.mjs'}
OLD_STATION = {'way/906194249', 'way/854794950', 'way/1354871463', 'way/1354871464', 'way/858994296', 'way/810356690', 'way/904734439', 'way/1350895889', 'way/904652357', 'way/904652318'}
def salience(b):
    if b['id'] in OLD_SIGN_PARENTS: return 1.0, 'rooftop ad frame (old sign-structures)'
    if b['old_status'] == 'dedicated_hero': return 0.8, 'landmark (old dedicated hero)'
    if b['id'] in OLD_STATION or 'station' in b['old_status'] or b['building'] in ('train_station', 'transportation'): return 0.7, 'station structure'
    if b['name']: return 0.4, 'named building'
    return 0.2, 'unnamed'
INCOMPLETE = {'finished_verified': 0.0, 'in_review': 0.3, 'in_progress': 0.7, 'not_started': 1.0}

rows = []; best_any = max((v['share_of_sphere'] for c in cov.values() for v in c['buildings'].values()), default=1)
for b in B:
    st, note = SS2.get(b['id'], ('not_started', ''))
    shares = {cid: c['buildings'].get(b['id'], {}).get('share_of_sphere', 0.0) for cid, c in cov.items()}
    mx = max(shares.values()); nviews = sum(1 for s in shares.values() if s >= 0.001)
    sal, why = salience(b)
    score = 0.45 * (mx / best_any) + 0.25 * nviews / len(cov) + 0.20 * sal + 0.10 * INCOMPLETE[st]
    d = b['dist_from_crossing_m']
    tier = 'Core' if d <= 50 else ('Middle' if d <= 150 else 'Background')
    vis_tier = 'Tier1_candidate' if mx >= 0.005 else ('Tier2_candidate' if mx >= 0.001 else ('visible_minor' if mx > 0 else 'not_visible_from_5_views'))
    rows.append({'source_building_id': b['id'], 'name': b['name'] or '(名称なし)', 'name_en': b['name_en'], 'osm_building': b['building'],
                 'plateau_id': b['plateau_id'], 'measuredHeight_m': b['measuredHeight'], 'plateau_top_m': b['plateau_top'], 'height_used_m': b['height_used'], 'height_source': b['height_source'],
                 'centroid_x_east_m': b['centroid'][0], 'centroid_y_north_m': b['centroid'][1], 'dist_from_crossing_m': d, 'distance_zone': tier,
                 'identity_note': IDN.get(b['id'], ''), 'old_status': b['old_status'], 'ss2_status': st, 'ss2_note': note or OLD_SIGN_PARENTS.get(b['id'], ''),
                 **{f'share_{cid}': round(s, 5) for cid, s in shares.items()}, 'visible_views': nviews, 'visible_area_max_fraction': round(mx, 5),
                 'salience': sal, 'salience_reason': why, 'priority_score': round(score, 4), 'visibility_tier': vis_tier})
rows.sort(key=lambda r: -r['priority_score'])
for i, r in enumerate(rows): r['rank'] = i + 1
cols = ['rank'] + [k for k in rows[0] if k != 'rank']
with open(os.path.join(out, 'ASSET_REGISTER.csv'), 'w', newline='', encoding='utf-8-sig') as f:
    w = csv.DictWriter(f, fieldnames=cols); w.writeheader(); w.writerows(rows)
with open(os.path.join(out, 'VIEW_COVERAGE.csv'), 'w', newline='', encoding='utf-8-sig') as f:
    w = csv.writer(f); w.writerow(['camera_id', 'view_yaw_deg', 'building_id', 'name', 'visible_fraction_of_sphere', 'day_or_night', 'method'])
    for cid, c in cov.items():
        for bid, v in sorted(c['buildings'].items(), key=lambda kv: -kv[1]['share_of_sphere']):
            for sec, s in v['sectors'].items():
                w.writerow([cid, sec, bid, byid[bid]['name'], round(s, 6), 'geometry-only', 'object-ID equirect panorama, PLATEAU/OSM prisms'])
json.dump(rows[:40], open(os.path.join(out, 'coverage', 'top40.json'), 'w'), ensure_ascii=False, indent=1)

# status panoramas: green finished, yellow in review/progress, red not started; labels for the 8 biggest per view
try: FONT = ImageFont.truetype('/usr/share/fonts/opentype/ipafont-gothic/ipag.ttf', 15)
except OSError: FONT = ImageFont.load_default()
status = {r['source_building_id']: r['ss2_status'] for r in rows}
COL = {'finished_verified': (60, 170, 80), 'in_review': (230, 190, 40), 'in_progress': (240, 140, 30), 'not_started': (200, 60, 60)}
idx2id = {i + 1: b['id'] for i, b in enumerate(B)}
for cid, c in cov.items():
    ids = np.load(os.path.join(vis, f'{cid}_ids.npy')); H, W = ids.shape
    img = np.zeros((H, W, 3), np.uint8); img[ids == 0] = (150, 190, 235); img[ids == -1] = (110, 110, 105)
    for k in np.unique(ids[ids > 0]):
        base = np.array(COL[status[idx2id[k]]]); shade = 0.75 + 0.25 * ((k * 37) % 7) / 6
        img[ids == k] = np.clip(base * shade, 0, 255)
    edge = np.zeros_like(ids, bool); edge[:, 1:] |= ids[:, 1:] != ids[:, :-1]; edge[1:, :] |= ids[1:, :] != ids[:-1, :]
    img[edge & (ids != 0)] = (30, 30, 30)
    im = Image.fromarray(img[int(H * .25):int(H * .62)]); d = ImageDraw.Draw(im)   # elevation -45..+45 deg band
    top = sorted(c['buildings'].items(), key=lambda kv: -kv[1]['share_of_sphere'])[:8]
    for bid, v in top:
        k = [i for i, x in idx2id.items() if x == bid][0]; ys, xs = np.where(ids == k)
        cx = int(np.median(xs)); cy = int(np.median(ys)) - int(H * .25)
        lab = byid[bid]['name'] or (IDN.get(bid, '').split('：')[-1].split('（')[0][:12] if bid in IDN else bid)
        d.text((cx - 30, max(2, cy)), lab[:14], font=FONT, fill=(0, 0, 0))
    for b_ in range(0, 360, 60):
        x = int((b_ / 360 + 0.5) % 1 * W); d.line([(x, 0), (x, 8)], fill=(0, 0, 0)); d.text((x + 2, 0), f'{b_}°', font=FONT, fill=(0, 0, 0))
    im.save(os.path.join(out, 'coverage', f'{cid}_status.png'))
print('rows', len(rows), 'top5', [(r['name'], r['priority_score']) for r in rows[:5]])
