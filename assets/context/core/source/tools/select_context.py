"""C-level context of the Core: every PLATEAU 2025 LOD2 building and bridge within RADIUS of the crossing that does
not have its own asset, as input for build_context.py.

python3 select_context.py plateau_core.json records_v2.json ASSET_REGISTER_V2.csv street_input.json out.json

C level (docs/core/DECISIONS.md): PLATEAU form and shared materials. It is a stand-in that later A/B assets replace one
building at a time: add the building's PLATEAU id to OWN_ASSETS (or give it an asset folder) and rebuild.
"""
import csv, json, math, sys
plateau_path, records_path, register_path, street_path, out_path = sys.argv[1:6]
RADIUS, DATUM, CENTRE = 250.0, 15.0, (6.5, -2.0)
P = json.load(open(plateau_path)); R = json.load(open(records_path))
reg = {r['source_id']: r for r in csv.DictReader(open(register_path, encoding='utf-8-sig'))}
street = json.load(open(street_path))
by_plateau = {r['plateau_id']: r for r in R if r.get('plateau_id') and r['geometry'] == 'plateau_lod2'}

# buildings with their own asset (assets/buildings/*): QFRONT, MAGNET (its PLATEAU solid also holds the Eiraku roof)
OWN_ASSETS = {'way/136691386': 'qfront', 'way/116806281': 'magnet + eiraku', 'way/136690966': 'west-block'}
# subway entrance canopies are drawn by the street asset (assets/street/core)
ENTRANCES = {f['id'] for f in street['features'] if f['kind'] == 'entrance'}
ENTRANCE_RINGS = [f['ring'] for f in street['features'] if f['kind'] == 'entrance']


def inside(x, y, ring):
    c = False
    for i in range(len(ring)):
        (x1, y1), (x2, y2) = ring[i], ring[i - 1]
        if (y1 > y) != (y2 > y) and x < (x2 - x1) * (y - y1) / (y2 - y1) + x1:
            c = not c
    return c


def is_entrance(cx, cy, height):
    # PLATEAU also models the canopies as low buildings; the street asset draws them
    return height < 5 and any(inside(cx, cy, r) or min(math.hypot(cx - p[0], cy - p[1]) for p in r) < 2.0 for r in ENTRANCE_RINGS)
# station side: shape must be checked against 2025-10 photographs before production (DECISIONS 2026-10-12)
STATION_WORDS = ('駅舎', '駅関連', '駅施設', '渋谷駅の高架部', '改札内', 'train_station')


def group_of(rec):
    if rec is None:
        return 'core'
    note = rec.get('name', '') + ' ' + reg.get(rec['id'], {}).get('identity_note', '') + ' ' + rec.get('building', '')
    return 'station' if any(w in note for w in STATION_WORDS) else 'core'


out = {'source': P['_meta']['source'], 'datum_tp_m': DATUM, 'radius_m': RADIUS, 'excluded': [], 'buildings': []}
for b in P['buildings']:
    pts = [p for s in b['surfaces'] for p in s['ring']]
    cx = sum(p[0] for p in pts) / len(pts); cy = sum(p[1] for p in pts) / len(pts)
    if math.hypot(cx - CENTRE[0], cy - CENTRE[1]) > RADIUS:
        continue
    rec = by_plateau.get(b['gml_id'])
    rid = rec['id'] if rec else 'plateau/' + b['gml_id']
    if rid in OWN_ASSETS or rid in ENTRANCES or is_entrance(cx, cy, b['top_tp'] - b['ground_tp']):
        out['excluded'].append({'id': rid, 'plateau_id': b['gml_id'], 'reason': ('own asset: ' + OWN_ASSETS[rid]) if rid in OWN_ASSETS else 'street asset entrance'})
        continue
    out['buildings'].append({'id': rid, 'plateau_id': b['gml_id'], 'kind': 'building', 'name': rec['name'] if rec else '', 'group': group_of(rec),
                             'ground_tp': b['ground_tp'], 'top_tp': b['top_tp'],
                             'surfaces': [{'kind': s['kind'], 'ring': [[round(p[0], 3), round(p[1], 3), round(p[2] - DATUM, 3)] for p in s['ring']]}
                                          for s in b['surfaces'] if s['kind'] != 'GroundSurface']})
for g in P['bridges']:
    pts = [p for s in g['surfaces'] for p in s['ring']]
    if min(math.hypot(p[0] - CENTRE[0], p[1] - CENTRE[1]) for p in pts) > RADIUS:
        continue
    out['buildings'].append({'id': 'brid/' + g['gml_id'], 'plateau_id': g['gml_id'], 'kind': 'structure', 'name': g['function_ja'] or '', 'group': 'core',
                             'ground_tp': g['z_min_tp'], 'top_tp': g['z_max_tp'],
                             'surfaces': [{'kind': s['kind'], 'ring': [[round(p[0], 3), round(p[1], 3), round(p[2] - DATUM, 3)] for p in s['ring']]} for s in g['surfaces']]})
json.dump(out, open(out_path, 'w'), ensure_ascii=False, separators=(',', ':'))
from collections import Counter
print(len(out['buildings']), Counter((b['kind'], b['group']) for b in out['buildings']), 'excluded', [(e['id'], e['reason']) for e in out['excluded']])
for b in out['buildings']:
    if b['group'] == 'station': print('  station:', b['id'], b['name'], round(b['top_tp'] - b['ground_tp'], 1))
