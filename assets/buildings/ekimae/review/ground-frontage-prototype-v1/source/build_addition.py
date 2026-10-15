"""Review prototype only. Blender 4.2.3; authored geometry, no photographic textures."""
import bpy,math,random,json,sys
from mathutils import Vector
from pathlib import Path
R=Path(__file__).resolve().parents[1];assert bpy.app.version==(4,2,3)
bpy.ops.wm.read_factory_settings(use_empty=True)
B=Vector((-46.78,-10.647,0));T=Vector((.9991711854627296,-.04070555417880273,0));N=Vector((.04070555417880273,.9991711854627296,0))
def xyz(u,d,h):return B-T*u+N*d+Vector((0,0,h))
M={};G={}
def mat(name,col,rough=.5,metal=0,alpha=1):
 m=bpy.data.materials.new('prototype_'+name);m.diffuse_color=(*col,alpha);m.use_nodes=True;p=m.node_tree.nodes['Principled BSDF'];p.inputs['Base Color'].default_value=(*col,1);p.inputs['Metallic'].default_value=metal;p.inputs['Roughness'].default_value=rough;p.inputs['Alpha'].default_value=alpha
 if alpha<1:m.surface_render_method='DITHERED'
 M[name]=m
for args in [('gold',(.57,.36,.065),.28,.55),('pale',(.68,.65,.53),.8),('seam',(.31,.29,.24),.85),('cream',(.72,.68,.53),.7),('glass',(.35,.45,.40),.10,.05,.055),('interior',(.18,.15,.10),.9),('green',(.055,.095,.043),.9),('lightleaf',(.12,.17,.07),.9),('olive',(.16,.18,.10),.9),('stem',(.075,.068,.033),.95)]:mat(*args)
def face(name,points):
 vs,fs=G.setdefault(name,([],[]));i=len(vs);vs.extend([xyz(*p) for p in points]);fs.append(tuple(range(i,i+len(points))))
def box(name,u0,u1,d0,d1,z0,z1):
 p=[(u,d,z) for z in [z0,z1] for d in [d0,d1] for u in [u0,u1]]
 for ids in [(0,1,3,2),(4,6,7,5),(0,4,5,1),(2,3,7,6),(0,2,6,4),(1,5,7,3)]:face(name,[p[i] for i in ids])
def strip(name,a,b,z0,z1,thick=.04):
 ax,ay=a;bx,by=b;dx=bx-ax;dy=by-ay;l=math.hypot(dx,dy);nx=-dy/l*thick/2;ny=dx/l*thick/2
 ps=[(ax-nx,ay-ny),(bx-nx,by-ny),(bx+nx,by+ny),(ax+nx,ay+ny)]
 for j in range(4):k=(j+1)%4;face(name,[(*ps[j],z0),(*ps[k],z0),(*ps[k],z1),(*ps[j],z1)])
 for z in [z0,z1]:face(name,[(*p,z) for p in ps])
def arc_at_u(u,off):
 lo=math.radians(50);hi=math.radians(90)
 for _ in range(60):
  a=(lo+hi)/2;x=-47.25+(8.72+off)*math.cos(a);y=-19.25+(8.72+off)*math.sin(a);uu=-((x-B.x)*T.x+(y-B.y)*T.y)
  if uu<u:lo=a
  else:hi=a
 d=(x-B.x)*N.x+(y-B.y)*N.y
 return (u,d)

# Fixed display envelope follows original corner, not the generated circular wall.
cut=arc_at_u(-1.70,.11);C=(0,.10);D=(cut[0]*.75,cut[1]*.75+C[1]*.25);Q=(1.20,.10)
for a,b in [(D,C),(C,Q)]:
 strip('gold',a,b,0,.145,.105);strip('gold',a,b,2.60,2.69,.075)
 face('glass',[(*a,.145),(*b,.145),(*b,2.62),(*a,2.62)])
for u,d in [D,C,Q]:box('gold',u-.025,u+.025,d-.035,d+.035,.145,2.69)
# Opaque interior back and terminal sides close the planted glazed bay, within old envelope.
foot=[D,C,Q,(1.2,-.60),(D[0],-.60)]
face('interior',[(*p,.02) for p in foot]);face('interior',[(*p,2.69) for p in foot])
for a,b in zip(foot[2:],foot[3:]+[foot[0]]):strip('green',a,b,.02,2.69,.025)
# Entry outer surround, broad fixed transom, two narrow glazed sidelights, no handles/mechanism claim.
for u in [1.20,3.20]:box('gold',u-.035,u+.035,-.12,.13,.015,2.70)
box('gold',1.20,3.20,-.12,.13,2.36,2.70)
for u in [1.58,2.82]:box('gold',u-.023,u+.023,-.10,.115,.035,2.37)
for a,b in [(1.235,1.557),(2.843,3.165)]:
 face('glass',[(a,.095,.10),(b,.095,.10),(b,.095,2.36),(a,.095,2.36)])
 box('gold',a,b,-.12,.13,.035,.105)
# Central opening remains open. A recessed, neutral floor and back give depth, not an invented moving door.
box('pale',1.235,3.165,-1.08,.09,.0,.035)
# Neutral transparent inner boundary, not a sealed blank panel.
face('glass',[(1.235,-1.07,.035),(3.165,-1.07,.035),(3.165,-1.07,2.36),(1.235,-1.07,2.36)])
for u in [1.235,3.165]:face('pale',[(u,.09,.035),(u,-1.08,.035),(u,-1.08,2.36),(u,.09,2.36)])
# Pale tiled terminal pier is distinct from preserved upper yellow louver and kiosk remainder.
box('pale',3.235,3.70,-.60,.115,0,2.87)
for z in [.58,1.16,1.74,2.32]:box('seam',3.237,3.698,.115,.117,z-.006,z+.006)
# Connect the bounded original arc cut to diagonal corner-return; not a hidden gap behind plants.
cut=arc_at_u(-1.70,.11)
face('glass',[(*cut,.145),(*D,.145),(*D,2.60),(*cut,2.60)])
strip('gold',D,D if False else (D[0]+.025,D[1]),.145,2.69,.05)
strip('gold',cut,D,.02,.14,.075)
strip('gold',cut,D,2.60,2.69,.065)
# Closed header backing and side transition beneath soffit, not vegetation used as a gap cover.
box('pale',0,3.7,-.60,-.15,2.69,2.975)
strip('pale',cut,D,2.69,2.975,.035)
strip('pale',D,C,2.69,2.975,.035)
box('pale',3.65,3.70,-.60,.208,0,2.975)
box('pale',-1.701,-1.699,-1.10,cut[1]+.10,0,2.975)
# Local cream soffit closes setback beneath the preserved continuous gold canopy.
outer=[arc_at_u(-1.70,.70)]
for i in range(1,13):
 u=-1.70+(1.70+.474373)*i/12
 if u<.474:outer.append(arc_at_u(u,.70))
outer +=[(.474373,.797771),(3.70,.797771)]
soffit=outer+[(3.70,-.60),(-1.275,-1.1),(-1.70,-1.1)]
face('cream',[(*p,2.975) for p in soffit])
for u in [0,1.2,3.2]:box('gold',u-.018,u+.018,-.25,.79,2.955,2.975)
# Recessed plant volume: varied, small authored leaves behind glazing, never exterior hedge.
rng=random.Random(60739635)
for j in range(4000):
 if j<2300:
  u=max(.09,min(1.10,rng.gauss([.23,.53,.86][j%3],.15)));d=rng.uniform(-.48,-.12);z=max(.24,min(2.55,rng.gauss([.43,.99,1.51,2.1,2.40][j%5],.23)))
 else:
  t=rng.uniform(.08,.94);u=D[0]*(1-t)+C[0]*t;d=D[1]*(1-t)+C[1]*t-.13-rng.uniform(0,.20);z=rng.uniform(.18,2.63)
 size=rng.uniform(.033,.10);angle=rng.uniform(0,math.tau)
 # Alternating lanceolate and broad oval folded leaves, not repeated diamonds.
 width=size*rng.uniform(.20,.36) if j%3==0 else size*rng.uniform(.45,.72)
 length=size*rng.uniform(.8,1.35);tilt=rng.uniform(-.6,.6)
 a=Vector((math.cos(angle)*width,math.sin(angle)*width,width*tilt))
 b=Vector((math.sin(angle)*length*.25,math.cos(angle)*length*.18,length))
 c=Vector((u,d,z));ring=[c+a*math.cos(math.tau*k/6)+b*math.sin(math.tau*k/6) for k in range(6)]
 mid=c+Vector((0,-rng.uniform(.008,.022),rng.uniform(-.01,.01)))
 name=['green','green','lightleaf','olive'][j%4]
 for k in range(6):face(name,[ring[k],ring[(k+1)%6],mid])
# Thin authored stems through the layered clumps, entirely behind the glass.
for j in range(24):
 u=.10+(j%8)*.14 if j<16 else D[0]+.12+(j-16)*.13
 d=-.33;z=.15
 for k in range(12):
  q=(u+math.sin(k*.8+j)*.025,d+math.cos(k*.7+j)*.025,z+.205)
  radius=.006
  for a in range(4):
   aa=math.tau*a/4;bb=math.tau*(a+1)/4
   face('stem',[(u+radius*math.cos(aa),d+radius*math.sin(aa),z),(u+radius*math.cos(bb),d+radius*math.sin(bb),z),(q[0]+radius*math.cos(bb),q[1]+radius*math.sin(bb),q[2]),(q[0]+radius*math.cos(aa),q[1]+radius*math.sin(aa),q[2])])
  u,d,z=q
# Hanging band bounded to shop, recessed behind canopy, not occupying opening below transom.
# Pendulous irregular clusters with mixed leaf scales; fringe is not a straight rectangle.
for cluster in range(72):
 u0=-1.20+4.32*cluster/71+rng.uniform(-.035,.035)
 drop=rng.uniform(.12,.36)
 for j in range(25):
  t=j/24;u=u0+rng.uniform(-.065,.065);d=-.04+rng.uniform(-.02,.02);z=2.85-drop*t+rng.uniform(-.01,.01)
  sz=rng.uniform(.04,.085);w=sz*rng.uniform(.4,.75);ang=rng.uniform(0,math.tau)
  a=Vector((math.cos(ang)*w,math.sin(ang)*w,0));b=Vector((.008,0,sz));c=Vector((u,d,z));ring=[c+a*math.cos(math.tau*k/6)+b*math.sin(math.tau*k/6) for k in range(6)]
  for k in range(6):face('green' if j%3 else 'olive',[ring[k],ring[(k+1)%6],c+Vector((0,-.012,0))])
for name,(vs,fs) in G.items():
 me=bpy.data.meshes.new('frontage_'+name);me.from_pydata(vs,[],fs);me.materials.append(M[name]);me.update();ob=bpy.data.objects.new('frontage_'+name,me);bpy.context.collection.objects.link(ob)
 # All source faces are generated in local source coordinates; global transform remains identity.
bpy.ops.export_scene.gltf(filepath=str(R/'web/addition.glb'),export_format='GLB',export_yup=True)
(R/'evidence/inferred-dimensions.json').write_text(json.dumps({'units':'meters, model-conditioned estimates, NOT surveyed','north_display':[0,1.20],'entry':[1.20,3.20],'terminal_pier':[3.235,3.70],'entry_clear_center':[1.603,2.797],'transom_height':[2.36,2.70],'north_front_offset':.10,'display_depth':.70,'return_direction':'Straight connection from retained arc cut to B; angle inferred, not original wall12 chord','side_return_endpoint':D,'interior_depth':1.08,'local_soffit_z':2.975,'original_curve_cut':cut,'known_uncertainties':['Original curve/canopy preserved; angular real canopy still differs','Ground corner return extent and setback unmeasured','Central opening depiction does not establish real door leaf number or mechanism','Upper width used for scale is inherited inference']},indent=2))
