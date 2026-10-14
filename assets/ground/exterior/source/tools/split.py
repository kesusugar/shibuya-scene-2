from pathlib import Path
import sys,json,numpy as np
from shapely.geometry import Polygon,box
from shapely.ops import triangulate
base=Path(sys.argv[1]);core_tri=sys.argv[2];dem_dir=sys.argv[3];D=json.load(open(base/'input.json'))
# Treat zero T.P. in LOD2 as missing. Estimate from the same DEM/seam blend as the substrate.
scope={};prepare=Path(__file__).resolve().parents[3]/'extension/source/tools/prepare.py';sys.argv=['prepare',dem_dir,core_tri];exec(prepare.read_text().split('tri=[]')[0],scope)
count=0
for surf in D['surfaces']:
 for p in surf['ring']:
  if p[2]<=0:p[2]=scope['height'](p[0],p[1]);count+=1
if count or 'missing_tp_fallback' not in D['source']:D['source']['missing_tp_fallback']={'vertices':count,'method':'GSI DEM5A blended to protected Core streets; estimated height replaces zero source heights'}
(base/'input.json').write_text(json.dumps(D,separators=(',',':'))+'\n')
for name,x0,x1 in [('west',-330,-70),('middle',-70,150),('east',150,380)]:
 mask=box(x0,-450,x1,350);surfaces=[]
 for surf in D['surfaces']:
  ring=surf['ring'];poly=Polygon([p[:2] for p in ring]);clip=poly.intersection(mask)
  if clip.is_empty or clip.area<1e-6:continue
  source=np.array(ring);origin=source[0,:2];matrix=np.column_stack((source[1,:2]-origin,source[2,:2]-origin))
  for tri in triangulate(clip):
   if tri.difference(clip).area>1e-8 or tri.area<1e-6:continue
   r=[]
   for x,y in list(tri.exterior.coords)[:3]:
    u,v=np.linalg.solve(matrix,np.array([x,y])-origin);z=source[0,2]+u*(source[1,2]-source[0,2])+v*(source[2,2]-source[0,2]);r.append([x,y,z])
   surfaces.append({**surf,'ring':r})
 cs=[]
 for c in D['crosswalks']:
  bars=[]
  for bar in c['bars']:
   q=Polygon(bar).buffer(0).intersection(mask)
   if q.geom_type=='Polygon' and q.area>.01:bars.append(list(q.exterior.coords)[:-1])
  if bars:cs.append({**c,'bars':bars})
 part={**D,'surfaces':surfaces,'crosswalks':cs};tile=base.parents[2]/f'exterior-{name}'/'source/data';tile.mkdir(parents=True,exist_ok=True);(tile/'input.json').write_text(json.dumps(part,separators=(',',':'))+'\n');print(name,len(surfaces))
print('height fallback',count)
