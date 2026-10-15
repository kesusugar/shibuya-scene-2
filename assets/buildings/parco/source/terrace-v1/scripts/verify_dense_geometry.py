"""Same dense geometry regression probe as independently accepted prototype; current candidate rerun."""
import bpy,bmesh,json,math,hashlib
from pathlib import Path
from mathutils import Vector
from collections import Counter
P=Path(__file__).resolve().parents[1];R=P/'verification';L=json.loads((P/'geometry/layout.json').read_text());asset=P/'parco_terrace_candidate.glb'
bpy.ops.wm.read_factory_settings(use_empty=True);bpy.ops.import_scene.gltf(filepath=str(asset));s=bpy.context.scene;dg=bpy.context.evaluated_depsgraph_get()
def ray(p,d,maxd=100):
 hit,loc,norm,idx,obj,matrix=s.ray_cast(dg,Vector(p),Vector(d),distance=maxd)
 return {'hit':hit,'object':obj.name if hit else None,'distance':(loc-Vector(p)).length if hit else None,'location':list(loc) if hit else None}
report={'asset_sha256':hashlib.sha256(asset.read_bytes()).hexdigest(),'sampling':{},'topology':{}}
for z in L['zones']:
 a=Vector(z['a']);b=Vector(z['b']);t=(b-a).normalized();n=Vector((-t.y,t.x));outs=[]
 for lo,hi,bot,top in z['rects']:
  for i in range(1,41):
   u=lo+(hi-lo)*i/41
   for j in range(1,21):
    h=bot+(top-bot)*j/21;xy=a+t*u-n*.5;q=ray((xy.x,xy.y,h),(n.x,n.y,0));q.update({'u':u,'z':h,'depth':q['distance']-.5 if q['hit'] else None});outs.append(q)
 report['sampling'][str(z['face'])]={'count':len(outs),'no_hits':[q for q in outs if not q['hit']],'deep_hits_over20m':[q for q in outs if q['hit'] and q['depth']>20],'near_front_under10cm':[q for q in outs if q['hit'] and -.1<q['depth']<.1],'min_depth':min(q['depth'] for q in outs if q['hit']),'max_depth':max(q['depth'] for q in outs if q['hit']),'objects':dict(Counter(q['object'] for q in outs))}
# Sample actual floors/soffits across polygons. Avoid boundaries by casting only lattice inside the 2D polygon.
def inside(p,poly):
 x,y=p;c=False
 for a,b in zip(poly,poly[1:]+poly[:1]):
  if ((a[1]>y)!=(b[1]>y)) and x<(b[0]-a[0])*(y-a[1])/(b[1]-a[1])+a[0]:c=not c
 return c
vertical=[]
for key in ['east_floor_polygon','corner_floor_polygon','north_fiveF_polygon']:
 poly=L[key];bot=30.178 if key=='north_fiveF_polygon' else 25.378
 top=34.7 if key=='east_floor_polygon' else 39.3
 for xi in range(math.floor(min(p[0] for p in poly)),math.ceil(max(p[0] for p in poly))):
  for yi in range(math.floor(min(p[1] for p in poly)),math.ceil(max(p[1] for p in poly))):
   p=(xi+.37,yi+.41)
   if not inside(p,poly) or inside(p,L['core_polygon']):continue
   down=ray((*p,bot+.1),(0,0,-1),1);up=ray((*p,top-.1),(0,0,1),1)
   vertical.append({'zone':key,'xy':p,'down':down,'up':up})
report['floor_ceiling']={'count':len(vertical),'floor_missing':[v for v in vertical if not v['down']['hit']],'ceiling_missing':[v for v in vertical if not v['up']['hit']],'floor_distance_minmax':[min(v['down']['distance'] for v in vertical if v['down']['hit']),max(v['down']['distance'] for v in vertical if v['down']['hit'])],'ceiling_distance_minmax':[min(v['up']['distance'] for v in vertical if v['up']['hit']),max(v['up']['distance'] for v in vertical if v['up']['hit'])]}
for obj in s.objects:
 if obj.type!='MESH' or not obj.name.startswith('prototype_'):continue
 bm=bmesh.new();bm.from_mesh(obj.data);bmesh.ops.remove_doubles(bm,verts=list(bm.verts),dist=1e-4);non=sum(not e.is_manifold for e in bm.edges);bad=sum(f.calc_area()<1e-10 for f in bm.faces)
 report['topology'][obj.name]={'vertices':len(bm.verts),'faces':len(bm.faces),'nonmanifold_edges':non,'boundary_edges':sum(e.is_boundary for e in bm.edges),'overconnected_edges':sum(len(e.link_faces)>2 for e in bm.edges),'zero_area_faces':bad};bm.free()
# North-end back and side closures: from within the scope towards interior, at varying heights.
termination=[]
for key in ['north_side_return','north_back_return']:
 a=Vector(L[key][0]);b=Vector(L[key][1]);t=(b-a).normalized();n=Vector((-t.y,t.x))
 for u in [.05,.25,.5,.75,.95]:
  p=a+(b-a)*u
  for h in [30.3,32.5,36.0,39.1]:
   for sign in [-1,1]:
    xy=p+n*sign*.5;q=ray((*xy,h),(-n.x*sign,-n.y*sign,0),1);termination.append({'return':key,'fraction':u,'height':h,'sign':sign,**q})
report['north_termination']={'count':len(termination),'misses':[q for q in termination if not q['hit']]}
(R/'dense-geometry-check.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps(report,indent=2))

# Explicit failure gates, distinct from informational 20 m cross-throat diagnostics.
assert sum(q['count'] for q in report['sampling'].values())==3200
assert all(not q['no_hits'] and not q['near_front_under10cm'] and q['max_depth']<25 and all(name.startswith('prototype_terrace_') for name in q['objects']) for q in report['sampling'].values())
assert report['floor_ceiling']['count']==475 and not report['floor_ceiling']['floor_missing'] and not report['floor_ceiling']['ceiling_missing']
assert report['north_termination']['count']==80 and not report['north_termination']['misses']
assert all(q['boundary_edges']==0 and q['zero_area_faces']==0 for name,q in report['topology'].items() if not name.startswith('prototype_terrace_retained'))
