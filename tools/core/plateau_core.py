# Gate C0 supplement: read PLATEAU 2025 CityGML around the crossing into one JSON (plan metres, heights in T.P.).
#   python3 tools/core/plateau_core.py <plateau_dir> <out.json> [radius_m=320]
# plateau_dir holds the 53393596 tile files (bldg, brid, frn, veg, tran) plus neighbouring bldg tiles and codelists/.
# Buildings and bridges keep every LOD2 surface polygon (LOD1 solid when there is no LOD2) so stepped towers and
# viaducts are not turned into full-height prisms; furniture and trees keep a centroid, height range and code.
# Read-only; positions use the same origin and axes as the old project (lat 35.6595, lon 139.7005; X east, Y north).
import re, math, json, sys, os, glob

src, out = sys.argv[1:3]; R = float(sys.argv[3]) if len(sys.argv) > 3 else 320.0
lat0, lon0 = 35.6595, 139.7005
kx = math.cos(math.radians(lat0)) * 111320.0; ky = 110574.0
CX, CY = 6.5, -2.0                                     # crossing centre node/291758776

def codes(name):
    t = open(os.path.join(src, 'codelists', name + '.xml'), encoding='utf-8').read()
    return {m.group(2): m.group(1) for m in re.finditer(r'<gml:description>([^<]*)</gml:description>\s*<gml:name[^>]*>([^<]*)</gml:name>', t)}

def rings(block):
    for p in re.findall(r'<gml:posList[^>]*>([^<]+)</gml:posList>', block):
        v = list(map(float, p.split()))
        yield [[round((v[i + 1] - lon0) * kx, 3), round((v[i] - lat0) * ky, 3), round(v[i + 2], 3)] for i in range(0, len(v) - 2, 3)]

def near(polys):
    return any(math.hypot(x - CX, y - CY) <= R for poly in polys for x, y, _ in poly)

def members(path):
    t = open(path, encoding='utf-8').read()
    for m in re.finditer(r'<core:cityObjectMember>(.*?)</core:cityObjectMember>', t, re.S):
        yield m.group(1)

def tag(block, name):
    m = re.search(r'<%s[^>]*>([^<]*)</%s>' % (name, name), block); return m.group(1) if m else None

def lod2_or_1(block, prefix):
    surf = []
    for kind in ('RoofSurface', 'WallSurface', 'GroundSurface', 'OuterFloorSurface', 'OuterCeilingSurface', 'ClosureSurface'):
        for s in re.finditer(r'<%s:%s.*?</%s:%s>' % (prefix, kind, prefix, kind), block, re.S):
            surf += [{'kind': kind, 'ring': r} for r in rings(s.group(0))]
    if surf: return 'lod2', surf
    m = re.search(r'<%s:lod1Solid>.*?</%s:lod1Solid>' % (prefix, prefix), block, re.S)
    return ('lod1', [{'kind': 'solid', 'ring': r} for r in rings(m.group(0))]) if m else (None, [])

out_d = {'_meta': {'origin': [lat0, lon0], 'axes': 'X east, Y north (m); z = T.P. metres', 'radius_m': R, 'centre': [CX, CY],
                   'source': 'PLATEAU 2025 Shibuya-ku CityGML (13113_shibuya-ku_pref_2025_citygml_1_op)'}}
# buildings: every tile file present
bl = []
for path in sorted(glob.glob(os.path.join(src, '*_bldg.gml'))):
    for b in members(path):
        if '<bldg:Building' not in b: continue
        lod, surf = lod2_or_1(b, 'bldg')
        if not surf or not near([s['ring'] for s in surf]): continue
        zs = [p[2] for s in surf for p in s['ring']]
        gz = [p[2] for s in surf if s['kind'] == 'GroundSurface' for p in s['ring']]
        bl.append({'gml_id': re.search(r'gml:id="([^"]+)"', b).group(1), 'tile': os.path.basename(path)[:8], 'lod': lod,
                   'measuredHeight': float(tag(b, 'bldg:measuredHeight') or 0), 'ground_tp': min(gz or zs), 'top_tp': max(zs), 'surfaces': surf})
out_d['buildings'] = bl
# bridges (pedestrian overpasses, viaducts)
BF = codes('Bridge_function'); br = []
for b in members(os.path.join(src, '53393596_brid.gml')):
    lod, surf = lod2_or_1(b, 'brid')
    if not surf or not near([s['ring'] for s in surf]): continue
    zs = [p[2] for s in surf for p in s['ring']]
    fn = tag(b, 'brid:function')
    br.append({'gml_id': re.search(r'gml:id="([^"]+)"', b).group(1), 'function': fn, 'function_ja': BF.get(fn), 'name': tag(b, 'gml:name'),
               'lod': lod, 'z_min_tp': min(zs), 'z_max_tp': max(zs), 'surfaces': surf})
out_d['bridges'] = br
# city furniture and trees: centroid, height range, code
FF, FC = codes('CityFurniture_function'), codes('CityFurniture_class')
def point_items(path, prefix, kindtag):
    items = []
    for b in members(path):
        rs = list(rings(b))
        if not rs or not near(rs): continue
        pts = [p for r in rs for p in r]
        items.append({'gml_id': re.search(r'gml:id="([^"]+)"', b).group(1), 'type': kindtag(b),
                      'x': round(sum(p[0] for p in pts) / len(pts), 2), 'y': round(sum(p[1] for p in pts) / len(pts), 2),
                      'z_min_tp': min(p[2] for p in pts), 'z_max_tp': max(p[2] for p in pts)})
    return items
out_d['furniture'] = point_items(os.path.join(src, '53393596_frn.gml'), 'frn',
                                 lambda b: {'function': tag(b, 'frn:function'), 'function_ja': FF.get(tag(b, 'frn:function')), 'class_ja': FC.get(tag(b, 'frn:class'))})
out_d['vegetation'] = point_items(os.path.join(src, '53393596_veg.gml'), 'veg',
                                  lambda b: {'kind': 'SolitaryVegetationObject' if 'SolitaryVegetationObject' in b else 'PlantCover', 'height': tag(b, 'veg:height')})
# road surfaces (LOD3 traffic areas keep their polygons; they are the ground of the Core)
TF, AF = codes('TrafficArea_function'), codes('AuxiliaryTrafficArea_function'); ta = []
t = open(os.path.join(src, '53393596_tran.gml'), encoding='utf-8').read()
for m in re.finditer(r'<tran:(TrafficArea|AuxiliaryTrafficArea)\b.*?</tran:\1>', t, re.S):
    blk = m.group(0); fn = tag(blk, 'tran:function'); lod = None
    for lv in ('lod3', 'lod2'):                       # one LOD only, so surfaces are not doubled
        g = re.search(r'<tran:%sMultiSurface>.*?</tran:%sMultiSurface>' % (lv, lv), blk, re.S)
        if g: lod = lv; rs = list(rings(g.group(0))); break
    if not lod or not rs or not near(rs): continue
    ta.append({'kind': m.group(1), 'lod': lod, 'function': fn, 'function_ja': (TF if m.group(1) == 'TrafficArea' else AF).get(fn), 'rings': rs})
out_d['traffic_areas'] = ta
json.dump(out_d, open(out, 'w'))
print('buildings', len(bl), 'bridges', len(br), 'furniture', len(out_d['furniture']), 'vegetation', len(out_d['vegetation']), 'traffic areas', len(ta))
