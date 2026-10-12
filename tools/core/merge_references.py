# Gate C0: one reference register for the Core, in the pack's columns, from the per-building registers.
#   python3 tools/core/merge_references.py <out.csv> [seibu meta.json]
import csv, json, re, sys, os
out = sys.argv[1]; rows = []
def year(*s):
    m = re.search(r'(19|20)\d\d', ' '.join(x or '' for x in s)); return m.group(0) if m else ''
redis = lambda lic: 'yes (attribution' + (', share-alike' if 'sa' in lic else '') + ')' if lic.startswith('cc-by') else ('yes' if lic in ('cc-zero', 'pd') or lic.startswith('pd-') else 'no / unknown')
for bid, path in (('way/136691386', 'assets/buildings/qfront/source/refs/REFERENCE_REGISTER.csv'), ('way/116806281', 'assets/buildings/magnet/source/refs/REFERENCE_REGISTER.csv')):
    for r in csv.DictReader(open(path, encoding='utf-8-sig')):
        lic = (r.get('licence') or '').lower(); st = r.get('status', 'used')
        rows.append({'photo_id': r['id'], 'building_id': bid, 'captured_year': r.get('year') or year(r.get('date'), r.get('commons_file')),
                     'captured_date': (r.get('date') or '')[:19], 'angle': '', 'source_url': r['url'], 'photographer': (r.get('author') or '')[:80], 'license': lic,
                     'redistribution_allowed': redis(lic) if lic else 'no / unknown', 'fov_or_lens': '', 'vantage': (r.get('use') or r.get('kind_auto_approx') or '')[:80],
                     'reference_only': 'yes', 'verified': 'licence read from the Commons page wikitext' if lic else 'licence unknown - excluded',
                     'notes': st if 'status' in r else (r.get('era') or '')})
if len(sys.argv) > 2 and os.path.exists(sys.argv[2]):
    for k, v in json.load(open(sys.argv[2])).items():
        lic = ';'.join(v.get('license') or []).lower()
        rows.append({'photo_id': v['img'][:-4], 'building_id': 'way/55896465', 'captured_year': year(v.get('date'), v['file']), 'captured_date': (v.get('date') or '')[:19],
                     'angle': '', 'source_url': v['url'], 'photographer': (v.get('author') or '')[:80], 'license': lic, 'redistribution_allowed': redis(lic) if lic else 'no / unknown',
                     'fov_or_lens': '', 'vantage': '', 'reference_only': 'yes', 'verified': 'downloaded, not yet reviewed (branch claude/g4-seibu-a, uncommitted)' if v.get('http') == '200' else 'not downloaded (HTTP ' + str(v.get('http')) + ')',
                     'notes': 'Seibu Shibuya closed 2026-09-30: 2026 photos carry closing-sale signage, not 2025 signage'})
cols = ['photo_id', 'building_id', 'captured_year', 'captured_date', 'angle', 'source_url', 'photographer', 'license', 'redistribution_allowed', 'fov_or_lens', 'vantage', 'reference_only', 'verified', 'notes']
with open(out, 'w', newline='', encoding='utf-8-sig') as f:
    w = csv.DictWriter(f, fieldnames=cols); w.writeheader(); w.writerows(rows)
from collections import Counter
print(len(rows), Counter(r['building_id'] for r in rows), Counter(r['captured_year'][:3] + 'x' for r in rows))
