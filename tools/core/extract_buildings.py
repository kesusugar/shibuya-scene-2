# Gate C0: one record per OSM building (all 666) from the old project's data, in Blender plan axes.
#   python3 tools/core/extract_buildings.py <old shibuya-scene-data.json> <old_building_model.json> <out.json>
# Read-only use of the old data. Height: PLATEAU LOD2 top (relative), else OSM/PLATEAU height, else levels x 3.4 m,
# else 9 m (flagged). Holes (courtyards) are ignored for the visibility prisms.
import json, sys, math
data, model, out = sys.argv[1:4]
d = json.load(open(data)); m = json.load(open(model))
generic = set(m['generic']); reserved = {r['id']: r['reason'] for r in m['reserved']}
skipped = {}
for s in m['skipped']: skipped.setdefault(s['key'].rsplit(':', 1)[0], s['reason'])
recs = {}
for b in d['buildings']:
    pid = b['id']; t = b['tags']; pl = b.get('plateau') or {}
    ring = [[round(p[0], 3), round(-p[1], 3)] for p in b['polygon']['outer']]
    if pid in reserved: old = 'dedicated_hero' if reserved[pid] == 'hero-definition' else reserved[pid]
    elif pid in generic: old = 'generic'
    elif pid in skipped: old = 'raw_data:' + skipped[pid]
    else: old = 'unknown'
    h = pl.get('top') or b.get('height') or pl.get('h')
    src = 'plateau_top' if pl.get('top') else ('height' if h else None)
    if not h and b.get('levels'): h = b['levels'] * 3.4; src = 'levels_x3.4'
    if not h: h = 9.0; src = 'default_9m'
    r = recs.setdefault(pid, {'id': pid, 'name': t.get('name') or t.get('name:ja') or '', 'name_en': t.get('name:en', ''),
                              'building': t.get('building', ''), 'plateau_id': pl.get('id', ''), 'measuredHeight': pl.get('h'),
                              'plateau_top': pl.get('top'), 'height_used': h, 'height_source': src, 'old_status': old, 'parts': []})
    r['parts'].append(ring)
for r in recs.values():
    xs = [p[0] for ring in r['parts'] for p in ring]; ys = [p[1] for ring in r['parts'] for p in ring]
    r['centroid'] = [round(sum(xs) / len(xs), 2), round(sum(ys) / len(ys), 2)]
    r['dist_from_crossing_m'] = round(math.hypot(r['centroid'][0] - 6.5, r['centroid'][1] + 2.0), 1)   # crossing node/291758776
json.dump(list(recs.values()), open(out, 'w'), ensure_ascii=False)
print('buildings', len(recs), 'parts', sum(len(r['parts']) for r in recs.values()))
