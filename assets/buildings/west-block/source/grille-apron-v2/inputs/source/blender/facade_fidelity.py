"""Photo-observed facade types; local dimensions inferred, geographic frontage unchanged."""
mat('west_tile_joint',(.30,.32,.29),0,.88)
mat('west_metal_edge',(.55,.57,.54),.65,.3)
mat('west_curtains',(.7,.8,.75),0,.82,'curtain')
for tex in ['clinic_upper','clinic_lower','sushi','middle_tenants','fruit_shop_band']:
 mat('west_sign_'+tex,(1,1,1),0,.75,tex)
# Light cream ceramic skin and dark green enamel bands are the actual visible materials.
M['west_tile_trim'].node_tree.nodes['Principled BSDF'].inputs['Base Color'].default_value=(.66,.67,.60,1)
M['west_fruit_glass'].node_tree.nodes['Principled BSDF'].inputs['Base Color'].default_value=(.20,.34,.30,1)
M['west_awning'].node_tree.nodes['Principled BSDF'].inputs['Base Color'].default_value=(.018,.115,.095,1)

def solid(x,z,w,h,depth,name,offset=0):
 c=Vector((x,south_y(x),z))+n*offset
 box(c,(w,depth,h),name,angle)
def framed(x,z,w,h,offset=-.22,frame='west_metal_edge'):
 for xx in [x-w/2,x+w/2]:solid(xx,z,.065,h+.1,.10,frame,offset)
 for zz in [z-h/2,z+h/2]:solid(x,zz,w+.07,.065,.10,frame,offset)
def tile_wall(x,z,w,h,offset=0,depth=.20):
 solid(x,z,w,h,depth,'west_tile_trim',offset-depth/2)
 # The photo resolves a square ceramic panel grid. Geometry joints remain visible from oblique views.
 cols=max(1,round(w/.54));rows=max(1,round(h/.54))
 for i in range(1,cols):panel(x-w/2+w*i/cols,z,.013,h,'west_tile_joint',offset+.008)
 for j in range(1,rows):panel(x,z-h/2+h*j/rows,w,.013,'west_tile_joint',offset+.008)
def opening(x,z,w,h,depth=.8,glass=False):
 # Four true return walls connect the open street plane to a dark interior back plane.
 solid(x-w/2-.07,z,.14,h+.15,depth,'west_tile_trim',-depth/2)
 solid(x+w/2+.07,z,.14,h+.15,depth,'west_tile_trim',-depth/2)
 solid(x,z-h/2-.06,w,.12,depth,'west_tile_trim',-depth/2)
 solid(x,z+h/2+.06,w,.12,depth,'west_tile_trim',-depth/2)
 panel(x,z,w,h,'west_shop_glass' if glass else 'west_recess',-depth)

def awning(x,w,material,depth=1.35,z=3.0):
 c=Vector((x,south_y(x),z));a=c-t*w/2;b=c+t*w/2
 frontA=a+n*depth-Vector((0,0,.18));frontB=b+n*depth-Vector((0,0,.18))
 face(material,[a+Vector((0,0,.35)),b+Vector((0,0,.35)),frontB,frontA])
 face(material,[frontA,frontB,frontB-Vector((0,0,.17)),frontA-Vector((0,0,.17))])
 for side in (a,b):face(material,[side+Vector((0,0,.35)),side+n*depth-Vector((0,0,.18)),side+n*depth-Vector((0,0,.35)),side-Vector((0,0,.12))])
 solid(x,z-.23,w+.04,.055,.08,'west_metal_edge',depth)
 # Thin sewn divisions and two support arms, not random weathering.
 for u in [-w*.32,w*.32]:
  q=Vector((x,south_y(x),z))+t*u
  solid(x+u,z+.05,.035,.09,depth,'west_frame',depth/2)

fruit=F['fruit_frontage'];fx,fw=-52.55,9.0;mid=F['middle_frontage'];rx=-57.82;rw=1.45
floors=[4.75,8.35,11.95,15.55];h=2.70
# Broad tiled left pier is strongly characteristic, as are the thin right pier and true dark shaft.
tile_wall(-60.15,10.5,3.2,16.2)
tile_wall(-47.52,10.5,.36,16.2)
# Side returns of tile facade, floor slabs connect the dark recess with the glazed facade.
for idx,z in enumerate(floors):
 opening(rx,z,rw,h,depth=1.05)
 # Main windows are set behind the outer ceramic piers. Curtain image is sampled only from top-floor Jan glass.
 opening(fx,z,fw,h,depth=.38,glass=True)
 for i in range(12):
  w=fw/12;cx=fx-fw/2+(i+.5)*w
  c=Vector((cx,south_y(cx),z))+n*(-.28)
  pts=[c-t*w/2-Vector((0,0,h/2)),c+t*w/2-Vector((0,0,h/2)),c+t*w/2+Vector((0,0,h/2)),c-t*w/2+Vector((0,0,h/2))]
  face('west_curtains',pts,[(i/12,0),((i+1)/12,0),((i+1)/12,1),(i/12,1)])
  # Fine subsidiary vertical strips follow broad irregular window groups below.
  solid(cx-w/2,z,.026,h,.05,'west_metal_edge',-.18)
 for fraction in [0,.22,.48,.75,1]:
  solid(fx-fw/2+fw*fraction,z,.065,h+.08,.10,'west_metal_edge',-.16)
 for zz in [z-h/2,z+h/2]:solid(fx,zz,fw,.065,.10,'west_metal_edge',-.16)
 # Horizontal heavy enamel fascias and pale sill lips cast real shadows; recess slab is visibly contiguous.
 solid(-53.94,z-h/2-.28,12.92,.49,.55,'west_awning',.17)
 solid(-53.94,z-h/2-.56,13.05,.12,.66,'west_tile_trim',.18)
 solid(-53.94,z+h/2+.11,12.9,.15,.38,'west_awning',.08)
 # Small recessed window on back of each shaft, not an opaque decal on the face.
 # Deep shaft apertures are dark; no unobserved bright back window grid.
 panel(rx,z,.9,1.98,'west_recess',-1.02)
panel(fx-fw*.3,floors[0],.55,2.5,'west_shop_glass',-.15)
# Date specific tenant lettering must stay in January layer, not baked into the architecture.
panel(fx,11.25,fw,.70,'west_sign_clinic_upper',-.11,'signs')
panel(fx,7.63,fw,.70,'west_sign_clinic_lower',-.11,'signs')
panel(-49.0,4.92,2.7,2.0,'west_sign_sushi',.40,'signs')
solid(-49.0,4.92,2.83,2.13,.30,'west_metal_edge',.20)
panel(fx,3.35,fw,.50,'west_sign_fruit_shop_band',.22,'signs')
tile_wall(-54.65,17.12,14.5,.20)
# Header: tiled surround, narrow maintenance rail, individual floodlight brackets.
tile_wall(-54.65,19.2,14.5,4.0)
for x in [-60.5,-57.8,-55.1,-52.4,-49.7]:
 solid(x,21.50,.07,.75,.06,'west_frame',.30)
 solid(x,21.88,.18,.18,.62,'west_frame',.45)
 solid(x,21.92,.42,.20,.22,'west_metal_edge',.78)
solid(-54.8,21.65,14,.08,.07,'west_frame',.30)
# Real inset shop bays, thresholds and frames. Display layout dimensions inferred where people occlude it.
for x,w in [(-58.5,4.8),(-53.3,4.8),(-49.6,1.8)]:
 opening(x,1.43,w,2.65,depth=1.0,glass=True)
 framed(x,1.43,w,2.65,-.22)
 for u in [-.33,.33]:
  framed(x+w*u,1.43,w*.33,2.65,-.22,'west_frame')
 solid(x,.08,w,.16,.6,'west_tile_trim',.08)
 solid(x,2.69,w-.2,.07,.10,'west_shop_light',-.5)
 # low display/plinth catches light through the storefront recess
 solid(x,.6,w-.4,.65,.38,'west_frame',-.7)
for x in [-61,-56,-50.6,-48.5]:tile_wall(x,1.5,.20,3)
awning(-55.4,12,'west_awning',1.65)
# Narrow middle shaft is a sequence of aluminum-frame windows and tenant boards.
for z in [4.4,7.5,10.6,13.7,16.8]:
 opening(-43.7,z,1.5,2.75,.62,True)
 framed(-43.7,z,1.5,2.75,-.2)
 solid(-43.7,z,.06,2.75,.1,'west_metal_edge',-.18)
 solid(-43.7,z,1.5,.065,.1,'west_metal_edge',-.18)
for x in [-44.62,-42.78]:tile_wall(x,10,.25,19.8)
panel(-45.65,11.3,.95,8.7,'west_sign_middle_tenants',.28,'signs')
solid(-45.65,11.3,1.05,8.8,.22,'west_wall_corner',.1)
opening(-43.7,1.4,1.7,2.7,.7,True);framed(-43.7,1.4,1.7,2.7,-.12)
awning(-43.7,2.7,'west_awning',1.25)
# Pharmacy sign sits in a blue rim and above a recessed entrance, not on a featureless cube.
tile_wall(-64.6,10.0,5.25,14.0)
for z in [4.7,8.6,12.5]:
 for x in [-66.1,-64.4,-62.8]:
  panel(x,z,1.30,2.3,'west_glass',.12);framed(x,z,1.30,2.3,.18)
solid(-64.65,9.5,4.87,11.47,.24,'west_book_awning',.1)
opening(-65.0,1.42,4.0,2.7,.6,True);framed(-65,1.42,4,2.7,.12)
awning(-65.0,4.5,'west_pharmacy_awning',1.25)
for x in [-66.5,-65.6,-64.7,-63.8,-62.9]:
 solid(x,15.38,.06,.45,.1,'west_frame',.15)
 solid(x,15.55,.12,.12,.45,'west_metal_edge',.3)
# Blank roof panel is not flat white: fine vertical seams, edge returns and two rear rails are visible.
bp=fruit['roof_back_panel'];bx,bz,bw,bh=bp['x_m'],bp['center_height_m'],bp['width_m'],bp['height_m']
solid(bx,bz,bw,bh,.24,'west_tile_trim',-.02)
for i in range(1,65):panel(bx-bw/2+bw*i/65,bz,.009,bh,'west_tile_joint',.112)
for x in [bx-bw/2,bx+bw/2]:solid(x,bz,.10,bh+.15,.3,'west_metal_edge',0)
for z in [bz-bh/2,bz+bh/2]:solid(bx,z,bw,.10,.3,'west_metal_edge',0)
for x in [bx-bw*.4,bx,bx+bw*.4]:solid(x,22.7,.12,2.5,.12,'west_frame',-.2)
