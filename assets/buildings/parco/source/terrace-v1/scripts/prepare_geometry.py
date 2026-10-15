"""Bounded clipping of ONLY authorized terrace-wall coverage; immutable input GLB bytes."""
from pathlib import Path
import json,numpy as np,hashlib
from glb_io import *
ROOT=Path(__file__).resolve().parents[1];BASE=ROOT/'inputs';OUT=ROOT/'geometry';OUT.mkdir(exist_ok=True)
source=BASE/'roof22-corrected-base.glb';d,b=read(source);assert hashlib.sha256(source.read_bytes()).hexdigest()=='7dbb2e71338da1d3a5a6db6ec52ec38235f07ba5adbbd7b0585f6bcb15d372cd'
reg=json.loads((ROOT/'registration/transform.json').read_text());assert reg['gate'].startswith('PASS')
s=reg['scale_m_per_pixel'];R=np.array(reg['rotation_row_matrix']);t=np.array(reg['translation_world_xy_m'])
def m(p):return (s*np.array([p[0],-p[1]])@R+t).tolist()
floor=25.378;f5=floor+4.8;f6=floor+9.6
sourcefaces=json.loads((BASE/'source-plateau.json').read_text())['surfaces'];pr=d['meshes'][1]['primitives'][0];verts=world(acc(d,b,pr['attributes']['POSITION']));ids=acc(d,b,pr['indices']).reshape(-1,3)
# Controls use the actual source outline, not a map-warped replacement.
zones=[{'face':171,'a':[-110.668,276.864],'b':[-119.881,294.839],'rects':[[0,20.200000,25.3779,34.7]]},
 {'face':108,'a':[-118.839,295.526],'b':[-125.516,307.472],'rects':[[0,13.685418,26.2,39.3]]},
 {'face':152,'a':[-125.516,307.472],'b':[-144.222,306.519],'rects':[[0,11.0,26.2,39.3],[11.,18.730264,f5,39.3]]}]
# Boundary extends tiny numeric tolerance only to the endpoint, never into adjacent faces.
for z in zones:
 z['length']=float(np.linalg.norm(np.array(z['b'])-z['a']));z['rects'][-1][1]=z['length']+.0001
# Polygon clipping retains interpolated XYZ on the source triangles.
def split(poly,fn):
 ip=[];op=[]
 for a,bb in zip(poly,poly[1:]+poly[:1]):
  da,db=fn(a),fn(bb);ain=da>=-1e-9;bin=db>=-1e-9
  (ip if ain else op).append(a)
  if ain!=bin:
   p=a+(bb-a)*da/(da-db);ip.append(p);op.append(p)
 return ip,op
def area(poly):
 if len(poly)<3:return 0.
 return float(sum(np.linalg.norm(np.cross(poly[i]-poly[0],poly[i+1]-poly[0]))*.5 for i in range(1,len(poly)-1)))
def subtract(poly,z,rect):
 a=np.array(z['a']);tt=(np.array(z['b'])-a)/z['length'];lo,hi,zlo,zhi=rect
 fn=[lambda p:(p[:2]-a)@tt-lo,lambda p:hi-(p[:2]-a)@tt,lambda p:p[2]-zlo,lambda p:zhi-p[2]]
 out=[];remain=poly
 for f in fn:
  if len(remain)<3:break
  remain,outer=split(remain,f)
  if area(outer)>1e-8:out.append(outer)
 return out,area(remain)
# Audited original source triangulation indices. Lower108/152 plinth additions are excluded.
targets={171:[195,451],108:[52,273],152:[128,367,368,369,370,371,372,373]}
retained=[];audit=[]
for z in zones:
 for ti in targets[z['face']]:
  q=[p.astype(float).copy() for p in verts[ids[ti]]];parts=[q];removed=0.
  for rect in z['rects']:
   new=[]
   for p in parts:
    rr,ar=subtract(p,z,rect);new+=rr;removed+=ar
   parts=new
  if removed<1e-7:continue
  orig=area(q);remain=sum(area(p) for p in parts);assert abs(orig-remain-removed)<1e-5
  for p in parts:retained.append({'source_face':z['face'],'source_triangle':ti,'vertices':[v.tolist() for v in p]})
  audit.append({'face':z['face'],'triangle':ti,'original_area_m2':orig,'removed_area_m2':removed,'retained_area_m2':remain,'original_indices':ids[ti].tolist()})
  ids[ti]=ids[ti][0]
# Remove the earlier shallow band pieces only; keep all upper cladding panels/reveal backings bit-identical.
components=json.loads((BASE/'shallow-component-stats.json').read_text())['components'];old_removed={}
for mi,material in [(8,'cladding'),(9,'joint'),(10,'glass'),(11,'rail_glass')]:
 c=[v for v in components if v['material']==material];ix=acc(d,b,d['meshes'][mi]['primitives'][0]['indices']).reshape(-1,3);assert len(ix)==12*len(c)
 deleted=[]
 for ci,v in enumerate(c):
  if v['kind'] not in ['pale_cladding_panel','reveal_backing']:
   ix[ci*12:(ci+1)*12]=ix[ci*12,0];deleted.append(v['kind'])
 old_removed[d['meshes'][mi]['name']]={'removed_prisms':len(deleted),'kept_prisms':len(c)-len(deleted),'removed_kinds':sorted(set(deleted))}
# Explicit root approval: obsolete genericspandrel ribbons only inside SAME opening boxes.
sp=d['meshes'][7]['primitives'][0];sv=world(acc(d,b,sp['attributes']['POSITION']));si=acc(d,b,sp['indices']).reshape(-1,3)
sp_retained=[];sp_audit=[]
for ti,ix in enumerate(si.copy()):
 q=[p.astype(float).copy() for p in sv[ix]];parts=[q];removed=0.;owners=[]
 for z in zones:
  aa=np.array(z['a']);tt=(np.array(z['b'])-aa)/z['length'];nn=np.array([tt[1],-tt[0]])
  dd=(np.array(q)[:,:2]-aa)@nn
  # Prove old facadeplane ownership; no otherface/officegrid selection.
  if max(abs(dd))>.20 or np.ptp(dd)>.06:continue
  for rect in z['rects']:
   new=[]
   for pp in parts:
    rr,ar=subtract(pp,z,rect);new+=rr;removed+=ar
    if ar>1e-8:owners.append(z['face'])
   parts=new
 if removed<1e-8:continue
 orig=area(q);remain=sum(area(pp) for pp in parts);assert abs(orig-remain-removed)<1e-6
 for pp in parts:sp_retained.append({'source_face':owners[0],'source_triangle':ti,'vertices':[v.tolist() for v in pp]})
 sp_audit.append({'mesh':7,'primitive':0,'triangle':ti,'face_ownership':sorted(set(owners)),'original_indices':ix.tolist(),'new_indices':[int(ix[0])]*3,'original_area_m2':orig,'removed_area_m2':removed,'retained_area_m2':remain})
 si[ti]=ix[0]
(OUT/'retained-spandrel-fragments.json').write_text(json.dumps(sp_retained,indent=2)+'\n')
(OUT/'spandrel-cut-audit.json').write_text(json.dumps({'scope':'Root authorized only obsolete generic spandrel ribbon portions inside the same terrace opening boxes. All outside-band segments are retained geometrically.','triangles':sp_audit},indent=2)+'\n')
write(OUT/'authorized-shell-cut.glb',d,b)
(OUT/'retained-wall-fragments.json').write_text(json.dumps(retained,indent=2)+'\n')
(OUT/'cut-audit.json').write_text(json.dumps({'source_sha256':hashlib.sha256(source.read_bytes()).hexdigest(),'triangles':audit,'shallow_band_replacement':old_removed,'all_original_position_normal_material_attributes':'unaltered bytes','all_unchanged_indices':'unaltered bytes','roof_source84_source141_footprint179':'unaltered bytes','no_hidden_backwall':'authorized shell indices degenerated, retained outside-band fragments rebuilt explicitly'},indent=2)+'\n')
# Plan-derived geometry bounded by the original wall scope.
a171=zones[0]['a'];b171=zones[0]['b'];a108=zones[1]['a'];ne=zones[1]['b'];nw=zones[2]['b']
layout={'candidate_only':True,'units':'m, x east/y north/z=TP-15','registration_file':'../registration/transform.json','levels':{'oneF_inferred_z':floor-15.1,'oneF_inferred_TP':floor-15.1+15,'oneF_TP_uncertainty_m':[-.5,.5],'fourF_z':floor,'fiveF_z':f5,'sixF_z':f6,'sevenF_z':f6+4.8,'east_soffit_z':34.7,'corner_north_soffit_z':39.3,'floor_thickness_m':.35},'datum_basis':'4F floor25.378 inferred from source3/source171 slab boundary; 1F=4F-15.1. This is NOT ground_tp23.4 and NOT TP survey proof. Modelcoarse26.2 retained as parapet/top boundary0.822m above4F.','zones':zones,
'east_floor_polygon':[a171,b171,m((1448,580)),m((1178,580)),m((1178,677)),m((1407,677)),m((1372,960))],
'corner_floor_polygon':[b171,a108,ne,nw,m((1114,395)),m((1178,580)),m((1448,580))],
'core_polygon':[m(p) for p in [(1178,395),(1340,395),(1340,376),(1448,376),(1448,580),(1178,580)]],
'shopfront_polyline':[m(p) for p in [(1372,960),(1407,677),(1178,677),(1178,580)]],
'north_fiveF_polygon':[nw,(np.array(ne)+(np.array(nw)-ne)*11/zones[2]['length']).tolist(),m((1308,395)),m((1114,395))],
'north_side_return':[nw,m((1114,395))],'north_back_return':[m((1114,395)),m((1178,395))],
'core_west_fiveF_walkway':[m(p) for p in [(1114,395),(1178,395),(1178,625),(1114,625)]],
'core_south_stair':{'start':m((1362,603)),'end':m((1178,603)),'width':2.5,'rise':4.8,'steps':30},
'east_plaza_stair':{'start':m((1449,945)),'end':m((1449,705)),'width':2.55,'rise':4.8,'steps':30,'direction':'stairs arrive4F from3F; plan map footprint and4.8m rise; tread scheme inferred'},
'notes':['Structural support positions/soffit thickness/step count are bounded inference.','The north route changes level:4F atcorner,5F western~7.7m, retaining shell below5F there.','No full core removal and no uniform8m inset.','Source84/141 true1.82m notch is untouched.','4F interior back wall has map-derived stepped/angled line.','The exact2Fsection cut is unknown;8–9m section-direction depth is only a check.']}
(OUT/'layout.json').write_text(json.dumps(layout,indent=2)+'\n');print('PREPARED',len(audit),'clipped source triangles; no original files written')
