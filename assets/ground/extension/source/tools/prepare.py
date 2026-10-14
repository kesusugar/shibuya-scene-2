from pathlib import Path
import math,json,sys,numpy as np
from shapely.geometry import Polygon,box,Point
from shapely.ops import unary_union,triangulate,nearest_points
from shapely.strtree import STRtree
from scipy.spatial import cKDTree
P=Path(sys.argv[1]);old=json.loads(Path(sys.argv[2]).read_text());polys=[Polygon([p[:2] for p in t]) for t in old];mask=unary_union([p for p in polys if p.is_valid and p.area>1e-8]).buffer(.002)
points=np.array([p for t in old for p in t]);tree=cKDTree(points[:,:2]);surface_tree=STRtree(polys);S=json.loads((P/'source.json').read_text());DEM={}
for dx in [0,1]:
 for dy in [0,1]:
  x,y=S['x']+dx,S['y']+dy;path=P/('dem.txt' if dx==dy==0 else f'{x}-{y}.txt');DEM[x,y]=np.genfromtxt(path,delimiter=',',missing_values='e',filling_values=np.nan)
kx=math.cos(math.radians(35.6595))*111320;ky=110574
missing=0

def height(x,y):
 global missing
 lon=139.7005+x/kx;lat=35.6595+y/ky;tx=(lon+180)/360*2**15;ty=(1-math.asinh(math.tan(math.radians(lat)))/math.pi)/2*2**15
 key=(int(tx),int(ty));a=DEM[key];u=(tx-key[0])*256;v=(ty-key[1])*256;i=min(254,int(u));j=min(254,int(v));fu=u-i;fv=v-j
 q=a[j:j+2,i:i+2];weights=np.array([[(1-fu)*(1-fv),fu*(1-fv)],[(1-fu)*fv,fu*fv]])
 good=np.isfinite(q)
 if not good.any():missing+=1;raise ValueError((x,y,'no DEM'))
 h=float(np.sum(np.where(good,q,0)*weights)/np.sum(good*weights));dist=mask.distance(Point(x,y))
 if dist<20:
  idx=int(surface_tree.nearest(Point(x,y)));q=nearest_points(Point(x,y),polys[idx])[1];t=np.array(old[idx]);a=t[0,:2];u=t[1,:2]-a;v=t[2,:2]-a;weights2=np.linalg.solve(np.column_stack((u,v)),np.array([q.x,q.y])-a);near=float(t[0,2]+weights2[0]*(t[1,2]-t[0,2])+weights2[1]*(t[2,2]-t[0,2]));f=min(1,dist/20);h=near*(1-f)+h*f
 return round(h,4)
tri=[]
for x in range(-330,380,6):
 for y in range(-450,350,6):
  cell=box(x,y,min(x+6,380),min(y+6,350)).difference(mask)
  if cell.is_empty:continue
  for p in (cell.geoms if hasattr(cell,'geoms') else [cell]):
   if p.geom_type!='Polygon' or p.area<1e-5:continue
   for t in triangulate(p):
    if not p.covers(t.representative_point()):continue
    for clipped in [t.intersection(p)]:
     if clipped.geom_type!='Polygon' or clipped.area<1e-5:continue
     ring=list(clipped.exterior.coords)[:-1]
     # intersection can have more than three vertices: triangulate again and constrain.
     for final in triangulate(clipped):
      if not clipped.covers(final.representative_point()) or final.area<1e-5:continue
      tri.append([[round(a,4),round(b,4),height(a,b)] for a,b in list(final.exterior.coords)[:3]])
stats={'source':'GSI DEM5A','source_acquired':'2026-10-13','datum_tp_m':15,'bounds_m':[-330,-450,380,350],'grid_m':6,'edge_blend_m':20,'source_ground_unchanged':True,'triangles':len(tri),'missing_dem':missing,'height_tp_range':[min(p[2] for t in tri for p in t),max(p[2] for t in tri for p in t)],'limitation':'DEM terrain substrate; finished street surfaces/roads are not surveyed. Blend at original ground seam is estimated, not source DEM.'}
(P/'extension.json').write_text(json.dumps({'triangles':tri,'stats':stats},separators=(',',':'))+'\n');(P/'stats.json').write_text(json.dumps(stats,indent=1)+'\n');print(stats)
