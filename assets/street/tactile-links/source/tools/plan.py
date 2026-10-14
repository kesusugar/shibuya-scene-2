import json,math,heapq,pathlib,sys,numpy as np
from shapely.geometry import Polygon,Point,LineString
from shapely.ops import unary_union
from shapely import contains_xy
R=pathlib.Path.cwd();G=json.load(open(R/'assets/ground/core/source/data/ground_input.json'));S=json.load(open(R/'assets/street/core/source/data/street_input.json'));T=json.load(open(R/'assets/street/tactile/source/data/stats.json'))
T['tiles']+=json.load(open(R/'assets/street/tactile-extra/source/data/stats.json'))['tiles']
walk=unary_union([Polygon([p[:2] for p in f['ring']]).buffer(0) for f in G['surfaces'] if f['class'] in ['sidewalk','island']]);blocked=[]
for f in S['features']:
 if f['kind']=='entrance':blocked.append(Polygon(f['ring']).buffer(.10))
 if f['kind']=='tree':blocked.append(Point(*f['point']).buffer(.85))
layout=json.load(open(R/'assets/street/core/source/data/street_layout.json'))
for run in layout['rail_runs']:blocked.append(LineString(run).buffer(.20))
for o in layout['items']:
 if 'xy' in o:blocked.append(Point(*o['xy']).buffer(.4))
for f in json.load(open(R/'assets/street/plaza-facilities/source/data/layout.json'))['items']:blocked.append(Polygon(f['ring']).buffer(.25))
K=json.load(open(R/'assets/buildings/plaza-kiosk/source/data/plateau.json'));blocked.append(unary_union([Polygon([p[:2] for p in s['ring']]).buffer(0) for s in K['surfaces'] if s['kind']=='RoofSurface']).buffer(.2))
walk=walk.difference(unary_union(blocked)).buffer(-.22)
step=.3;x0=-55;y0=-75;xs=np.arange(x0,55,step);ys=np.arange(y0,36,step);xx,yy=np.meshgrid(xs,ys);valid=contains_xy(walk,xx,yy);ny,nx=valid.shape
sources={}
for tile in T['tiles']:
 if tile['kind']!='guide':continue
 x,y=tile['centre_xy'];i=round((x-x0)/step);j=round((y-y0)/step)
 if 0<=i<nx and 0<=j<ny and valid[j,i]:sources[(i,j)]=tile
queue=[];distance={};previous={};origin={}
for key,tile in sources.items():distance[key]=0;origin[key]=tile;heapq.heappush(queue,(0,key))
while queue:
 cost,node=heapq.heappop(queue)
 if cost!=distance[node]:continue
 i,j=node
 for di,dj in [(1,0),(-1,0),(0,1),(0,-1)]:
  ni,nj=i+di,j+dj;other=(ni,nj)
  if not(0<=ni<nx and 0<=nj<ny and valid[nj,ni]):continue
  nc=cost+step
  if nc<distance.get(other,1e9):distance[other]=nc;previous[other]=node;origin[other]=origin[node];heapq.heappush(queue,(nc,other))
routes=[];centre=np.array([6.5,-2])
for f in S['features']:
 if f['kind']!='entrance':continue
 ring=np.array(f['ring']);edges=np.roll(ring,-1,axis=0)-ring;u=edges[np.argmax(np.linalg.norm(edges,axis=1))];u=u/np.linalg.norm(u);v=np.array([-u[1],u[0]]);lu=ring@u;lv=ring@v;c=u*(lu.max()+lu.min())/2+v*(lv.max()+lv.min())/2;length=lu.max()-lu.min()
 if np.linalg.norm(c+u*length/2-centre)<np.linalg.norm(c-u*length/2-centre):u=-u
 goal=c-u*(length/2+.65);candidates=[(math.hypot(xs[i]-goal[0],ys[j]-goal[1]),(i,j)) for i,j in distance if math.hypot(xs[i]-goal[0],ys[j]-goal[1])<=1.2]
 if not candidates:routes.append({'id':f['id'],'status':'unreachable without road or obstacle placement','goal':goal.tolist()});continue
 _,node=min(candidates);end=node;path=[node]
 while node in previous:node=previous[node];path.append(node)
 path.reverse();pts=[[round(float(xs[i]),4),round(float(ys[j]),4)] for i,j in path];pts[0]=origin[end]['centre_xy'];compressed=[pts[0]];k=0
 while k<len(pts)-1:
  furthest=next((j for j in range(len(pts)-1,k,-1) if walk.covers(LineString([pts[k],pts[j]]))),k+1);compressed.append(pts[furthest]);k=furthest
 pts=compressed;routes.append({'id':f['id'],'goal':goal.tolist(),'endpoint_distance_m':math.dist(pts[-1],goal),'length_m':distance[end],'source_tile':origin[end],'points':pts,'status':'estimated connection to modeled open end; not surveyed route'})
out=pathlib.Path(sys.argv[1] if len(sys.argv)>1 else 'assets/street/tactile-links/source/data/routes.json');out.write_text(json.dumps({'routes':routes,'grid_m':step,'clearance_m':.22,'position_basis':'Existing modeled opening orientation and sidewalk-only shortest grid route; not a verified 2025 guidance layout'},indent=1)+'\n');print([(r['id'],r.get('length_m'),len(r.get('points',[])),r['status']) for r in routes])
