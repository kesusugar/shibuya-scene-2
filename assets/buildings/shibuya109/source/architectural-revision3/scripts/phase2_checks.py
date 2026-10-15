import sys,numpy as np,json,struct
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parent));import phase2 as p
from glb_helpers import load,acc
j,b=load(p.ROOT/'inputs/prior.glb');plan=p.build();vv=[];meta=[]
for mi in range(1,17):
 if mi in [9,12]:continue
 prim=j['meshes'][mi]['primitives'][0];v=np.array(acc(j,b,prim['attributes']['POSITION']))[:,[0,2,1]];v[:,1]*=-1;ii=np.array(acc(j,b,prim['indices'])).flatten().reshape(-1,3)
 for ti,ids in enumerate(ii):
  if mi==11 and 26<=ti<=33:continue # Entrance phase removes its old dark field.
  if ti not in plan['remove'].get(mi,[]):vv.append(v[ids]);meta.append((mi,ti))
for a in plan['additions']:
 if 'existing_material' not in a:continue
 v=np.array(a['vertices'])
 for ti,ids in enumerate(a['triangles']):vv.append(v[ids]);meta.append((a['name'],ti))
vv=np.array(vv);e1=vv[:,1]-vv[:,0];e2=vv[:,2]-vv[:,0]
def hits(o,d,maxdist=1.1):
 h=np.cross(np.broadcast_to(d,e2.shape),e2);det=np.einsum('ij,ij->i',e1,h);ok=abs(det)>1e-9;f=np.zeros(len(det));f[ok]=1/det[ok];s=o-vv[:,0];u=f*np.einsum('ij,ij->i',s,h);q=np.cross(s,e1);v=f*(q@d);t=f*np.einsum('ij,ij->i',e2,q);ix=np.where(ok&(u>=-1e-7)&(v>=-1e-7)&(u+v<=1.0000001)&(t>0)&(t<maxdist))[0];return [meta[i] for i in ix]
bad=[]
for u in np.linspace(.12,10.38,20):
 for z in np.linspace(1.82,26.13,40):
  if 1.0<=u<=9.7 and 3.4<=z<=4.7:continue # Intended new sideportalheader, not residualshell.
  h=hits(p.wp(u,z,1),-p.W_N)
  if h:bad.append((u,z,h))
print('cavity_original_shell_blockers',len(bad),bad[:8])
bad=[]
for z,w,h,d in p.SLOTS:
 for r in [(p.MID-w/2,p.MID+w/2,z,z+h),(p.MID-w*.28,p.MID+w*.28,z-d,z)]:
  for u in np.linspace(r[0]+.05,r[1]-.05,20):
   for zz in np.linspace(r[2]+.05,r[3]-.05,3):
    k=min(5,max(0,int(np.searchsorted(p.U,u)-1)));o=p.cp(k,u,zz,1);dr=p.cp(k,u,zz,0)-o;hs=hits(o,dr)
    if hs:bad.append((u,zz,hs))
print('slot_original_shell_blockers',len(bad),bad[:8])

normal_report=[]
for a in plan['additions']:
 v=np.array(a['vertices']);n=np.array(a['normals']);t=np.array(a['triangles']);cr=np.cross(v[t[:,1]]-v[t[:,0]],v[t[:,2]]-v[t[:,0]]);areas=np.linalg.norm(cr,axis=1);dot=(cr*n[t].mean(axis=1)).sum(axis=1)
 normal_report.append({'mesh':a['name'],'triangles':len(t),'degenerate':int(sum(areas<1e-10)),'opposed_normals':int(sum(dot< -1e-10)),'minimum_double_area_m2':float(min(areas))})
print(json.dumps(normal_report,indent=2))
assert all(x['degenerate']==0 and x['opposed_normals']==0 for x in normal_report)

portal_bad=[]
for tangent in np.linspace(-2.62,2.62,45):
 for zz in np.linspace(1.19,4.18,30):
  o=p.PORTAL_C+tangent*p.PORTAL_R+p.PORTAL_N+np.array([0,0,zz]);hs=hits(o,-p.PORTAL_N,1.999)
  if hs:portal_bad.append((tangent,zz,hs))
print('portal_original_shell_blockers_to_back_minus1',len(portal_bad),portal_bad[:8])
assert not portal_bad
for edge in [-2.65,2.65]:
 for k in range(6):
  a=np.r_[p.A[k],0];b=np.r_[p.A[k+1],0];ta=(a-p.PORTAL_C)@p.PORTAL_R;tb=(b-p.PORTAL_C)@p.PORTAL_R
  if min(ta,tb)<=edge<=max(ta,tb):
   f=(edge-ta)/(tb-ta);point=a+f*(b-a);arc=p.U[k]+f*(p.U[k+1]-p.U[k]);print('portal_boundary',edge,'facet',k,'approx_arc',arc,'approx_xy',point[:2].tolist(),'outer_depth',(point-p.PORTAL_C)@p.PORTAL_N)
# Cross each intersected original stair-wall plane just above the actual tread.
sources=json.loads((p.ROOT/'inputs/plateau.json').read_text())['surfaces'];stair_bad=[];stair_samples=0
for si in [37,109,95]:
 xy=[]
 for v in sources[si]['ring']:
  if v[:2] not in xy:xy.append(v[:2])
 a,b=[np.r_[x,0] for x in xy];tt=p.unit(b-a);nn=np.array([tt[1],-tt[0],0.])
 for frac in np.linspace(.003,.997,80):
  pt=a+(b-a)*frac;t,f=p.STAIR_INV@(pt[:2]-p.STAIR_BI[:2])
  if not (0<t<p.STAIR_END and .005<f<.995):continue
  floor=5.90 if t>=1 else 1.38+4.52*np.ceil(t*29)/29
  for zz in np.linspace(floor+.025,7.875,7):
   o=pt+nn*.25+np.array([0,0,zz]);hs=hits(o,-nn,.50);stair_samples+=1
   if hs:stair_bad.append((si,float(t),float(f),zz,hs))
print('stair_clearance_plane_samples',stair_samples,'blockers',len(stair_bad),stair_bad[:8])
assert not stair_bad
# Compute exact nominal plan intersection footprint including .75m landing.
a95,b95=[p.STAIR_INV@(np.array(sources[95]['ring'][i][:2])-p.STAIR_BI[:2]) for i in [0,3]]
fend=a95[1]+(b95[1]-a95[1])*(p.STAIR_END-a95[0])/(b95[0]-a95[0])
print('landing_end_inner_xy',p.stairp(p.STAIR_END,0,0)[:2].tolist(),'source95_end_xy',p.stairp(p.STAIR_END,fend,0)[:2].tolist(),'fend',fend)

lower_bad=[];lower_samples=0
for lo,hi,bot,top in json.loads((p.ROOT/'inputs/lower72-fit.json').read_text())['shell_aperture_rects_uz']:
 for u in np.linspace(lo+.06,hi-.06,32):
  for zz in np.linspace(bot+.06,top-.06,12):
   hs=hits(p.wp(u,zz,1),-p.W_N,1.21);lower_samples+=1
   if hs:lower_bad.append((u,zz,hs))
print('lower72_aperture_samples',lower_samples,'opaque_original_or_panel_blockers',len(lower_bad),lower_bad[:8])
assert not lower_bad
tower_bad=[];tower_samples=0
for si in [37,109,95]:
 xy=[]
 for v in sources[si]['ring']:
  if v[:2] not in xy:xy.append(v[:2])
 a,b=[np.r_[x,0] for x in xy];tt=p.unit(b-a);nn=np.array([tt[1],-tt[0],0.])
 for frac in np.linspace(.04,.96,30):
  pt=a+(b-a)*frac
  for zz in np.linspace(7.05 if si==95 else 5.95,26.20,20):
   hs=hits(pt+nn*.08+np.array([0,0,zz]),-nn,.16);tower_samples+=1
   if hs:tower_bad.append((si,frac,zz,hs))
print('right_tower_original_frontage_samples',tower_samples,'opaque_original_blockers',len(tower_bad),tower_bad[:8])
assert not tower_bad
print('right_tower_nominal_backplane_landing_clearance_m',float((p.TOWER_BACK-p.STAIR_END)*np.linalg.norm(p.STAIR_ALONG)))
print('right_tower_louver_tip_landing_clearance_m',float((p.TOWER_BACK-p.STAIR_END)*np.linalg.norm(p.STAIR_ALONG)-.09))
mid_surviving=[]
for tri,tag in zip(vv,meta):
 owner=tag[0]
 if isinstance(owner,str):
  if not owner.startswith('phase2_retained_fragments_'):continue
  owner=int(owner.rsplit('_',1)[1])
 if owner not in range(2,8):continue
 ds=(tri-p.W_ORIGIN)@p.W_N;us=(tri-p.W_ORIGIN)@p.W_T
 if not (min(ds)>.01 and max(ds)<.30 and max(ds)-min(ds)<.02 and min(us)>-.001 and max(us)<42.306):continue
 poly=[np.array([u,z]) for u,z in zip(us,tri[:,2])]
 for axis,val,g in [(0,10.5,True),(0,42.30549706598424,False),(1,7.65,True),(1,26.25,False)]:
  if poly:poly=p.half(poly,axis,val,g)
 area=0 if len(poly)<3 else abs(sum(a[0]*b[1]-a[1]*b[0] for a,b in zip(poly,poly[1:]+poly[:1])))/2
 if area>1e-8:mid_surviving.append((tag,float(area)))
print('middle72_surviving_coarse_overlay_positive_area',len(mid_surviving),mid_surviving[:8])
assert not mid_surviving
fit=plan['report']['stair_accommodation']['fitted_cylinder_return'];chain=[np.array(fit['anchors_xyz'][0])[:2],np.array(fit['new_intermediate_B'])[:2],np.array(fit['anchors_xyz'][1])[:2],np.array(fit['anchors_xyz'][2])[:2]]
def pdist(pt,a,b):
 t=max(0.,min(1.,float(np.dot(pt-a,b-a)/np.dot(b-a,b-a))));return float(np.linalg.norm(pt-(a+t*(b-a))))
def orient(a,b,c):return (b[0]-a[0])*(c[1]-a[1])-(b[1]-a[1])*(c[0]-a[0])
def sdist(a,b,c,d):
 if orient(a,b,c)*orient(a,b,d)<0 and orient(c,d,a)*orient(c,d,b)<0:return 0.
 return min(pdist(a,c,d),pdist(b,c,d),pdist(c,a,b),pdist(d,a,b))
rail_a=p.STAIR_BI[:2];rail_b=p.STAIR_TI[:2];deck_end=p.stairp(p.STAIR_END,0,0)[:2]
rail_distance=min(sdist(a,b,rail_a,rail_b) for a,b in zip(chain,chain[1:]));deck_distance=min(sdist(a,b,rail_b,deck_end) for a,b in zip(chain,chain[1:]))
print('fitted_return_min_inner_rail_center_plan_distance_m',rail_distance,'minus_rail_radius035',rail_distance-.035)
print('fitted_return_min_open_landing_inner_edge_plan_distance_m',deck_distance)
assert rail_distance>.035 and deck_distance>0
print('left_route_limit','No complete annular deck route is modeled or certified; these checks establish no intersection with existing inner rail or landing edge only.')
