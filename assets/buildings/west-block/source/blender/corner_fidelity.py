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
# Ground-level bookshop: visible paired storefronts below the curved title, blue folded awning and pale door frames.
for a in [MID-.44,MID+.40]:
 nr=Vector((math.cos(a),math.sin(a),0));tv=Vector((-nr.y,nr.x,0));q=Vector((CX,CY,1.10))+nr*(R+.02)
 for u in [-1.1,0,1.1]:
  p=q+tv*u;box(p,(.08,.08,2.15),'west_metal_edge')
 face('west_shop_glass',[q-tv*1.1-Vector((0,0,1.05)),q+tv*1.1-Vector((0,0,1.05)),q+tv*1.1+Vector((0,0,1.05)),q-tv*1.1+Vector((0,0,1.05))])
 for z in [.1,2.15]:
  p=q.copy();p.z=z;box(p,(2.3,.08,.08),'west_metal_edge',a+math.pi/2)
 # sloping blue canopy wraps each of the two door planes rather than the unrelated southern frontage
 p=q+Vector((0,0,1.15));a1=p-tv*1.2;b1=p+tv*1.2
 face('west_book_awning',[a1,b1,b1+nr*.95-Vector((0,0,.32)),a1+nr*.95-Vector((0,0,.32))])
 face('west_book_awning',[a1+nr*.95-Vector((0,0,.32)),b1+nr*.95-Vector((0,0,.32)),b1+nr*.95-Vector((0,0,.48)),a1+nr*.95-Vector((0,0,.48))])

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
