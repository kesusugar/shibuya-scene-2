"""Photo-led Ekimae facade. Geometry dimensions are inferred, not surveyed.
EK01 November 2025 defines sign era. EK02/03 corroborate architecture only.
All helpers batch by material; seed fixed for reproducible decorative planting.
"""
import math,random
from mathutils import Vector

def build(g):
 globals().update(g)
 rng=random.Random(60739635)
 for name,col,rough,metal in [('ek_reveal',(.022,.028,.024),.8,0),('ek_silver',(.43,.45,.42),.33,.55),('ek_gold_dark',(.29,.18,.045),.42,.45),('ek_leaf',(.055,.105,.028),.85,0),('ek_leaf_light',(.15,.19,.055),.85,0),('ek_lavender',(.19,.105,.24),.8,0),('ek_glass_blue',(.105,.145,.155),.3,.3),('ek_glass_warm',(.08,.075,.05),.24,.18),('ek_cafe_ceiling',(.55,.39,.16),.7,0)]:mat(name,col,rough,metal)
 # Shallow transparent glazing reveals modelled interior strips, not a pasted facade photograph.
 for name in ['ek_glass','ek_glass_blue','ek_glass_warm']:
  p=M[name].node_tree.nodes.get('Principled BSDF');p.inputs['Alpha'].default_value=.62
  M[name].surface_render_method='DITHERED'
 # Continuous arc + short north return; east wing is a separate facade.
 total=F['rooftop']['developed_width_m']-.26*(START-END);curve=R*(START-END)
 def point(s,off=0):
  if s<=curve:
   a=END+s/R;n=Vector((math.cos(a),math.sin(a),0));return Vector((CX,CY,0))+n*(R+off),n
  return Vector((CX,CY+R,0))-T*(s-curve)+N*off,N
 def surf(s0,s1,z0,z1,name,off=0,layer='base',uvspan=(0,1)):
  n=max(1,math.ceil((s1-s0)/.65))
  for i in range(n):
   sa=s0+(s1-s0)*i/n;sb=s0+(s1-s0)*(i+1)/n;p,na=point(sa,off);q,nb=point(sb,off)
   u0=uvspan[0]+(uvspan[1]-uvspan[0])*i/n;u1=uvspan[0]+(uvspan[1]-uvspan[0])*(i+1)/n
   face(name,[(p.x,p.y,z0),(p.x,p.y,z1),(q.x,q.y,z1),(q.x,q.y,z0)],[(u0,0),(u0,1),(u1,1),(u1,0)],layer)
 def solid(s0,s1,z0,z1,name,inner=.0,outer=.22):
  surf(s0,s1,z0,z1,name,outer);surf(s0,s1,z0,z1,name,inner)
  n=max(1,math.ceil((s1-s0)/.65))
  for i in range(n):
   a=s0+(s1-s0)*i/n;b=s0+(s1-s0)*(i+1)/n;pa,_=point(a,inner);pb,_=point(b,inner);qa,_=point(a,outer);qb,_=point(b,outer)
   for z in [z0,z1]:face(name,[(pa.x,pa.y,z),(qa.x,qa.y,z),(qb.x,qb.y,z),(pb.x,pb.y,z)])
  for s in [s0,s1]:
   p,_=point(s,inner);q,_=point(s,outer);face(name,[(p.x,p.y,z0),(q.x,q.y,z0),(q.x,q.y,z1),(p.x,p.y,z1)])
 def beam(p,q,width,name):
  p=Vector(p);q=Vector(q);d=(q-p).normalized();x=d.cross(Vector((0,0,1)))
  if x.length<.01:x=d.cross(Vector((0,1,0)))
  x.normalize();x*=width/2;y=d.cross(x).normalized()*width/2
  ps=[p-x-y,p+x-y,p+x+y,p-x+y,q-x-y,q+x-y,q+x+y,q-x+y]
  for ids in [(0,3,2,1),(4,5,6,7),(0,1,5,4),(1,2,6,5),(2,3,7,6),(3,0,4,7)]:face(name,[ps[i] for i in ids])
 # North straight wing: real red window infills with projecting aluminum grid.
 for z in [5.1,8.5,11.9,15.3,18.7,22.1,25.5,28.9]:
  for j,u in enumerate([1.2,3.4,5.6,7.8]):
   panel(u,z,1.9,2.85,'ek_reveal',.11);panel(u,z-.7,1.65,1.1,'ek_red_frame',.14)
   panel(u,z+.28,1.61,1.85,['ek_glass','ek_glass_blue','ek_glass_warm'][(j+int(z))%3],.16)
   for uu in [u-.89,u+.89]:
    p=A+T*uu+N*.25;beam((p.x,p.y,z-1.4),(p.x,p.y,z+1.4),.1,'ek_silver')
   p=A+T*u+N*.27;beam(p-T*.9+Vector((0,0,z-.5)),p+T*.9+Vector((0,0,z-.5)),.08,'ek_silver')
  for zz in [z-1.55,z+1.48]:panel(L/2,zz,L,.2,'ek_band',.29)
 # Long return wing remains compatible with PLATEAU back/roof; windows not full flat black rectangles.
 for z in [5.1,8.5,11.9,15.3,18.7,22.1,25.5,28.9]:
  for i in range(17):
   u=1.15+1.95*i
   if u>EL-.8:break
   east_panel(u,z,1.8,2.7,'ek_reveal',.12);east_panel(u,z-.6,1.55,1.2,'ek_red_frame',.18);east_panel(u,z+.4,1.5,1.65,'ek_glass_blue',.2)
   for du in [-.85,.85]:
    p=E+ET*(u+du)+EN*.29;beam((p.x,p.y,z-1.38),(p.x,p.y,z+1.38),.09,'ek_silver')
  east_panel(23.5,z-1.5,21,.2,'ek_band',.31)
 # Ground-floor frontage on the long wing, shop identities not invented.
 for u in [2,5,8,11,14,17,20,23,26,29,32]:
  east_panel(u,1.45,2.75,2.7,'ek_shop_glass',.15)
  for du in [-1.38,1.38]:
   p=E+ET*(u+du)+EN*.3;beam((p.x,p.y,.05),(p.x,p.y,2.9),.085,'ek_silver')
 east_panel(EL/2,3.1,EL,.35,'ek_steel',.3)
 for u in [1.5,4.5,7.5]:panel(u,1.5,2.7,2.8,'ek_shop_glass',.28)
 # Curved cafe: dark glazing at shallow recess behind gold/aluminum spandrels.
 surf(0,total,0,31.3,'ek_reveal',.04)
 for floor,(z0,z1) in enumerate([(0.25,3.15),(3.45,6.55),(6.85,10.0),(10.4,13.55),(13.9,17.1),(17.5,20.55)]):
  count=18 if floor==5 else 7 if floor>0 else 10
  step=total/count
  for j in range(count):
   lo=j*step;hi=(j+1)*step
   surf(lo+.06,hi-.06,z0+.06,z1-.06,['ek_glass','ek_glass_blue','ek_glass_warm'][(j+floor)%3],.11)
   # Horizontal interior planes and dim warm shelves give volume, not pasted black glazing.
   if floor<=4:
    solid(lo+.12,hi-.12,z0+.70,z0+.79,'ek_gold_dark' if floor<3 else 'ek_steel',.055,.085)
    solid(lo+.12,hi-.12,z1-.22,z1-.12,'ek_cafe_ceiling' if floor<3 else 'ek_silver',.055,.082)
    for ss in [lo+.4,hi-.45]:
     solid(ss,ss+.12,z0+.15,z0+.7,'ek_gold_dark',.055,.087)
   solid(lo,lo+(.035 if floor<3 else .075),z0,z1,'ek_silver',.12,.26)
   if floor>=3:
    solid(lo,hi,z0+.75,z0+.81,'ek_silver',.12,.22)
    solid((lo+hi)/2-.025,(lo+hi)/2+.025,z0,z1,'ek_silver',.12,.21)
  solid(0,total,z0-.12,z0+.04,'ek_gold' if floor<3 else 'ek_band',.0,.36)
  solid(0,total,z1-.04,z1+.16,'ek_gold' if floor<3 else 'ek_band',.0,.36)
  if floor<=2:
   # Corner glazing sits between golden side piers, not a yellow ground-floor tube.
   for a,b in [(0,1.0),(total-1.25,total)]:
    solid(a,b,z0,z1,'ek_yellow',.08,.43)
    for zz in [z0+.25,z0+1.05,z0+1.85,z0+2.55]:solid(a,b,zz,zz+.045,'ek_gold_dark',.43,.445)
 # Cafe plant decor: small low-poly leaf tufts along bands, not scene tree edits.
 for zbase in [3.4,6.8,9.9]:
  surf(1,total-1.3,zbase-.35,zbase+.15,'ek_leaf',.31)
  for j in range(245):
   center=[1.5,4.5,10.8,15.7,total-1.8][j%5];s=max(1,min(total-1.3,rng.gauss(center,.85)));z=zbase+rng.uniform(-.65,.25);p,n=point(s,.37+rng.uniform(0,.11));sz=rng.uniform(.09,.24)
   # diamond clusters, four faces, varied photosupported green/lavender accents
   material='ek_lavender' if j%9==0 else 'ek_leaf_light' if j%3==0 else 'ek_leaf'
   tangent=Vector((-n.y,n.x,0));a=Vector((p.x,p.y,z));pts=[a+tangent*sz,a+Vector((0,0,sz*.8)),a-tangent*sz,a-Vector((0,0,sz*.8)),a+n*.13]
   for k in range(4):face(material,[pts[k],pts[(k+1)%4],pts[4]])
 # Entrance framing, separated transoms, door bars and bright canopy underside.
 for s in [curve*.44,curve+6.3]:
  for ds in [-1.05,1.05]:solid(s+ds-.065,s+ds+.065,.12,2.85,'ek_gold',.15,.46)
  solid(s-1.1,s+1.1,2.8,3.02,'ek_gold',.15,.48)
  for ds in [-.16,.16]:
   p,n=point(s+ds,.39);beam((p.x,p.y,.85),(p.x,p.y,1.65),.045,'ek_silver')
 solid(.6,total-.6,2.98,3.12,'ek_gold',.25,.72)
 surf(5.8,10.0,8.3,9.5,'ek_sign_loccitane',.43,'signs',(0,1))
 # Tiled piers and 6F narrow windows create the characteristic vertical rhythm.
 for s in [.1,total-1.0]:
  solid(s,s+.8,10.4,20.8,'ek_band',.1,.4)
  for zz in [11,12.4,13.8,15.2,16.6,18,19.4]:solid(s,s+.8,zz,zz+.035,'ek_steel',.4,.415)
 # Upper restaurant sign strips remain in a separate dated layer, once across front.
 for band in F['restaurant_alignment']['bands']:
  name,z0,z1=band['name'],band['z0'],band['z1']
  surf(0,total,z0,z1,'ek_sign_'+name,.44,'signs',(0,1))
  # Only floor-edge trim. Uniform bay bars would wrongly cross continuous lettering.
  for zz in [z0,z1]:solid(0,total,zz-.045,zz+.045,'ek_band',.2,.49)
  if name=='gusto':solid(0,total,z0-.48,z0-.04,'ek_band',.1,.47)
 east_panel(2.6,17.2,2.8,22,'ek_sign_eyecity',.43,'signs')
 # Tall 17LIVE return billboard, present in the same November reference, not a fabricated generic banner.
 panel(L-8.2,17.5,3.0,26.1,'ek_screen_back',.38)
 panel(L-8.2,17.5,2.85,25.9,'ek_sign_longboard',.45,'signs')
 # Roof display: continuous backing, visible side thickness and real support lattice.
 roof=F['rooftop'];z=roof['center_height_m'];h=roof['height_m'];bot=z-h/2;top=z+h/2
 solid(0,total,bot-.12,top+.12,'ek_screen_back',-.35,.23)
 surf(0,total,bot,top,'ek_sign_samsung',.26,'signs',(0,1))
 east_panel(12.45,z,24.32,17.28,'ek_screen_back',.25);east_panel(8.4,z,16.0,17.13,'ek_sign_hit_sky',.30,'signs')  # unseen remainder stays neutral backing, never extrapolated
 for s in [total*i/12 for i in range(13)]:
  p,n=point(s,-.5);q=p-n*1.7
  beam((p.x,p.y,31.1),(p.x,p.y,top),.13,'ek_steel');beam((q.x,q.y,31.1),(p.x,p.y,bot+2),.12,'ek_steel')
 for i in range(12):
  p,_=point(total*i/12,-.5);q,_=point(total*(i+1)/12,-.5)
  for zz in [31.6,bot-.3]:beam((p.x,p.y,zz),(q.x,q.y,zz),.13,'ek_steel')
  beam((p.x,p.y,31.6),(q.x,q.y,bot-.3),.12,'ek_steel')
  beam((q.x,q.y,31.6),(p.x,p.y,bot-.3),.12,'ek_steel')
 # Floodlights fixed atop billboard, with short brackets and shallow housings.
 for s in [total*i/8 for i in range(9)]:
  p,n=point(s,.12);q=p+n*.5
  beam((p.x,p.y,top),(q.x,q.y,top+.65),.06,'ek_steel');box((q.x,q.y,top+.65),(.4,.25,.18),'ek_silver')
 for u in [.3,6.3,12.45,18.5,24.6]:
  p=E+ET*u-EN*.3
  beam((p.x,p.y,31.2),(p.x,p.y,top),.13,'ek_steel')
  q=p+EN*.8;beam((p.x,p.y,top),(q.x,q.y,top+.65),.06,'ek_steel');box((q.x,q.y,top+.65),(.4,.25,.18),'ek_silver')
