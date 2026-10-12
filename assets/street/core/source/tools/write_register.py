"""Writes data/street_register_v2.csv from street_stats.json: one row per exported item with its basis.
python3 write_register.py street_stats.json street_layout.json out.csv"""
import csv, json, sys
S, L = json.load(open(sys.argv[1])), json.load(open(sys.argv[2]))
xy = {i['id']: i['xy'] for i in L['items']}
rows = []
for f in S['features']:
    if f['kind'] in ('entrance', 'tree'):
        p = f.get('point') or [round(sum(q[0] for q in f['ring']) / len(f['ring']), 3), round(sum(q[1] for q in f['ring']) / len(f['ring']), 3)]
        rows.append([f['id'], f['kind'], round(p[0], 3), round(p[1], 3), f['anchor_tp'], 'OSM 2025-10-31 (position)', f['shape_status']])
    else:
        p = xy[f['id']]
        rows.append([f['id'], f['kind'], p[0], p[1], f['anchor_tp'], f['placement'], 'generic standard-size model; not photo-measured'])
rows.append(['RAIL', 'kerb_railing', '', '', '', f"rule R3 ({S['rail_length_m']} m)", 'generic 横断防止柵 H0.8; alignment not surveyed'])
with open(sys.argv[3], 'w', newline='') as fh:
    w = csv.writer(fh); w.writerow(['id', 'kind', 'x_m', 'y_m', 'anchor_tp_m', 'position_basis', 'shape_status']); w.writerows(rows)
print(len(rows), 'rows')
