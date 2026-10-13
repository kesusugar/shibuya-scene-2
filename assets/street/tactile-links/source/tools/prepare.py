from pathlib import Path
import json,math,sys
from shapely.geometry import Polygon,Point,LineString
from shapely.ops import unary_union,triangulate
R=Path.cwd();routes=json.load(open(R/'assets/street/tactile-links/source/data/routes.json'));old=[]
def rectangle(c,d,w=.298,h=.298):
 u=[d[1],-d[0]];return Polygon([(c[0]+u[0]*x+d[0]*y,c[1]+u[1]*x+d[1]*y) for x,y in [(-w/2,-h/2),(w/2,-h/2),(w/2,h/2),(-w/2,h/2)]])
for path in ['assets/street/tactile/source/data/stats.json','assets/street/tactile-extra/source/data/stats.json']:
 for t in json.load(open(R/path))['tiles']:old.append(rectangle(t['centre_xy'],t['direction_xy'],.300,.300))
mask=unary_union(old);G=json.load(open(R/'assets/ground/core/source/data/ground_input.json'));walk=unary_union([Polygon([p[:2] for p in s['ring']]).buffer(0) for s in G['surfaces'] if s['class'] in ['sidewalk','island']]).buffer(-.001)
features=json.load(open(R/'assets/street/core/source/data/street_input.json'))['features'];blocks=[Polygon(f['ring']).buffer(.1) for f in features if f['kind']=='entrance'];blocks += [Point(*f['point']).buffer(.85) for f in features if f['kind']=='tree']
blocks += [Polygon(f['ring']).buffer(.25) for f in json.load(open(R/'assets/street/plaza-facilities/source/data/layout.json'))['items']];blocks += [LineString(run).buffer(.12) for run in json.load(open(R/'assets/street/core/source/data/street_layout.json'))['rail_runs']];walk=walk.difference(unary_union(blocks));faces=[];tiles=[];warns=[]
for r in routes['routes']:
 if not r.get('points'):continue
 a,b=r['points'][-2:];l=math.dist(a,b);d=[(b[0]-a[0])/l,(b[1]-a[1])/l];u=[d[1],-d[0]]
 for ix in [-.15,.15]:
  for iy in [-.15,.15]:
   c=[b[0]+u[0]*ix+d[0]*iy,b[1]+u[1]*ix+d[1]*iy];warns.append({'id':r['id'],'centre':c,'direction':d,'foot':rectangle(c,d)})
warn_mask=unary_union([w['foot'] for w in warns]);consumed=Polygon()
def parts(p):return [p] if p.geom_type=='Polygon' else [g for g in getattr(p,'geoms',[]) if g.geom_type=='Polygon']
def top(poly,dz):
 for p in parts(poly):
  for t in triangulate(p):
   if t.area<1e-9 or t.difference(p).area>1e-9:continue
   ring=list(t.exterior.coords)[:-1];cross=(ring[1][0]-ring[0][0])*(ring[2][1]-ring[0][1])-(ring[1][1]-ring[0][1])*(ring[2][0]-ring[0][0])
   if cross<0:ring.reverse()
   faces.append([[x,y,dz] for x,y in ring])
def prism(poly,bottom,upper):
 top(poly,upper)
 for p in parts(poly):
  for ring in [p.exterior,*p.interiors]:
   ps=list(ring.coords)
   for a,b in zip(ps,ps[1:]):faces.append([[a[0],a[1],bottom],[b[0],b[1],bottom],[b[0],b[1],upper],[a[0],a[1],upper]])
for w in warns:
 p=w['foot'].intersection(walk).difference(mask).difference(consumed)
 if p.area<.002:continue
 consumed=consumed.union(p);top(p,.002);c=w['centre'];d=w['direction'];u=[d[1],-d[0]]
 for ix in range(5):
  for iy in range(5):
   x=(ix-2)*.06;y=(iy-2)*.06;cc=[c[0]+u[0]*x+d[0]*y,c[1]+u[1]*x+d[1]*y];dot=Point(*cc).buffer(.007,resolution=2).intersection(p);prism(dot,.002,.007)
 tiles.append({'group':w['id'],'kind':'warning','centre_xy':c,'direction_xy':d,'rendered_area_m2':p.area})
for r in routes['routes']:
 for a,b in zip(r.get('points',[])[:-1],r.get('points',[])[1:]):
  l=math.dist(a,b);d=[(b[0]-a[0])/l,(b[1]-a[1])/l]
  for k in range(math.ceil(l/.3)):
   c=[a[0]+d[0]*(.15+k*.3),a[1]+d[1]*(.15+k*.3)];p=rectangle(c,d).intersection(walk).difference(mask).difference(warn_mask).difference(consumed)
   if p.area<.002:continue
   consumed=consumed.union(p);top(p,.002);u=[d[1],-d[0]]
   for ix in range(4):
    cc=[c[0]+u[0]*(ix-1.5)*.06,c[1]+u[1]*(ix-1.5)*.06];bar=rectangle(cc,d,.017,.27).intersection(p);prism(bar,.002,.007)
   tiles.append({'group':r['id'],'kind':'guide','centre_xy':c,'direction_xy':d,'rendered_area_m2':p.area})
assert consumed.intersection(mask).area<1e-6
D={'faces':faces,'tiles':tiles,'datum_tp_m':15,'overlap_with_prior_tiles_m2':consumed.intersection(mask).area,'routes':routes['routes'],'status':'Estimated connections to modeled entrance open ends, clipped to sidewalk and existing tactile footprints; not surveyed accessibility routes'}
Path(sys.argv[1] if len(sys.argv)>1 else 'assets/street/tactile-links/source/data/geometry.json').write_text(json.dumps(D,separators=(',',':'))+'\n');print(len(tiles),'tiles',len(faces),'faces',D['overlap_with_prior_tiles_m2'],'overlap')
