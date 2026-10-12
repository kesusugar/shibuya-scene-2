# Gate C0 supplement: register of non-building structures and street furniture sources for the Core.
#   python3 tools/core/structure_register.py <old shibuya-scene-data.json> <plateau_core.json> <docs/core>
# Rows: PLATEAU bridges (viaducts, decks, footbridges), OSM elevated rail and deck ways within 150 m, the station
# corridor block, subway-entrance canopies, and one coverage row per furniture source (OSM vs PLATEAU frn).
import json, sys, os, csv, math
old_path, pl_path, out = sys.argv[1:4]
D = json.load(open(old_path)); P = json.load(open(pl_path))
HERE = os.path.dirname(os.path.abspath(__file__))
IDN = json.load(open(os.path.join(HERE, 'identity_notes.json'), encoding='utf-8'))
reg = {r['source_id']: r for r in csv.DictReader(open(os.path.join(out, 'ASSET_REGISTER_V2.csv'), encoding='utf-8-sig'))}
CX, CY = 6.5, -2.0
def plan(p): return p[0], -p[1]                       # old web points are [x, z] with z = south
def dmin(pts): return round(min(math.hypot(x - CX, y - CY) for x, y in pts), 1)
def zone(d): return 'Core' if d <= 50 else ('Middle' if d <= 150 else 'Background')
rows = []
def add(**k):
    base = {'structure_id': '', 'type': '', 'name_or_identity': '', 'source': '', 'dist_from_crossing_m': '', 'zone': '', 'z_min_tp': '', 'z_max_tp': '',
            'deck_tp': '', 'underside_tp': '', 'matches': '', 'rank_v2': '', 'visible_area_max': '', 'ss2_status': 'not_started', 'notes': ''}
    base.update(k); rows.append(base)
for b in P['bridges']:
    sid = 'brid/' + b['gml_id']; pts = [(p[0], p[1]) for s in b['surfaces'] for p in s['ring']]
    fl = [p[2] for s in b['surfaces'] if s['kind'] == 'OuterFloorSurface' for p in s['ring']]
    ce = [p[2] for s in b['surfaces'] if s['kind'] == 'OuterCeilingSurface' for p in s['ring']]
    d = dmin(pts); r = reg.get(sid, {})
    add(structure_id=sid, type='bridge/viaduct (PLATEAU brid, function: %s)' % b['function_ja'], name_or_identity=IDN.get(sid, ''), source='PLATEAU 2025 brid LOD2',
        dist_from_crossing_m=d, zone=zone(d), z_min_tp=b['z_min_tp'], z_max_tp=b['z_max_tp'], deck_tp=f'{min(fl)}-{max(fl)}' if fl else '',
        underside_tp=f'{min(ce)}-{max(ce)}' if ce else '', rank_v2=r.get('rank_v2', ''), visible_area_max=r.get('visible_area_max', ''),
        notes='geometry in visibility v2 (records_v2)')
for kind in ('rails', 'footways'):
    for w in D[kind]:
        t = w['tags']; layer = t.get('layer', '0')
        if not (t.get('bridge') or (layer not in ('0', '') and not layer.startswith('-'))): continue
        pts = [plan(p) for p in w['points']]; d = dmin(pts)
        if d > 150: continue
        add(structure_id=w['id'], type=('elevated rail' if kind == 'rails' else 'deck / elevated footway') + f" (bridge={t.get('bridge')}, layer={layer})",
            name_or_identity=t.get('name', ''), source='OSM (old data, fetched 2026-09-08)', dist_from_crossing_m=d, zone=zone(d),
            notes='line only: position/extent cross-check for the PLATEAU bridge rows; no height in OSM')
for sid in ('way/355250634', 'way/1333409445'):
    r = reg.get(sid, {})
    add(structure_id=sid, type='station corridor block' if sid == 'way/355250634' else 'deck (building=yes, man_made=bridge)',
        name_or_identity=r.get('name', '') + ' ' + IDN.get(sid, ''), source='OSM + PLATEAU bldg LOD2', dist_from_crossing_m=r.get('dist_from_crossing_m', ''),
        zone=zone(float(r.get('dist_from_crossing_m') or 999)), z_min_tp=r.get('ground_tp', ''), z_max_tp=r.get('top_tp', ''), rank_v2=r.get('rank_v2', ''),
        visible_area_max=r.get('visible_area_max', ''),
        notes=('OSM indoor=corridor, levels 2;3, building:min_level=1; PLATEAU models the block as a solid from the ground (15.41) to roofs 26.9-35.7, '
               'so an open ground floor is NOT shown by either source - to be checked on photos. REF-A stands 2.5 m inside its north face (window).')
        if sid == 'way/355250634' else 'PLATEAU ground 15.18, roof 25.9 (solid block in PLATEAU)')
for sid, idn in IDN.items():
    if '地下鉄出入口' in idn:
        r = reg.get(sid, {})
        add(structure_id=sid, type='subway entrance canopy', name_or_identity=idn, source='OSM building (levels x 3.4 m height)',
            dist_from_crossing_m=r.get('dist_from_crossing_m', ''), zone=zone(float(r.get('dist_from_crossing_m') or 999)), rank_v2=r.get('rank_v2', ''),
            visible_area_max=r.get('visible_area_max', ''), notes='height not measured; PLATEAU frn has no entrances inside 150 m (its 55 are outside the surveyed strip)')
# furniture sources: counts by zone, so the gap is explicit
def zc(items):
    z = {'Core': 0, 'Middle': 0, 'Background': 0}
    for x, y in items: z[zone(math.hypot(x - CX, y - CY))] += 1
    return z
osm = {'signals': [plan(s['point']) if 'point' in s else plan(s['points'][0]) for s in D['signals']], 'trees': [plan(s['point']) if 'point' in s else plan(s['points'][0]) for s in D['trees']]}
for k, pts in osm.items():
    z = zc(pts); add(structure_id=f'OSM:{k}', type='furniture source', source='OSM', zone='Core %d / Middle %d / Background %d' % (z['Core'], z['Middle'], z['Background']),
                     notes='OSM is known to be incomplete at the crossing (4 signals in the Core)')
from collections import defaultdict
byf = defaultdict(list)
for f in P['furniture']: byf[f['type']['function_ja']].append((f['x'], f['y']))
for k, pts in sorted(byf.items(), key=lambda kv: -len(kv[1])):
    z = zc(pts); add(structure_id=f'PLATEAU frn:{k}', type='furniture source', source='PLATEAU 2025 frn', zone='Core %d / Middle %d / Background %d' % (z['Core'], z['Middle'], z['Background']),
                     notes='PLATEAU frn is surveyed only along a strip about 100-200 m east (Meiji-dori); none inside 50 m')
cols = list(rows[0])
with open(os.path.join(out, 'STRUCTURE_REGISTER.csv'), 'w', newline='', encoding='utf-8-sig') as f:
    w = csv.DictWriter(f, fieldnames=cols); w.writeheader(); w.writerows(rows)
print(len(rows), 'rows')
