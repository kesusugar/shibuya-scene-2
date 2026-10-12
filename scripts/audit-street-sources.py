"""Cross-check authoring coordinates against the retained October 2025 OSM response; no network required."""
import json, math, hashlib, sys
from pathlib import Path
from shapely.geometry import Polygon, Point
base=Path('assets/street/core/source/data'); source=base/'osm_2025.json'
H=json.loads(source.read_text()); D=json.loads((base/'street_input.json').read_text())
assert D['source_sha256']==hashlib.sha256(source.read_bytes()).hexdigest()
rows={(e['type']+'/'+str(e['id'])):e for e in H['elements']}
def xy(e):
    k=6378137*math.pi/180
    return ((e['lon']-139.7005)*k*math.cos(math.radians(35.6595)),(e['lat']-35.6595)*k)
result=[]
for f in D['features']:
    e=rows[f['id']]
    if f['kind']=='tree': delta=Point(f['point']).distance(Point(xy(e)))
    else: delta=Polygon(f['ring']).hausdorff_distance(Polygon([xy(p) for p in e['geometry']]))
    assert delta<0.001,(f['id'],delta)
    result.append({'id':f['id'],'kind':f['kind'],'difference_from_retained_2025_osm_m':round(delta,6),'identity':f.get('identity')})
output={'query_date':H['query_date'],'sha256':D['source_sha256'],'features':result,'max_difference_m':max(r['difference_from_retained_2025_osm_m'] for r in result),
        'limitations':'Agreement with a retained map coordinate does not prove photo agreement or physical survey accuracy.'}
p=Path(sys.argv[1]);p.parent.mkdir(parents=True,exist_ok=True);p.write_text(json.dumps(output,ensure_ascii=False,indent=2)+'\n')
print(len(result),'features; max map-coordinate difference',output['max_difference_m'],'m')
