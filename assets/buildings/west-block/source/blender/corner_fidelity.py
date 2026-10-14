"""Architectural hardware observed in WB01/WB02. Hidden rear details remain intentionally simple."""
# Curved gray band carries squared cladding joints, not an anonymous uninterrupted surface.
for j in range(1,13):
 a=MID-(8*ws)/(2*R)+j*(8*ws)/(12*R)
 rr=R+.055
 x,y=CX+rr*math.cos(a),CY+rr*math.sin(a)
 if hi>lo:box((x,y,(hi+lo)/2),(.024,.024,hi-lo),'west_tile_joint')
# Thin inset frame around the flat red medicine fascia, with photo-observed square joints.
flank=corner['flat_flank'];xx,zz,ww,hh=[flank[k] for k in ['x_m','center_height_m','width_m','height_m']]
for x in [xx-ww/2,xx+ww/2]:solid(x,zz,.09,hh+.12,.20,'west_metal_edge',.12)
for z in [zz-hh/2,zz+hh/2]:solid(xx,z,ww,.10,.22,'west_metal_edge',.12)
# Actual photo texture contains the tile joints; add only outer depth and raised letters left unguessed.
# Rooftop sign casing has return thickness and regular frame rails.
for z in [B.z-H/2-.08,B.z+H/2+.08]:box((B.x,B.y,z),(W+.20,.25,.14),'west_metal_edge',yaw)
for u in [-W/2-.06,W/2+.06]:
 p=B+T*u;box((p.x,p.y,B.z),(.13,.25,H+.22),'west_metal_edge',yaw)
# Photo shows a row of small floodlight heads; nine per curved rim and six per DMM facet are density estimates, not individually measured counts.
for z,r,width,count in [(sc['rakuten']+corner['rakuten_height_m']/2+.22,R+.2,7.7*ws,9),(sc['rakuten']-corner['rakuten_height_m']/2-.20,R+.15,7.7*ws,9)]:
 for i in range(count):
  a=MID-width/(2*r)+width*i/(r*(count-1));nr=Vector((math.cos(a),math.sin(a),0));q=Vector((CX,CY,z))+nr*r
  box(q+nr*.23,(.09,.45,.075),'west_frame',a-math.pi/2)
  box(q+nr*.40+Vector((0,0,.12)),(.22,.20,.28),'west_metal_edge',a-math.pi/2)
# DMM floodlight brackets along both planar faces preserve the kink of the box.
for pa,pb in [(dleft,dhinge),(dhinge,dright)]:
 d=pb-pa;ang=math.atan2(d.y,d.x);out=Vector((d.y,-d.x,0)).normalized()
 for i in range(6):
  p=pa.lerp(pb,(i+.5)/6);p.z=zd-hd/2-.22
  box(p+out*.25,(.08,.58,.07),'west_frame',ang)
  box(p+out*.48+Vector((0,0,.12)),(.23,.20,.21),'west_metal_edge',ang)
# Ground storefronts: WB01 Jan31 and WB02 Feb07 resolve asymmetric solid/open faces.
# Use the same endpoints as the unchanged lettering and DMM planes, never radial floating bays.
# Dimensions below are inferred from visible proportions; no hidden interior or product graphics.
Z=Vector((0,0,1))
def shop_basis(a,b):
 tangent=(b-a).normalized();normal=Vector((tangent.y,-tangent.x,0))
 return tangent,normal,(b-a).length

def shop_face(a,b,u0,u1,z0,z1,material,depth=0):
 tv,nv,w=shop_basis(a,b)
 p=a+tv*(w*u0)+nv*depth;q=a+tv*(w*u1)+nv*depth
 face(material,[p+Z*z0,q+Z*z0,q+Z*z1,p+Z*z1])

def shop_solid(a,b,u0,u1,z0,z1,material,depth=.08,offset=0):
 tv,nv,w=shop_basis(a,b);q=a+tv*(w*(u0+u1)/2)+nv*offset+Z*((z0+z1)/2)
 box(q,(w*(u1-u0),depth,z1-z0),material,math.atan2(tv.y,tv.x))

# Left: broad pale shutter/panel field, shadowed upper strip, broad corner jamb.
a,b=dleft,dhinge
shop_solid(a,b,0,1,.02,2.20,'west_tile_trim',.18,-.09)
shop_face(a,b,.10,.83,1.42,2.06,'west_frame',.012)
shop_solid(a,b,.12,.82,.06,1.43,'west_tile_trim',.09,.025)
for u in [.10,.46,.83]:shop_solid(a,b,u,u+.014,.05,2.13,'west_metal_edge',.07,.06)
# Photos resolve broad pale panels, not evenly spaced shutter slats.
# Corner's pale pier continues down from the exact sign hinge.
shop_solid(a,b,.84,1,.02,2.18,'west_tile_trim',.20,-.07)

# Center-gai: light outer jambs, recessed dark doorway, display frames on each side.
a,b=dhinge,dright
tv,nv,w=shop_basis(a,b)
shop_face(a,b,0,1,.02,2.18,'west_recess',-.46)
for u0,u1 in [(0,.13),(.91,1)]:shop_solid(a,b,u0,u1,.02,2.18,'west_tile_trim',.46,-.23)
shop_solid(a,b,0,1,2.07,2.20,'west_tile_trim',.46,-.23)
shop_solid(a,b,.13,.91,.015,.07,'west_metal_edge',.53,-.23)
# Open entry between the two photo-resolved display fields. Neutral backing only.
for u0,u1 in [(.13,.31),(.66,.91)]:
 shop_face(a,b,u0,u1,.16,2.04,'west_shop_glass',-.10)
 for u in [u0,u1]:shop_solid(a,b,u,u+.018,.08,2.08,'west_metal_edge',.12,-.04)
 for z in [.18,.77,1.37,2.02]:shop_solid(a,b,u0,u1,z,z+.028,'west_frame',.12,-.035)
# Doorway returns connect opening to the dark back plane instead of painted-on glazing.
for u in [.31,.66]:
 p=a+tv*(w*u)
 face('west_tile_trim',[p+Z*.07,p-nv*.46+Z*.07,p-nv*.46+Z*2.07,p+Z*2.07])

# Unequal blue awnings share wall/sign planes but expose the photographed pale corner wedge.
# Both backs attach to the wall; closed end returns prevent floating roof fragments.
t0,n0,w0=shop_basis(dleft,dhinge);t1,n1,w1=shop_basis(dhinge,dright)
depth0,depth1=.68,.92
left_tip=dhinge+n0*depth0-t0*.18
right_tip=dhinge+n1*depth1+t1*.18
for pa,pb,fa,fb in [(dleft,dhinge,dleft+n0*depth0,left_tip),(dhinge,dright,right_tip,dright+n1*depth1)]:
 backa=pa+Z*2.17;backb=pb+Z*2.17;fronta=fa+Z*1.96;frontb=fb+Z*1.96
 face('west_book_awning',[backa,backb,frontb,fronta])
 face('west_book_awning',[fronta,frontb,frontb-Z*.13,fronta-Z*.13])
 # Pale sewn leading edge seen in both photos, with closed triangular end returns.
 face('west_tile_trim',[fronta+Z*.025,frontb+Z*.025,frontb-Z*.018,fronta-Z*.018])
 for back,front in [(backa,fronta),(backb,frontb)]:face('west_book_awning',[back,front,front-Z*.13,back-Z*.06])
 # Discreet seams follow the roof slope, not fake wall tilt.
 for f in [.25,.50,.75]:
  v=backa.lerp(backb,f);q=fronta.lerp(frontb,f);dv=(frontb-fronta).normalized()*.006
  face('west_frame',[v-dv+Z*.004,v+dv+Z*.004,q+dv+Z*.004,q-dv+Z*.004])

# Separate top pharmacy sign and two planar Taiseido lettering faces, all Jan31 photo extractions.
for tex in ['sanzenri','taiseido_left','taiseido_right']:mat('west_sign_'+tex,(1,1,1),0,.7,tex)
solid(-40.96,20.0,3.92,7.90,.24,'west_metal_edge',.15)
panel(-40.96,20.0,3.72,7.70,'west_sign_sanzenri',.29,'signs')
for pa,pb,tex in [(dleft,dhinge,'taiseido_left'),(dhinge,dright,'taiseido_right')]:
 z,h=3.0,1.60
 pts=[Vector((pa.x,pa.y,z-h/2)),Vector((pb.x,pb.y,z-h/2)),Vector((pb.x,pb.y,z+h/2)),Vector((pa.x,pa.y,z+h/2))]
 face('west_sign_'+tex,pts,[(0,0),(1,0),(1,1),(0,1)],'signs')
 for zz in [z-h/2-.06,z+h/2+.06]:
  d=pb-pa;q=(pa+pb)/2;box((q.x,q.y,zz),(d.length,.12,.12),'west_metal_edge',math.atan2(d.y,d.x))
