# Gate C0 supplement: how many Wikimedia Commons photos exist around the crossing, by year and licence.
#   python3 tools/core/commons_survey.py <out.json> [radius_m=250]
# Uses the public API politely: one request at a time, >= 4 s apart, exponential back-off on HTTP 429/5xx.
# A request that still fails is recorded as "unverified", never as "no photos". Nothing is downloaded but metadata.
# Sources: geotagged files near the crossing (list=geosearch, camera or object location) plus keyword searches for
# the C1 candidates. Year = EXIF DateTimeOriginal, else the file's DateTime metadata, else unknown.
import json, sys, time, re, urllib.request, urllib.parse, urllib.error

out = sys.argv[1]; R = int(sys.argv[2]) if len(sys.argv) > 2 else 250
API = 'https://commons.wikimedia.org/w/api.php'
UA = 'shibuya-scene-2-core-audit/1.0 (private research; reference survey, low rate)'
LAT, LON = 35.659480, 139.700559   # node/291758776 (crossing centre) - approximate
last = [0.0]; log = []

def call(params, tries=6):
    params = dict(params, format='json', formatversion='2')
    url = API + '?' + urllib.parse.urlencode(params)
    wait = 4.0
    for k in range(tries):
        dt = time.time() - last[0]
        if dt < 4.0: time.sleep(4.0 - dt)
        last[0] = time.time()
        try:
            with urllib.request.urlopen(urllib.request.Request(url, headers={'User-Agent': UA}), timeout=60) as r:
                return json.load(r)
        except urllib.error.HTTPError as e:
            log.append({'params': params, 'http': e.code, 'try': k})
            if e.code in (429, 500, 502, 503, 504):
                ra = e.headers.get('Retry-After'); time.sleep(float(ra) if ra and ra.isdigit() else wait); wait *= 2; continue
            return None
        except Exception as e:  # network
            log.append({'params': params, 'error': str(e), 'try': k}); time.sleep(wait); wait *= 2
    return None

files, status = {}, {}
# 1. geotagged files around the crossing (Commons caps radius at 10 km and limit at 500)
for prim in ('primary', 'all'):
    r = call({'action': 'query', 'list': 'geosearch', 'gscoord': f'{LAT}|{LON}', 'gsradius': R, 'gslimit': 500, 'gsnamespace': 6, 'gsprimary': prim})
    status[f'geosearch_{prim}'] = 'ok' if r else 'unverified'
    for g in (r or {}).get('query', {}).get('geosearch', []): files.setdefault(g['title'], {'via': set()})['via'].add('geo'); files[g['title']]['dist_m'] = g.get('dist')
# 2. keyword searches for the C1 candidates and the crossing itself
QUERIES = {'west_block': ['渋谷センター街 入口', 'Center Gai entrance Shibuya', '大盛堂 渋谷', 'Taiseido Shibuya'],
           'ekimae_bldg': ['渋谷駅前ビル', 'Shibuya Ekimae Building'],
           'crossing': ['Shibuya Crossing', '渋谷スクランブル交差点'],
           'station_side': ['Shibuya Station Hachiko exit', '渋谷駅 ハチ公口', 'Shibuya Mark City walkway']}
for key, qs in QUERIES.items():
    for q in qs:
        r = call({'action': 'query', 'list': 'search', 'srsearch': q, 'srnamespace': 6, 'srlimit': 100})
        status[f'search:{q}'] = ('ok total %d' % r['query']['searchinfo']['totalhits']) if r else 'unverified'
        for s in (r or {}).get('query', {}).get('search', []): files.setdefault(s['title'], {'via': set()})['via'].add(key)
# 3. metadata in batches of 50
titles = sorted(files)
for i in range(0, len(titles), 50):
    r = call({'action': 'query', 'titles': '|'.join(titles[i:i + 50]), 'prop': 'imageinfo', 'iiprop': 'extmetadata|size',
              'iiextmetadatafilter': 'DateTimeOriginal|DateTime|LicenseShortName|Artist|UsageTerms'})
    if not r: status[f'meta_batch_{i}'] = 'unverified'; continue
    for p in r['query']['pages']:
        ii = (p.get('imageinfo') or [{}])[0]; em = ii.get('extmetadata', {})
        dto = re.sub('<[^>]+>', '', em.get('DateTimeOriginal', {}).get('value', ''))
        m = re.search(r'(19|20)\d\d', dto); y = int(m.group(0)) if m else None
        files[p['title']].update(year=y, year_source='DateTimeOriginal' if y else 'unknown', licence=em.get('LicenseShortName', {}).get('value'),
                                 width=ii.get('width'), height=ii.get('height'))
for f in files.values(): f['via'] = sorted(f['via'])
json.dump({'status': status, 'failures': log, 'files': files}, open(out, 'w'), ensure_ascii=False, indent=0)
print('files', len(files), 'status', status)
