# Reuses identical hash-checked Blender imports and surface-contact diagnostics.
from pathlib import Path
exec((Path(__file__).parent/'render-assembly.py').read_text().split('for m in bpy.data.materials:')[0])
def hull(points):
 p=sorted(set((float(v[0]),float(v[1])) for v in points))
 def cross(o,a,b):return (a[0]-o[0])*(b[1]-o[1])-(a[1]-o[1])*(b[0]-o[0])
 lo=[];hi=[]
 for v in p:
  while len(lo)>=2 and cross(lo[-2],lo[-1],v)<=0:lo.pop()
  lo.append(v)
 for v in reversed(p):
  while len(hi)>=2 and cross(hi[-2],hi[-1],v)<=0:hi.pop()
  hi.append(v)
 return lo[:-1]+hi[:-1]
def separation(pa,pb):
 a,b=hull(pa),hull(pb);best={'separating_gap_m':-1e99}
 for poly in [a,b]:
  for i,v in enumerate(poly):
   w=poly[(i+1)%len(poly)];dx,dy=w[0]-v[0],w[1]-v[1];n=math.hypot(dx,dy);axis=(-dy/n,dx/n)
   A=[x*axis[0]+y*axis[1] for x,y in a];B=[x*axis[0]+y*axis[1] for x,y in b]
   gap=max(min(A)-max(B),min(B)-max(A))
   if gap>best['separating_gap_m']:best={'separating_gap_m':gap,'unit_plan_axis':axis,'interval_a':[min(A),max(A)],'interval_b':[min(B),max(B)]}
 best.update(projected_convex_hulls_disjoint=best['separating_gap_m']>1e-6,hull_a=a,hull_b=b)
 return best
points=lambda bid:[o.matrix_world@v.co for o in groups[bid] for v in o.data.vertices]
final=separation(points('west-block'),points('quattro'))
west=json.loads((root/'assets/buildings/west-block/source/data/plateau.json').read_text())
q=json.loads((root/'assets/buildings/quattro/source/data/original_shell.json').read_text())
wp=[p for s in west['surfaces'] for p in s['ring']];qp=[p for s in q.values() for p in s['vertices']]
source=separation(wp,qp)
report={'method':'2D convex-hull separating-axis test on ALL imported mesh vertices, including signs and every decoration. A positive separating axis proves disjoint projected convex envelopes, thus excludes triangle contact and any solid containment, including non-watertight meshes. No ray-parity assumption is required.','final_assets':final,'original_source_shells':source,'source_note':'West original PLATEAU surface XY versus BIG ECHO exact original shell XY. These baseline files are hashed in separation-input-manifest.json.','conclusion':'Projected envelopes are strictly separated: AABB overlap is a false positive. No geometry change recommended.' if final['projected_convex_hulls_disjoint'] else 'Hull overlap inconclusive: need triangle and closed-solid containment investigation.'}
(out/'geometry-separation.json').write_text(json.dumps(report,indent=2))
items=[]
for rel in ['assets/buildings/west-block/source/data/plateau.json','assets/buildings/quattro/source/data/original_shell.json']:
 d=(root/rel).read_bytes();items.append({'path':rel,'bytes':len(d),'sha256':hashlib.sha256(d).hexdigest()})
(out/'separation-input-manifest.json').write_text(json.dumps({'inputs':items},indent=2))
print('FINAL_SEPARATION',final['separating_gap_m'],'SOURCE_SEPARATION',source['separating_gap_m'])
