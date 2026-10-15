"""Sample pinned existing extension ground; no ground edits. Run with extension.glb path."""
import sys,json,math
from pathlib import Path
from glb_helpers import load,acc,to_blender,sha
ROOT=Path(__file__).resolve().parents[1];path=Path(sys.argv[1]);j,b=load(path);C=(-129.0380165156,6.9354800658);N=(.998716,-.050703);R=(.050703,.998716);L=math.hypot(*N);N=tuple(x/L for x in N);R=tuple(x/L for x in R)
points={}
for o,label in [(0,'rear'),(8.52,'front')]:
 for r,side in [(-3.2759,'left'),(3.2759,'right')]:points[label+'_'+side]=[C[k]+o*N[k]+r*R[k] for k in range(2)]
reg=json.loads((ROOT/'inputs/registration-proposal.json').read_text())['landmarks']
for n in ['stair_bottom_inner','stair_bottom_outer','stair_top_inner','stair_top_outer']:points[n]=reg[n]['proposed_blender_xy']
tris=[];context=[]
for mi,m in enumerate(j['meshes']):
 for pi,p in enumerate(m['primitives']):
  vs=[to_blender(v) for v in acc(j,b,p['attributes']['POSITION'])];ii=[i[0] for i in acc(j,b,p['indices'])]
  for k in range(0,len(ii),3):
   tri=[vs[i] for i in ii[k:k+3]];tris.append((mi,pi,k//3,tri))
   if all(-138<x<-114 and -1<y<19 for x,y,z in tri):context.append(tri)
result={}
for name,(x,y) in points.items():
 hits=[]
 for mi,pi,ti,(a,c,d) in tris:
  den=(c[1]-d[1])*(a[0]-d[0])+(d[0]-c[0])*(a[1]-d[1])
  if abs(den)<1e-8:continue
  u=((c[1]-d[1])*(x-d[0])+(d[0]-c[0])*(y-d[1]))/den;v=((d[1]-a[1])*(x-d[0])+(a[0]-d[0])*(y-d[1]))/den
  if min(u,v,1-u-v)>=-1e-7:hits.append({'mesh':mi,'primitive':pi,'triangle':ti,'z':u*a[2]+v*c[2]+(1-u-v)*d[2],'barycentric':[u,v,1-u-v],'triangle_xyz':[a,c,d]})
 if not hits:
  assert name.startswith('stair'),name
  result[name]={'xy':[x,y],'z':None,'hits':[],'status':'No containing extension triangle; no contact claim'};continue
 result[name]={'xy':[x,y],'z':max(h['z'] for h in hits),'hits':hits}
record={'ground_glb_sha256':sha(path.read_bytes()),'source_asset':'ground/extension/extension.glb','status':'Exact interpolation on unchanged existing ground_fill_extension. Model-ground contact, not surveyed pavement or full-scene validation. Core defaultfallback0.14 rejected; exteriorwest/middle/east nohits.','points':result}
(ROOT/'inputs/ground-contact.json').write_text(json.dumps(record,indent=2));(ROOT/'inputs/render-ground-context.json').write_text(json.dumps({'source_sha256':record['ground_glb_sha256'],'scope':'Read-only unchanged local source triangles; render-only, excluded from building GLB.','triangles':context},indent=2));print(json.dumps({k:v['z'] for k,v in result.items()},indent=2))
