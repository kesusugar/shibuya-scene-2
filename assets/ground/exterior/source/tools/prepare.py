from pathlib import Path
import json,math,numpy as np
from shapely.geometry import Polygon,Point,box,LineString
from shapely.ops import unary_union,triangulate
from shapely import segmentize
import sys
P=Path(sys.argv[1]);D=json.load(open(P/'traffic.json'));OLD=json.load(open(sys.argv[2]));old_mask=unary_union([Polygon([p[:2] for p in t]) for t in OLD]).buffer(.02);scope=box(-330,-450,380,350);CLASS={'車道部':'road','車道交差部':'intersection','歩道部':'sidewalk','島':'island'}
cover3=unary_union([Polygon([p[:2] for p in q['exterior']],[[p[:2] for p in h] for h in q['interiors']]).buffer(0) for a in D['traffic_areas'] if a['lod']=='lod3' for q in a['polygons']]);surfaces=[]
for a in D['traffic_areas']:
 for q in a['polygons']:
  ring=q['exterior'];holes=q['interiors']
  zmap={(p[0],p[1]):p[2] for r in [ring,*holes] for p in r};poly=Polygon([p[:2] for p in ring],[[p[:2] for p in h] for h in holes]).buffer(0)
  if poly.is_empty:continue
  usable=poly.intersection(scope).difference(old_mask)
  if a['lod']=='lod2':usable=usable.difference(cover3)
  if usable.is_empty or usable.area<.001:continue
  # Triangulate the supplied ring first, retaining each source vertex height.
  for tri in triangulate(poly):
   if tri.difference(poly).area>1e-8 or tri.area<1e-8:continue
   pts=list(tri.exterior.coords)[:3];zz=[zmap[p] for p in pts];q=tri.intersection(usable)
   for part in ([q] if q.geom_type=='Polygon' else getattr(q,'geoms',[])):
    if part.geom_type!='Polygon' or part.area<1e-5:continue
    # Source triangles and clipping polygons generally have convex intersections.
    for t in triangulate(part):
     if t.difference(part).area>1e-8 or t.area<1e-5:continue
     source=np.array(pts);matrix=np.column_stack((source[1]-source[0],source[2]-source[0]));r=[]
     for x,y in list(t.exterior.coords)[:3]:
      weights=np.linalg.solve(matrix,np.array([x,y])-source[0]);z=zz[0]+weights[0]*(zz[1]-zz[0])+weights[1]*(zz[2]-zz[0]);r.append([round(x,5),round(y,5),round(z,5)])
     surfaces.append({'class':CLASS[a['function_ja']],'lod':a['lod'],'ring':r})
road=unary_union([Polygon([p[:2] for p in s['ring']]) for s in surfaces if s['class'] in ['road','intersection']]);CW=json.load(open(sys.argv[3]));bands=[]
for c in CW['crosswalks']:
 if c.get('osm_markings')=='no' or c.get('osm_crossing')=='unmarked':continue
 points=c.get('points_measured') or c['points'];line=LineString(points);w=c['width_m'] if c['status']=='measured' else 4
 p0,p1=points[:2];q0,q1=points[-2:];l=math.dist(p0,p1);m=math.dist(q0,q1)
 ext=LineString([[p0[0]-(p1[0]-p0[0])/l*3,p0[1]-(p1[1]-p0[1])/l*3],*points[1:-1],[q1[0]+(q1[0]-q0[0])/m*3,q1[1]+(q1[1]-q0[1])/m*3]]);band=ext.buffer(w/2,cap_style='flat',join_style='mitre');area=band.intersection(road).area
 if area>.05:bands.append({'id':c['id'],'width_m':w,'width_source':'orthophoto' if c['status']=='measured' else 'default','band':band,'line':ext,'area':area})
bands.sort(key=lambda b:-b['area']);kept=[]
for b in bands:
 if any(b['band'].intersection(k['band']).area>.5*min(b['band'].area,k['band'].area) for k in kept):continue
 kept.append(b)
cross=[]
for b in kept:
 bars=[];n=int((b['width_m']+.45)//.9);start=-((n*.9-.45)/2)+.225
 for i in range(n):
  segments=[];offset=start+i*.9
  coords=list(b['line'].coords)
  for p,q in zip(coords,coords[1:]):
   dx,dy=q[0]-p[0],q[1]-p[1];length=math.hypot(dx,dy)
   if length<1e-4:continue
   nx,ny=-dy/length,dx/length;segments.append(LineString([[p[0]+nx*offset,p[1]+ny*offset],[q[0]+nx*offset,q[1]+ny*offset]]).buffer(.225,cap_style='flat'))
  g=unary_union(segments).intersection(road).difference(old_mask)
  for p in ([g] if g.geom_type=='Polygon' else getattr(g,'geoms',[])):
   if p.geom_type=='Polygon' and p.area>.05:
    for tri in triangulate(p):
     if tri.area>1e-6 and tri.difference(p).area<1e-8:bars.append([[round(x,5),round(y,5)] for x,y in list(segmentize(tri,1).exterior.coords)[:-1]])
 cross.append({'id':b['id'],'width_m':b['width_m'],'width_source':b['width_source'],'bars':bars,'band':list(b['band'].exterior.coords)[:-1]})
params={'radius_m':450,'kerb_height_m':.15,'kerb_low_m':.02,'landing_flat_m':1,'landing_ramp_m':1.5,'zebra_bar_m':.45,'zebra_gap_m':.45,'default_crosswalk_width_m':4,'fill_grid_m':6}
out={'params':params,'stats':{'surfaces':len(surfaces)},'source':{'plateau':'PLATEAU 2025 Shibuya four transport tiles; original Core excluded','crosswalks':CW['source'],'osm':CW['osm']},'surfaces':surfaces,'crosswalks':cross,'landings':[list(b['band'].exterior.coords)[:-1] for b in kept],'fill':[]}
(P/'input.json').write_text(json.dumps(out,separators=(',',':'))+'\n');print(len(surfaces),'source triangles',len(cross),'crossing bands',sum(len(c['bars']) for c in cross),'bars')
