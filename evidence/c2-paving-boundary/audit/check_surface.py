import json,hashlib,math,sys
from pathlib import Path
import numpy as np
from shapely.geometry import Polygon,MultiPoint
from shapely.strtree import STRtree
from shapely.ops import unary_union
root=Path(sys.argv[1])
before=json.load(open(root/'before-triangles.json'));after=json.load(open(root/'after-triangles.json'))
def fingerprint(ts):
 return hashlib.sha256('\n'.join(sorted(';'.join(sorted(','.join(str(round(v*1e5)) for v in p) for p in t)) for t in ts)).encode()).hexdigest()
unchanged={name:fingerprint(ts)==fingerprint(after[name]) for name,ts in before.items() if name!='ground_sidewalk'}
assert all(unchanged.values()),unchanged
b=np.array(before['ground_sidewalk']);a=np.array(after['ground_sidewalk'])
polys=[Polygon(t[:,:2]) for t in b];tree=STRtree(polys)
max_error=0.;max_plane_error=0.;unmatched=0;exact_matches=0;nonvertical_matches=0
key=lambda t:tuple(sorted(tuple(round(float(v),5) for v in p) for p in t))
original_keys={key(t) for t in b}
for t in a:
 if key(t) in original_keys:
  exact_matches+=1;continue
 xy=t[:,:2];centroid=MultiPoint(xy).centroid
 best=math.inf;best_height=None
 for idx in tree.query(centroid.buffer(.00002)):
  bt=b[idx];normal=np.cross(bt[1]-bt[0],bt[2]-bt[0]);length=np.linalg.norm(normal)
  if length<1e-12:continue
  normal=normal/length;drop=int(np.argmax(abs(normal)));axes=[i for i in range(3) if i!=drop]
  if not Polygon(bt[:,axes]).buffer(.00002).covers(MultiPoint(t[:,axes])):continue
  err=max(abs((t-bt[0])@normal))
  if err<best:
   best=err;best_height=err/abs(normal[2]) if abs(normal[2])>=.1 else None
 if not math.isfinite(best):unmatched+=1
 else:
  max_plane_error=max(max_plane_error,best)
  if best_height is not None:max_error=max(max_error,best_height);nonvertical_matches+=1
# Unions test coverage, while summed triangle area also catches loss of overlapping source faces.
old_area=sum(p.area for p in polys);new_polys=[Polygon(t[:,:2]) for t in a]
new_area=sum(p.area for p in new_polys)
diff=unary_union(polys).symmetric_difference(unary_union(new_polys)).area
out={'baseline_commit':'3e99483','unchanged_other_parts':unchanged,'sidewalk_before_triangles':len(b),'sidewalk_after_triangles':len(a),'maximum_nonvertical_height_error_m':max_error,'maximum_triangle_plane_distance_m':max_plane_error,'exact_triangle_matches':exact_matches,'nonvertical_plane_matches':nonvertical_matches,'unmatched_after_triangles':unmatched,'summed_plan_area_before_m2':old_area,'summed_plan_area_after_m2':new_area,'coverage_symmetric_difference_m2':diff,'method':'Unchanged triangles matched at 10 micrometre quantization. Changed triangles matched to original 3D planes using dominant-axis projected coverage with 20 micrometre tolerance. Height error evaluated for abs(normal.z)>=0.1; near-vertical faces use 3D plane distance. Compare plan-area sum and union; other parts compared as triangle-coordinate multisets.'}
Path(sys.argv[2]).write_text(json.dumps(out,indent=2)+'\n')
print(json.dumps(out))
assert unmatched==0 and max_error<.0001 and max_plane_error<.00002 and abs(new_area-old_area)<.001 and diff<.001
