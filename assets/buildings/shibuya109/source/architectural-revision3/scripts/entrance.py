"""Evidence-led entrance ensemble. Blender coordinates, metres, T.P.15 datum.
Returns original-index removal masks and batched added geometry; never edits inputs.
"""
import math,json,random
from pathlib import Path
from mathutils import Vector
ROOT=Path(__file__).resolve().parents[1]
C=Vector((-129.0380165156,6.9354800658,0));N=Vector((.998716,-.050703,0)).normalized();R=Vector((.050703,.998716,0)).normalized()
def P(o,r,z):return C+o*N+r*R+Vector((0,0,z))
def mat(name,rgb,metal=0,rough=.5,emission=None):
 d={'name':name,'pbrMetallicRoughness':{'baseColorFactor':[*rgb,1],'metallicFactor':metal,'roughnessFactor':rough}}
 if emission:d['emissiveFactor']=emission
 return d
class Mesh:
 def __init__(self,name,material):self.name=name;self.material=material;self.vertices=[];self.normals=[];self.triangles=[];self.colors=[]
 def tri(self,pts,color=(1,1,1,1),normals=None):
  pts=[Vector(p) for p in pts];nn=(pts[1]-pts[0]).cross(pts[2]-pts[0]);
  if nn.length<1e-10:return
  nn.normalize();k=len(self.vertices);self.vertices.extend([list(p) for p in pts]);self.normals.extend([list(n) for n in normals] if normals else [list(nn)]*3);self.triangles.append([k,k+1,k+2]);self.colors.extend([list(color)]*3)
 def quad(self,a,b,c,d,color=(1,1,1,1)):self.tri([a,b,c],color);self.tri([a,c,d],color)
 def sheet(self,a,b,c,d,thickness=.018):
  ps=[Vector(p) for p in [a,b,c,d]];off=(ps[1]-ps[0]).cross(ps[2]-ps[0]).normalized()*(thickness/2)
  self.quad(*[p+off for p in ps]);self.quad(*[p-off for p in reversed(ps)])
  for a,b in zip(ps,ps[1:]+ps[:1]):self.quad(a-off,b-off,b+off,a+off)
 def box(self,o0,o1,r0,r1,z0,z1,color=(1,1,1,1)):
  v=[P(o,r,z) for z in [z0,z1] for r in [r0,r1] for o in [o0,o1]]
  for ids in [(0,2,3,1),(4,5,7,6),(0,1,5,4),(2,6,7,3),(0,4,6,2),(1,3,7,5)]:self.quad(*[v[i] for i in ids],color)
 def tube(self,a,b,r,segments=8,r2=None,color=(1,1,1,1)):
  a,b=Vector(a),Vector(b);axis=(b-a).normalized();u=axis.cross(Vector((0,0,1)))
  if u.length<.01:u=axis.cross(Vector((1,0,0)))
  u.normalize();v=axis.cross(u);r2=r if r2 is None else r2
  for i in range(segments):
   d=u*math.cos(i*math.tau/segments)+v*math.sin(i*math.tau/segments);e=u*math.cos((i+1)*math.tau/segments)+v*math.sin((i+1)*math.tau/segments)
   aa,ab,ba,bb=a+d*r,a+e*r,b+d*r2,b+e*r2
   self.tri([aa,ab,bb],color,[d,e,e]);self.tri([aa,bb,ba],color,[d,e,d]);self.tri([a,ab,aa],color);self.tri([b,ba,bb],color)
 def data(self):return {k:getattr(self,k) for k in ['name','material','vertices','normals','triangles','colors']}
def build():
 gold=Mesh('entrance_gold_open_frame',mat('entrance_anodized_gold',(.57,.35,.105),.75,.31))
 spine=Mesh('entrance_stowed_gray_awning_spine',mat('entrance_gray_spine',(.14,.16,.17),.6,.4))
 silver=Mesh('entrance_stair_rails_nosings',mat('entrance_brushed_silver',(.55,.58,.60),.82,.28))
 portal=Mesh('entrance_polygonal_gradient_portal',mat('entrance_original_gradient', (1,1,1),.08,.43))
 dark=Mesh('entrance_shallow_passage_fixture_housings',mat('entrance_recess_charcoal',(.026,.032,.032),.08,.7))
 white=Mesh('entrance_canonical_white_logo_and_lamps',mat('entrance_white_identity',(.9,.92,.9),.12,.38,[.14,.14,.13]))
 jamb=Mesh('entrance_neutral_jamb_soffit',mat('entrance_jamb_metal',(.36,.35,.31),.55,.47))
 stairglass=Mesh('entrance_stair_frosted_side_panels',mat('entrance_frosted_side_glass',(.32,.46,.43),.18,.31))
 stair=Mesh('entrance_gold_mosaic_stair',mat('entrance_original_mosaic_colors',(1,1,1),.4,.42))
 # Four round posts and flared feet. Feet are provisional planar slope only.
 ground=json.loads((ROOT/'inputs/ground-contact.json').read_text())['points'];gtris=json.loads((ROOT/'inputs/render-ground-context.json').read_text())['triangles']
 def ground_z(x,y,fallback):
  heights=[]
  for a,b,c in gtris:
   den=(b[1]-c[1])*(a[0]-c[0])+(c[0]-b[0])*(a[1]-c[1])
   if abs(den)<1e-9:continue
   u=((b[1]-c[1])*(x-c[0])+(c[0]-b[0])*(y-c[1]))/den;v=((c[1]-a[1])*(x-c[0])+(a[0]-c[0])*(y-c[1]))/den
   if min(u,v,1-u-v)>=-1e-7:heights.append(u*a[2]+v*b[2]+(1-u-v)*c[2])
  return max(heights) if heights else fallback
 foot=[]
 for o in [0,8.52]:
  for r in [-3.2759,3.2759]:
   key=('front' if o else 'rear')+('_left' if r<0 else '_right');z=ground[key]['z'];foot.append({'local_out_right':[o,r],'world_xyz':list(P(o,r,z)),'source_sample':key,'status':'Existing model ground_fill_extension contact, not surveyed grade'})
   gold.tube(P(o,r,z+.11),P(o,r,8.02 if o else 7.70),.145,16)
   start=len(gold.vertices);gold.tube(P(o,r,z),P(o,r,z+.16),.235,16,.16)
   for k in range(start,len(gold.vertices)):
    v=gold.vertices[k]
    if abs(v[2]-z)<1e-5:v[2]=ground_z(v[0],v[1],z)
   for k in range(start,len(gold.vertices),3):
    v=[Vector(p) for p in gold.vertices[k:k+3]];nn=(v[1]-v[0]).cross(v[2]-v[0]).normalized();gold.normals[k:k+3]=[list(nn)]*3
   for zz in [6.08,6.20,7.30,7.40]:gold.tube(P(o,r,zz),P(o,r,zz+.045),.19,16)
 # Open square-pyramid space frame: six transverse by eight longitudinal bays.
 # Visible reference supplies topology; hidden repeat count remains an estimate.
 ny,nx=6,8;w=6.5518;length=8.52;low=6.10;high=7.35
 for z in [low,high]:
  for r in [-w/2,w/2]:gold.tube(P(0,r,z),P(length,r,z),.055,10)
  for o in [0,length]:gold.tube(P(o,-w/2,z),P(o,w/2,z),.055,10)
 # Lower orthogonal grid, upper offset grid, tetrahedral diagonals, no filled roof.
 for ix in range(nx+1):
  o=length*ix/nx;gold.tube(P(o,-w/2,low),P(o,w/2,low),.024)
 for iy in range(ny+1):
  r=-w/2+w*iy/ny;gold.tube(P(0,r,low),P(length,r,low),.024)
 for ix in range(nx):
  o=length*(ix+.5)/nx
  gold.tube(P(o,-w/2,high),P(o,w/2,high),.025)
 for iy in range(ny):
  r=-w/2+w*(iy+.5)/ny;gold.tube(P(0,r,high),P(length,r,high),.025)
 for ix in range(nx):
  for iy in range(ny):
   apex=P(length*(ix+.5)/nx,-w/2+w*(iy+.5)/ny,high)
   for dx,dy in [(0,0),(0,1),(1,0),(1,1)]:gold.tube(P(length*(ix+dx)/nx,-w/2+w*(iy+dy)/ny,low),apex,.023)
 # Stowed gray center spine, faceted folding cover not opaque overall canopy.
 spine.box(.12,8.38,-.23,.23,5.94,6.25)
 for side in [-1,1]:
  # Two folded strips form narrow V along central carrier.
  a,b,c=[side*x for x in [.23,.47,.64]]
  spine.sheet(P(.16,a,6.17),P(8.34,a,6.17),P(8.34,b,5.80),P(.16,b,5.80))
  spine.sheet(P(.16,b,5.80),P(8.34,b,5.80),P(8.34,c,6.21),P(.16,c,6.21))
 # Reference-visible repeated downlights and selected floodlights, no real-time lights.
 for o in [.65,1.95,3.25,4.55,5.85,7.15]:white.tube(P(o,0,5.91),P(o,0,5.945),.065,12)
 for o in [1.10,3.24,5.36,7.48]:
  for r in [-2.1,2.1]:
   dark.box(o-.14,o+.14,r-.2,r+.2,5.96,6.14);white.box(o-.10,o+.10,r-.15,r+.15,5.95,5.965)
 for r in [-2.185,2.185]:
  for i in range(17):
   o=.25+i*.50;white.tube(P(o,r,6.035),P(o,r,6.095),.028,6)
 # Polygonal entry portal, front face mild facets with smooth original vertex gradient.
 # Width6.2, lintel1.7m, clear portal2.55–2.85m across provisional grade.
 def front(r):return .76-.045*abs(r)
 def col(r):
  t=(r+3.1)/6.2;a,b,c=(.95,.23,.28),(.66,.045,.30),(.11,.012,.32)
  p,q,f=(a,b,t/.5) if t<.5 else(b,c,(t-.5)/.5)
  return tuple(p[k]*(1-f)+q[k]*f for k in range(3))+(1,)
 def gradient_quad(ps):
  base=len(portal.vertices);portal.quad(*[P(*p) for p in ps]);
  # set colors by vertex local transverse coordinate, not imported photo pixels
  for i in range(base,len(portal.vertices)):
   r=(Vector(portal.vertices[i])-C).dot(R);portal.colors[i]=list(col(r))
 cuts=[-3.1,-2.1,-1.05,0,1.05,2.1,3.1]
 for a,b in zip(cuts,cuts[1:]):
  gradient_quad([(front(a),a,4.2),(front(b),b,4.2),(front(b),b,5.9),(front(a),a,5.9)])
  jamb.quad(P(-1.0,a,4.2),P(-1.0,b,4.2),P(front(b),b,4.2),P(front(a),a,4.2))
  portal.quad(P(front(a),a,5.9),P(front(b),b,5.9),P(.05,b,5.9),P(.05,a,5.9),col((a+b)/2))
 for r in [-3.1,3.1]:
  edge=[P(.05,r,4.2),P(front(r),r,4.2),P(front(r),r,5.9),P(.05,r,5.9)]
  portal.quad(*(list(reversed(edge)) if r>0 else edge),color=col(r))
 portal.quad(P(.05,3.1,4.2),P(.05,-3.1,4.2),P(.05,-3.1,5.9),P(.05,3.1,5.9),col(0))
 for a,b in [(-3.1,-2.65),(2.65,3.1)]:
  gradient_quad([(front(a),a,1.52-a*.30/6.5518),(front(b),b,1.52-b*.30/6.5518),(front(b),b,4.2),(front(a),a,4.2)])
  jamb.box(.10,front((a+b)/2),a,b,1.52,4.20)
 # Shallow doorway, dark backing behind bounded source aperture; deliberately no invented interior.
 dark.quad(P(-1.0,-2.65,1.64),P(-1.0,2.65,1.40),P(-1.0,2.65,4.2),P(-1.0,-2.65,4.2))
 for r in [-2.65,2.65]:
  q=[P(-1.0,r,1.52-r*.30/6.5518),P(front(r),r,1.52-r*.30/6.5518),P(front(r),r,4.2),P(-1.0,r,4.2)]
  jamb.quad(*(list(reversed(q)) if r<0 else q))
 jamb.quad(P(-1.0,-2.65,1.64),P(front(-2.65),-2.65,1.64),P(front(2.65),2.65,1.40),P(-1.0,2.65,1.40))
 # Transform exact accepted canonical authored vertices, not a font or newly drawn logo.
 local=json.loads((ROOT/'inputs/logo-record.json').read_text())['local_vertices'];scale=.425
 for key in ['logo_gradient_face','logo_metal_return','logo_shibuya_letters']:
  vv=local[key]
  for i in range(0,len(vv),3):
   pts=[P(.795+v[2]*scale,(v[0]-.575)*scale,5.25+v[1]*scale) for v in vv[i:i+3]]
   # canonical authoring plane X/Y maps to R/Z, its +Z to N; proper-handed rotation
   lv=[Vector(v) for v in vv[i:i+3]];ln=(lv[1]-lv[0]).cross(lv[2]-lv[0]).normalized();wnormal=R*ln.x+Vector((0,0,ln.y))+N*ln.z
   white.tri(pts,normals=[wnormal]*3)
 # Supported Dogenzaka side portal identity, on its own silver header; no tenant text.
 wa=Vector((-132.146,-.776,0));wt=Vector((-.945716344,-.324993227,0));wn=Vector((.324993227,-.945716344,0));uc=5.35
 def sidep(u,z,d):return wa+wt*u+wn*d+Vector((0,0,z))
 for i in range(6):
  right0=-1.05+i*2.10/6;right1=-1.05+(i+1)*2.10/6
  start=len(portal.vertices);portal.quad(sidep(uc-right0,3.50,.275),sidep(uc-right1,3.50,.275),sidep(uc-right1,4.60,.275),sidep(uc-right0,4.60,.275))
  for k in range(start,len(portal.vertices)):
   right=-(Vector(portal.vertices[k])-wa).dot(wt)+uc;portal.colors[k]=list(col(right*3.1/1.05))
 for key in ['logo_gradient_face','logo_metal_return','logo_shibuya_letters']:
  vv=local[key]
  for i in range(0,len(vv),3):
   lv=[Vector(v) for v in vv[i:i+3]];ln=(lv[1]-lv[0]).cross(lv[2]-lv[0]).normalized();sn=-wt*ln.x+Vector((0,0,ln.y))+wn*ln.z
   white.tri([sidep(uc-(v[0]-.575)*.27,4.182+v[1]*.27,.305+v[2]*.27) for v in vv[i:i+3]],normals=[sn]*3)
 # Gold mosaic stair, plan registered diagonal flight. Count/elevation are inferred.
 reg=json.loads((ROOT/'inputs/registration-proposal.json').read_text())['landmarks']
 def xy(name):return Vector((*reg[name]['proposed_blender_xy'],0))
 bi,bo,ti,to=[xy(k) for k in ['stair_bottom_inner','stair_bottom_outer','stair_top_inner','stair_top_outer']]
 along=ti-bi;across=bo-bi;steps=29;z0=1.38;z1=5.90
 rng=random.Random(109)
 for i in range(steps):
  a=i/steps;b=(i+1)/steps;z=z0+(z1-z0)*b;zp=z0+(z1-z0)*a
  for j in range(10):
   f=j/10;g=(j+1)/10
   p=bi+along*a+across*f;q=bi+along*a+across*g;s=bi+along*b+across*g;t=bi+along*b+across*f
   tone=rng.uniform(.68,1.12);color=(.56*tone,.38*tone,.10*tone,1)
   stair.quad(p+Vector((0,0,z)),q+Vector((0,0,z)),s+Vector((0,0,z)),t+Vector((0,0,z)),color)
   stair.quad(p+Vector((0,0,zp)),q+Vector((0,0,zp)),q+Vector((0,0,z)),p+Vector((0,0,z)),color)
  silver.tube(bi+along*a+Vector((0,0,z+.007)),bo+along*a+Vector((0,0,z+.007)),.019,6)
 # Closed supporting wedge sides; no guessed interior stairwell.
 for p,q in [(bi,ti),(bo,to)]:
  for i in range(steps):
   e0=p+along*(i/steps);e1=p+along*((i+1)/steps);zz=z0+(z1-z0)*(i+1)/steps
   side=[e0+Vector((0,0,z0)),e1+Vector((0,0,z0)),e1+Vector((0,0,zz)),e0+Vector((0,0,zz))]
   stair.quad(*(list(reversed(side)) if p==bi else side),color=((.34,.36,.35,1) if p==bo else (.37,.27,.10,1)))
 stair.quad(ti+Vector((0,0,z1)),to+Vector((0,0,z1)),to+Vector((0,0,z0)),ti+Vector((0,0,z0)),(.37,.27,.10,1))
 stair.quad(bi+Vector((0,0,z0)),ti+Vector((0,0,z0)),to+Vector((0,0,z0)),bo+Vector((0,0,z0)),(.37,.27,.10,1))
 for f in [0,.5,1]:
  p,q=bi+across*f,ti+across*f
  silver.tube(p+Vector((0,0,z0+1.0)),q+Vector((0,0,z1+1.0)),.035,10)
  silver.tube(p+Vector((0,0,z0+.45)),q+Vector((0,0,z1+.45)),.018,8)
  for i in sorted(set(list(range(0,steps+1,5))+[steps])):
   t=i/steps;v=p+along*t;z=z0+(z1-z0)*t
   silver.tube(v+Vector((0,0,z)),v+Vector((0,0,z+1.0)),.026,8)
 # The official close view shows a frosted outer balustrade above a metal side plinth.
 for i in range(8):
  a=(i+.04)/8;b=(i+.96)/8;pa=bo+along*a;pb=bo+along*b;za=z0+(z1-z0)*a;zb=z0+(z1-z0)*b
  stairglass.quad(pa+Vector((0,0,za+.36)),pb+Vector((0,0,zb+.36)),pb+Vector((0,0,zb+.93)),pa+Vector((0,0,za+.93)))
  # Reverse face gives the thin panel a two-sided physical surface, separated2cm.
  off=across.normalized()*.018
  stairglass.quad(pa+off+Vector((0,0,za+.93)),pb+off+Vector((0,0,zb+.93)),pb+off+Vector((0,0,zb+.36)),pa+off+Vector((0,0,za+.36)))
  edge=[pa+Vector((0,0,za+.36)),pb+Vector((0,0,zb+.36)),pb+Vector((0,0,zb+.93)),pa+Vector((0,0,za+.93))]
  for a,b in zip(edge,edge[1:]+edge[:1]):stairglass.quad(a,b,b+off,a+off)
 # Minimum exterior top landing. Route continues around the cylinder; no terminal door.
 ext=along.normalized()*.75;li,lo=ti+ext,to+ext
 landing=[ti,to,lo,li]
 jamb.quad(*[v+Vector((0,0,z1)) for v in landing])
 jamb.quad(*[v+Vector((0,0,z1-.12)) for v in reversed(landing)])
 for a,b in zip(landing,landing[1:]+landing[:1]):jamb.quad(a+Vector((0,0,z1-.12)),b+Vector((0,0,z1-.12)),b+Vector((0,0,z1)),a+Vector((0,0,z1)))
 # Continue only outer landing rail; the cylinderward side remains open for the documented turn.
 silver.tube(to+Vector((0,0,z1+1)),lo+Vector((0,0,z1+1)),.035,10)
 silver.tube(lo+Vector((0,0,z1)),lo+Vector((0,0,z1+1)),.026,8)
 report={'posts':foot,'canopy':{'bays_transverse':ny,'bays_longitudinal':nx,'plan_m':[w,length],'chord_z_m':[low,high],'main_post_diameter_m':.29,'tube_diameter_m':.046,'hidden_node_count':'regularized estimate from clear2025 photos; not measured'},'portal':{'width_m':6.2,'lintel_z_m':[4.2,5.9],'lower_logo_scale_from_authored_outline':scale,'lower_logo_width_m':4.15*scale,'combined_logo_height_m':2.99*scale},'stairs':{'landing_extension_m':.75,'landing_end_xy':[list(li[:2]),list(lo[:2])],'risers':steps,'bottom_z':z0,'top_z':z1,'top_height':'photo-fitted near portal lintel5.9±0.5m;29risers approximate; not surveyed','run_m':along.length,'width_m':across.length},'removed':{'12':'all116 coarse canopy triangles','20':'all8 plain panel triangles','11':'original26–33 entrance shadow only'},'ground':'Four post centers and flared-foot base rings fitted to unchanged ground_fill_extension triangles. Exact model-ground contact is documented, not surveyed elevation or full-scene validation. Core fallback0.14 rejected; no roads edited. Stair outerbase not covered by extension, retains inferred1.38m.'}
 return {'remove':{12:list(range(116)),20:list(range(8)),11:list(range(26,34))},'additions':[m.data() for m in [gold,spine,silver,portal,dark,white,jamb,stair,stairglass]],'report':report}
