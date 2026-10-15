"""Exact serialized triangle multiset regression: only redundant core_base omitted from approved terrace geometry."""
from pathlib import Path
import json,numpy as np,struct,hashlib
from collections import Counter
from glb_io import *
ROOT=Path(__file__).resolve().parents[1];a,ab=read(ROOT/'inputs/frozen-terrace-additions.glb');b,bb=read(ROOT/'geometry/additions.glb')
def triangles(d,buf,m):
 p=m['primitives'][0];v=acc(d,buf,p['attributes']['POSITION']);idx=acc(d,buf,p['indices']).reshape(-1,3)
 return [tuple(sorted(tuple(float(x)for x in row)for row in v[ix]))for ix in idx]
A={m['name']:triangles(a,ab,m)for m in a['meshes']};B={m['name']:triangles(b,bb,m)for m in b['meshes']};oldlog=json.loads((ROOT/'inputs/frozen-terrace-components.json').read_text());newlog=json.loads((ROOT/'geometry/component-log.json').read_text());expected=[c for c in oldlog if c['label']!='core_base'];assert newlog==expected,'Unexpected geometry component delta'
rows=[]
for name,old in A.items():
 ca,cb=Counter(old),Counter(B[name]);removed=list((ca-cb).elements());added=list((cb-ca).elements());ok=(not added and not removed)if name!='prototype_terrace_floor'else(not added and len(removed)==20)
 if name=='prototype_terrace_floor':
  # core_wrap_4F_floor is second slab in the fixed component-order export; each7vertex prism contributes24triangles.
  floorlogs=[c for c in oldlog if c['material']=='floor'];offset=0;target=[]
  for c in floorlogs:
   count=4*len(c['plan'])-4
   if c['label']=='core_wrap_4F_floor':target=old[offset:offset+count];break
   offset+=count
  assert len(target)==24 and not(Counter(target)-cb),'Retained core-wrap floor triangles changed or absent'
  # Worldz=glTFy; all omitted triangles are inside the old duplicate slab's height band.
  z=[p[1]for tr in removed for p in tr];ok &= abs(min(z)-25.128)<1e-5 and abs(max(z)-25.378)<1e-5
 rows.append({'mesh':name,'removed_triangle_count':len(removed),'added_triangle_count':len(added),'pass':ok})
report={'candidate_sha256':hashlib.sha256((ROOT/'parco_terrace_candidate.glb').read_bytes()).hexdigest(),'component_log_equals_frozen_minus_only_core_base':newlog==expected,'retained_core_wrap_floor_24_serialized_triangles_exact':True,'all_other_added_geometry_triangles_exact':all(r['pass']for r in rows),'meshes':rows,'scope':'Material values/names may change only on new terrace geometry. Base roof22 is separately preserved. No other primitive geometry flattened or omitted.'};(ROOT/'verification/terrace-delta.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps(report,indent=2));assert report['all_other_added_geometry_triangles_exact']
