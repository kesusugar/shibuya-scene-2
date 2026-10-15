"""Bounded six apertures and wing72/86 recess. Geometry estimates, not survey.
Read-only pinned input; build() returns original triangle masks and indexed additions.
Coordinates are Blender Z-up. Copyrighted reference images are not dependencies.
"""
from pathlib import Path
import json, struct, hashlib, math
import numpy as np
ROOT=Path(__file__).resolve().parents[1]
PIN='a31e295bf8ce9bbef9ddc0c6164526db84cb7b08a6caf1957352be142854db90'
A=np.array([[-132.981,1.713],[-130.891,2.920],[-129.474,4.872],[-128.976,7.229],[-129.480,9.585],[-130.902,11.533],[-132.996,12.735]])
U=np.r_[0,np.cumsum(np.linalg.norm(np.diff(A,axis=0),axis=1))];MID=U[3]-.30
SLOTS=[(10.05,4.35,.55,.58),(14.25,4.10,.48,.53),(18.45,3.95,.45,.50)]+[(z,3.95,.45,.50) for z in [22.65,26.85,31.05]]
SLOT_RECTS=[r for z,w,h,d in SLOTS for r in [(MID-w/2,MID+w/2,z,z+h),(MID-w*.28,MID+w*.28,z-d,z)]]
W_ORIGIN=np.array([-132.146,-.776,0.]);W_T=np.array([-.945716344,-.324993227,0.]);W_N=np.array([.324993227,-.945716344,0.])
SLITS=[(12.,40.,28.775,29.225),(23.,40.,24.575,25.025)]
CAV=(0.,10.5,1.70,26.25)
PORTAL_C=np.array([-129.0380165156,6.9354800658,0.])
PORTAL_R=np.array([.050703,.998716,0.]);PORTAL_N=np.array([.998716,-.050703,0.])
PORTAL_RECT=(-2.65,2.65,1.17,4.20)
STAIR_BI=np.array([-125.50037,9.17703,0.]);STAIR_BO=np.array([-124.19737,11.94828,0.]);STAIR_TI=np.array([-133.61348,12.90997,0.])
STAIR_ALONG=STAIR_TI-STAIR_BI;STAIR_ACROSS=STAIR_BO-STAIR_BI
STAIR_INV=np.linalg.inv(np.column_stack((STAIR_ALONG[:2],STAIR_ACROSS[:2])))
STAIR_END=1.+.75/np.linalg.norm(STAIR_ALONG);STAIR_TOP=5.90;STAIR_CEILING=26.25
TOWER_BACK=1.+.85/np.linalg.norm(STAIR_ALONG)
def stairp(t,f,z):return STAIR_BI+t*STAIR_ALONG+f*STAIR_ACROSS+np.array([0,0,z])
def unit(v):
 v=np.asarray(v,dtype=float);return v/max(np.linalg.norm(v),1e-20)
def wp(u,z,d=0):return W_ORIGIN+u*W_T+d*W_N+np.array([0,0,z])
def cp(k,u,z,d=0):
 t=unit(A[k+1]-A[k]);p=np.r_[A[k]+t*(u-U[k]),z];r=unit(np.array([p[0]+134.75,p[1]-7.22,0.]));return p+r*d
class Mesh:
 def __init__(self,name,material,existing=None):
  self.d={'name':name,'vertices':[],'normals':[],'triangles':[],'material':material};self.lookup={}
  if existing is not None:self.d['existing_material']=existing
 def vertex(self,p,n):
  key=tuple(round(float(x),8) for x in list(p)+list(n))
  if key not in self.lookup:
   self.lookup[key]=len(self.d['vertices']);self.d['vertices'].append(list(map(float,p)));self.d['normals'].append(list(map(float,n)))
  return self.lookup[key]
 def poly(self,ps,ns=None,normal=None):
  ps=[np.array(p) for p in ps]
  if len(ps)<3:return
  n=unit(np.cross(ps[1]-ps[0],ps[2]-ps[0]))
  if normal is not None and np.dot(n,normal)<0:ps=[ps[0]]+list(reversed(ps[1:]));n=-n
  if ns is None:ns=[n]*len(ps)
  ids=[self.vertex(p,n) for p,n in zip(ps,ns)]
  for i in range(1,len(ids)-1):
   if np.linalg.norm(np.cross(ps[i]-ps[0],ps[i+1]-ps[0]))>1e-9:self.d['triangles'].append([ids[0],ids[i],ids[i+1]])
 def tube(self,a,b,r=.035,sides=8):
  a=np.asarray(a);b=np.asarray(b);t=unit(b-a)
  if np.linalg.norm(b-a)<1e-6:return
  x=unit(np.cross(t,[0,0,1] if abs(t[2])<.9 else [1,0,0]));y=np.cross(t,x);ids=[]
  for p in [a,b]:
   ids.append([self.vertex(p+r*(math.cos(i*2*math.pi/sides)*x+math.sin(i*2*math.pi/sides)*y),math.cos(i*2*math.pi/sides)*x+math.sin(i*2*math.pi/sides)*y) for i in range(sides)])
  for i in range(sides):
   j=(i+1)%sides;self.d['triangles'] += [[ids[0][i],ids[0][j],ids[1][j]],[ids[0][i],ids[1][j],ids[1][i]]]
  self.poly([a+r*(math.cos(i*2*math.pi/sides)*x+math.sin(i*2*math.pi/sides)*y) for i in range(sides)],normal=-t)
  self.poly([b+r*(math.cos(i*2*math.pi/sides)*x+math.sin(i*2*math.pi/sides)*y) for i in range(sides)],normal=t)
def planar_xy(mesh,points,normal):
 points=[np.asarray(x,dtype=float) for x in points];ids=list(range(len(points)))
 def cross2(a,b,c):return (b[0]-a[0])*(c[1]-a[1])-(b[1]-a[1])*(c[0]-a[0])
 area=sum(a[0]*b[1]-a[1]*b[0] for a,b in zip(points,points[1:]+points[:1]));sgn=1 if area>0 else -1
 while len(ids)>3:
  found=False
  for j in range(len(ids)):
   ia,ib,ic=ids[j-1],ids[j],ids[(j+1)%len(ids)];a,b,c=[points[k] for k in [ia,ib,ic]]
   if cross2(a,b,c)*sgn<=1e-10:continue
   if any(min(cross2(a,b,points[k])*sgn,cross2(b,c,points[k])*sgn,cross2(c,a,points[k])*sgn)>=-1e-10 for k in ids if k not in [ia,ib,ic]):continue
   mesh.poly([a,b,c],normal=normal);ids.pop(j);found=True;break
  if not found:raise ValueError('Cannot earclip shoulder polygon')
 mesh.poly([points[k] for k in ids],normal=normal)
def material(name,color,metal,rough):return {'name':name,'pbrMetallicRoughness':{'baseColorFactor':color+[1],'metallicFactor':metal,'roughnessFactor':rough}}
def half(poly,axis,val,greater):
 out=[]
 for a,b in zip(poly,poly[1:]+poly[:1]):
  da=(a[axis]-val)*(1 if greater else -1);db=(b[axis]-val)*(1 if greater else -1);ia=da>=-1e-9;ib=db>=-1e-9
  if ia:out.append(a)
  if ia!=ib:out.append(a+(b-a)*(da/(da-db)))
 return out
def subtract(poly,r):
 """Return convex pieces outside a rectangle, and whether positive area was cut."""
 inside=poly;outside=[]
 for axis,val,g in [(0,r[0],True),(0,r[1],False),(1,r[2],True),(1,r[3],False)]:
  if not inside:break
  p=half(inside,axis,val,not g)
  if len(p)>2:outside.append(p)
  inside=half(inside,axis,val,g)
 area=0 if len(inside)<3 else abs(sum(a[0]*b[1]-a[1]*b[0] for a,b in zip(inside,inside[1:]+inside[:1])))/2
 return (outside,True) if area>1e-9 else ([poly],False)
def subtract_volume(poly,planes):
 inside=poly;outside=[]
 for axis,val,g in planes:
  if not inside:break
  pp=half(inside,axis,val,not g)
  if len(pp)>2:outside.append(pp)
  inside=half(inside,axis,val,g)
 area=0 if len(inside)<3 else sum(np.linalg.norm(np.cross(inside[i][2:5]-inside[0][2:5],inside[i+1][2:5]-inside[0][2:5])) for i in range(1,len(inside)-1))
 return (outside,True) if area>1e-9 else ([poly],False)
def build():
 raw=(ROOT/'inputs/prior.glb').read_bytes();assert hashlib.sha256(raw).hexdigest()==PIN
 jl=struct.unpack_from('<I',raw,12)[0];J=json.loads(raw[20:20+jl]);B=raw[28+jl:]
 def acc(i):
  a=J['accessors'][i];v=J['bufferViews'][a['bufferView']];nc={'SCALAR':1,'VEC2':2,'VEC3':3,'VEC4':4}[a['type']];fmt={5126:'f',5123:'H',5125:'I',5121:'B'}[a['componentType']];st=v.get('byteStride',struct.calcsize(fmt)*nc);off=v.get('byteOffset',0)+a.get('byteOffset',0)
  return np.array([struct.unpack_from('<'+fmt*nc,B,off+k*st) for k in range(a['count'])])
 source=json.loads((ROOT/'inputs/source-triangle-map.json').read_text())['source_faces'];removed={};g={};replacement={};records=[]
 lowerfit=json.loads((ROOT/'inputs/lower72-fit.json').read_text());lowerrects=lowerfit['shell_aperture_rects_uz'];lowercandidates={(x['mesh_index'],x['triangle']) for x in json.loads((ROOT/'inputs/lower72-triangles.json').read_text())['triangles']}
 assert lowerfit['input_sha256']==PIN
 def rm(mi,ti):removed.setdefault(mi,set()).add(ti)
 def repl(mi):
  if mi not in replacement:
   mat=J['meshes'][mi]['primitives'][0]['material'];replacement[mi]=Mesh('phase2_retained_fragments_'+str(mi),J['materials'][mat],mat)
   replacement[mi].d['existing_mesh']=mi
  return replacement[mi]
 # Source map gives candidates only. Each candidate is checked for plane/spatial ownership below.
 owners={}
 for si in [72,86,123,44,39,132,37,109,95]:
  for name,ids in source[str(si)].items():
   mi=next(i for i,m in enumerate(J['meshes']) if m['name']==name)
   for ti in ids:owners[(mi,ti)]=si
 for mi,m in enumerate(J['meshes']):
  if mi not in list(range(1,9))+[10,11,13,14,15,16]:continue
  p=m['primitives'][0];vs=acc(p['attributes']['POSITION'])[:,[0,2,1]];vs[:,1]*=-1
  ns=acc(p['attributes']['NORMAL'])[:,[0,2,1]];ns[:,1]*=-1;tris=acc(p['indices']).flatten().reshape(-1,3)
  for ti,ids in enumerate(tris):
   pts=vs[ids];norm=ns[ids];si=owners.get((mi,ti));rects=[];uv=None
   if (mi,ti) in lowercandidates:si=72
   if mi==11:
    if ti<26:rm(mi,ti)
    continue
   if mi==10:
    if pts[:,2].min()>8 and pts[:,2].max()<20:rm(mi,ti)
    continue
   if si in [123,44,39,132] or mi==8:
    # Arc facet classification; original source positions vary by <=1mm with height.
    for k in range(1,5):
     t=unit(np.r_[A[k+1]-A[k],0]);n=np.array([t[1],-t[0],0]);o=np.r_[A[k],0]
     ds=(pts-o)@n;us=(pts-o)@t+U[k]
     if max(abs(ds))<.15 and max(ds)-min(ds)<.006 and min(us)>U[k]-.04 and max(us)<U[k+1]+.04:
      uv=np.c_[us,pts[:,2]];rects=SLOT_RECTS;break
   elif si in [72,86] or mi in [13,14,15,16]:
    # Legacy corner bevel crosses both planes and belongs to the cavity if below soffit.
    us=(pts-W_ORIGIN)@W_T;ds=(pts-W_ORIGIN)@W_N
    if si==72 or (max(ds)-min(ds)<.015 and -.02<=min(ds) and max(ds)<.30):
     uv=np.c_[us,pts[:,2]];rects=[CAV]+SLITS
     if si==72 and mi==1:rects+=lowerrects
     if (mi,ti) in lowercandidates:rects+=[(0.,42.30549706598424,1.30,7.65)]
     if si==72 and 2<=mi<=7 and min(ds)>.01 and max(ds)<.30 and max(ds)-min(ds)<.02 and min(us)>-.001 and max(us)<42.306:
      rects+=[(10.5,42.30549706598424,7.65,26.25)]
     if mi>=13:rects=[(0,10.5,1.45,26.25)]+SLITS
    elif si==86 or (min(us)>-.45 and max(us)<.30):
     # Return86 recedes from72 to cylinder: full lower return opened, bounded at original edge.
     uv=np.c_[ds,pts[:,2]];rects=[(-2.95,.35,1.70 if mi<13 else 1.45,26.25)]
   is_stair=si in [37,109,95]
   if is_stair:
    tf=(STAIR_INV@(pts[:,:2]-STAIR_BI[:2]).T).T;uv=np.c_[tf[:,0],pts[:,2]];rects=[]
   if uv is None or (not rects and not is_stair):continue
   # Snap only projected classification coordinates at float32 boundary noise.
   # Original XYZ/normals are untouched; this avoids micrometre exterior slivers.
   for r in rects:
    for axis,vals in [(0,r[:2]),(1,r[2:])]:
     for value in vals:uv[np.abs(uv[:,axis]-value)<1e-5,axis]=value
   poly=[np.r_[uv[i],pts[i],norm[i],tf[i,1]] if is_stair else np.r_[uv[i],pts[i],norm[i]] for i in range(3)];pieces=[poly];changed=False
   if is_stair:
    step_bounds=[(i/29,(i+1)/29,1.38+(5.90-1.38)*(i+1)/29) for i in range(29)]+[(1.,TOWER_BACK,5.90)]
    for ta,tb,floor in step_bounds:
     new=[]
     for piece in pieces:
      out,cut=subtract_volume(piece,[(0,ta,True),(0,tb,False),(8,0.,True),(8,1.,False),(1,floor,True),(1,STAIR_CEILING,False)]);new+=out;changed|=cut
     pieces=new
   for r in rects:
    new=[]
    for piece in pieces:
     out,cut=subtract(piece,r);new+=out;changed|=cut
    pieces=new
   # Entrance and slots share the same original shell triangles: subtract both
   # before emitting a single set of retained fragments. Tangent planes are
   # evaluated from original/interpolated XYZ, never approximated by arc width.
   if si in [123,44,39,132]:
    new=[]
    for piece in pieces:
     portal_piece=[]
     for vertex in piece:
      vertex=vertex.copy();vertex[0]=np.dot(vertex[2:5]-PORTAL_C,PORTAL_R)
      for axis,values in [(0,PORTAL_RECT[:2]),(1,PORTAL_RECT[2:])]:
       for value in values:
        if abs(vertex[axis]-value)<1e-5:vertex[axis]=value
      portal_piece.append(vertex)
     out,cut=subtract(portal_piece,PORTAL_RECT);new+=out;changed|=cut
    pieces=new
   if is_stair:
    # Named37/109/95 architectural correction: replace the false low overhang
    # with actual tall louver/glass hierarchy, preserving shoulder26.25..33.2.
    new=[]
    for piece in pieces:
     out,cut=subtract_volume(piece,[(1,5.90 if si in [37,109] else 7.0,True),(1,26.25,False)]);new+=out;changed|=cut
    pieces=new
   if changed:
    rm(mi,ti)
    for piece in pieces:repl(mi).poly([v[2:5] for v in piece],[unit(v[5:8]) for v in piece])
 # Three architectural material groups, plus retained material fragments merged into their original meshes.
 metal=Mesh('phase2_aperture_metal',material('phase2_aluminum',[.48,.50,.51],.72,.35))
 dark=Mesh('phase2_recess_backing',material('phase2_dark_glass',[.025,.045,.057],.30,.28))
 frame=Mesh('phase2_spatial_frame',material('phase2_structural_tubes',[.29,.32,.33],.72,.40))
 # Six true bounded stepped pockets; source-faceted coordinates do not alter tower silhouette.
 for z,w,h,drop in SLOTS:
  outline=[(MID-w/2,z),(MID-w*.28,z),(MID-w*.28,z-drop),(MID+w*.28,z-drop),(MID+w*.28,z),(MID+w/2,z),(MID+w/2,z+h),(MID-w/2,z+h)]
  for a,b in zip(outline,outline[1:]+outline[:1]):
   # Split boundary segments at every source-facet seam for exact original alignment.
   ts=[0.,1.]
   if abs(b[0]-a[0])>1e-9:ts+= [(u-a[0])/(b[0]-a[0]) for u in U if 0<(u-a[0])/(b[0]-a[0])<1]
   for t0,t1 in zip(sorted(ts),sorted(ts)[1:]):
    aa=np.array(a)+(np.array(b)-a)*t0;bb=np.array(a)+(np.array(b)-a)*t1;k=min(5,max(0,int(np.searchsorted(U,(aa[0]+bb[0])/2)-1)))
    metal.poly([cp(k,*aa,0),cp(k,*bb,0),cp(k,*bb,-.42),cp(k,*aa,-.42)])
    metal.tube(cp(k,*aa,.018),cp(k,*bb,.018),.020)
  for r in [(MID-w/2,MID+w/2,z,z+h),(MID-w*.28,MID+w*.28,z-drop,z)]:
   for k in range(6):
    lo=max(r[0],U[k]);hi=min(r[1],U[k+1])
    if hi<=lo:continue
    dark.poly([cp(k,lo,r[2],-.42),cp(k,hi,r[2],-.42),cp(k,hi,r[3],-.42),cp(k,lo,r[3],-.42)],normal=cp(k,(lo+hi)/2,0,.1)-cp(k,(lo+hi)/2,0))
  # Fine internal low rail and vertical jamb detail, set behind the outer shell.
  for k in range(6):
   lo=max(MID-w*.28+.07,U[k]);hi=min(MID+w*.28-.07,U[k+1])
   if hi>lo:frame.tube(cp(k,lo,z-drop+.12,-.18),cp(k,hi,z-drop+.12,-.18),.018)
 # Cavity ends at d=-2.60, just shy of the source86 depth anchor (2.628m).
 dep=-2.60;u0=0.;u1=10.5;z0=1.70;z1=26.25
 dark.poly([wp(u0,z0,dep),wp(u1,z0,dep),wp(u1,z1,dep),wp(u0,z1,dep)],normal=W_N)
 metal.poly([wp(u1,z0,0),wp(u1,z1,0),wp(u1,z1,dep),wp(u1,z0,dep)],normal=-W_T)
 metal.poly([wp(u0,z0,0),wp(u0,z0,dep),wp(u0,z1,dep),wp(u0,z1,0)],normal=W_T)
 metal.poly([wp(u0,z1,0),wp(u1,z1,0),wp(u1,z1,dep),wp(u0,z1,dep)],normal=[0,0,-1])
 metal.poly([wp(u0,z0,0),wp(u0,z0,dep),wp(u1,z0,dep),wp(u1,z0,0)],normal=[0,0,1])
 # Near-cylinder junction uses actual86 edge, rather than an independent glass panel.
 c=np.array([-132.868,1.755,0.]);edge_u=float((c-W_ORIGIN)@W_T)
 metal.poly([wp(0,z0,dep),np.array([c[0],c[1],z0]),np.array([c[0],c[1],z1]),wp(0,z1,dep)],normal=W_T)
 # Curtainwall approximately square 8 x 19 bays; no opaque exterior remains in aperture.
 us=np.linspace(0,10.5,9);zs=np.linspace(z0,z1,20)
 for u in us:metal.tube(wp(u,z0,dep+.035),wp(u,z1,dep+.035),.032)
 for z in zs:metal.tube(wp(0,z,dep+.035),wp(10.5,z,dep+.035),.032)
 # Overhead two-depth-bay spatial lattice, behind outside line, with alternating single diagonals.
 ds=[-.16,-1.30,-2.44];zz=25.78
 for d in ds:
  frame.tube(wp(.12,zz,d),wp(10.38,zz,d))
 for u in us:
  u=max(.12,min(10.38,u));frame.tube(wp(u,zz,ds[0]),wp(u,zz,ds[-1]))
 for i in range(8):
  for j in range(2):
   lo=max(.12,us[i]);hi=min(10.38,us[i+1]);aa=(lo,ds[j]);bb=(hi,ds[j+1])
   if (i+j)%2:aa=(hi,ds[j]);bb=(lo,ds[j+1])
   frame.tube(wp(aa[0],zz,aa[1]),wp(bb[0],zz,bb[1]),.029)
 # Slim hanging support lattice: only cylinder-side three bays, not a full glazed-field cage.
 front=-.24;fzs=np.linspace(4.3,20.1,13);fus=[.18,1.48,2.78,4.08]
 for u in fus:frame.tube(wp(u,fzs[0],front),wp(u,zz,front),.035)
 for z in fzs:
  frame.tube(wp(fus[0],z,front),wp(fus[-1],z,front),.032)
  for u in [fus[0],fus[-1]]:frame.tube(wp(u,z,front),wp(u,z,dep+.10),.029)
 for i in range(3):
  for j in range(len(fzs)-1):
   a,b=(fus[i],fus[i+1]) if (i+j)%2 else (fus[i+1],fus[i]);frame.tube(wp(a,fzs[j],front),wp(b,fzs[j+1],front),.027)
 # Slits have actual shell cuts, closed 0.32m reveals and dark backs.
 for lo,hi,bot,top in SLITS:
  dark.poly([wp(lo,bot,-.32),wp(hi,bot,-.32),wp(hi,top,-.32),wp(lo,top,-.32)],normal=W_N)
  for a,b in [((lo,bot),(hi,bot)),((hi,bot),(hi,top)),((hi,top),(lo,top)),((lo,top),(lo,bot))]:
   metal.poly([wp(*a,.26),wp(*b,.26),wp(*b,-.32),wp(*a,-.32)])
 # Localized lower72 apertures replace the false generic continuous blue strips.
 lower_metal=Mesh('phase2_lower72_aluminum',J['materials'][19],19)
 lower_frame=Mesh('phase2_lower72_joints',J['materials'][11],11)
 # Panel rhythm is unchanged1.35m. Only the evidenced lower field is surfaced.
 for ua in np.arange(10.5,42.30549706598424,1.35):
  ub=min(ua+1.35,42.30549706598424)
  for za in np.arange(1.30,7.65,1.35):
   zb=min(za+1.35,7.65);pieces=[list(map(np.array,[(ua+.012,za+.012),(ub-.012,za+.012),(ub-.012,zb-.012),(ua+.012,zb-.012)]))]
   for r in lowerrects:
    new=[]
    for pp in pieces:out,cut=subtract(pp,r);new+=out
    pieces=new
   for pp in pieces:lower_metal.poly([wp(u,z,.025) for u,z in pp],normal=W_N)
 # Thin dark joint backing stays restricted to lower solid pieces, not openings.
 for axis,vals in [(0,np.arange(10.5,42.3055,1.35)),(1,np.arange(1.30,7.65,1.35))]:
  for value in vals:
   r=(max(10.5,value-.012),min(42.30549706598424,value+.012),1.30,7.65) if axis==0 else (10.5,42.30549706598424,max(1.30,value-.012),min(7.65,value+.012))
   pieces=[list(map(np.array,[(r[0],r[2]),(r[1],r[2]),(r[1],r[3]),(r[0],r[3])]))]
   for hole in lowerrects:
    new=[]
    for pp in pieces:out,cut=subtract(pp,hole);new+=out
    pieces=new
   for pp in pieces:lower_frame.poly([wp(u,z,.027) for u,z in pp],normal=W_N)
 # Source72 middlewall only: fine1.35m squarejoints replace inherited coarse
 # horizontalbands. Existing aluminum shell/material remains unchanged.
 midrects=[]
 for u in np.arange(10.5,42.30549706598424,1.35):midrects.append((max(10.5,u-.012),min(42.30549706598424,u+.012),7.65,26.25))
 for z in np.arange(1.30,26.25,1.35):
  if z>=7.65:midrects.append((10.5,42.30549706598424,z-.012,min(26.25,z+.012)))
 for r in midrects:
  pieces=[list(map(np.array,[(r[0],r[2]),(r[1],r[2]),(r[1],r[3]),(r[0],r[3])]))]
  for hole in SLITS:
   new=[]
   for pp in pieces:out,cut=subtract(pp,hole);new+=out
   pieces=new
  for pp in pieces:lower_frame.poly([wp(u,z,.027) for u,z in pp],normal=W_N)
 for idx,(lo,hi,bot,top) in enumerate(lowerrects):
  dark.poly([wp(lo,bot,-.22),wp(hi,bot,-.22),wp(hi,top,-.22),wp(lo,top,-.22)],normal=W_N)
  for a,b in [((lo,bot),(hi,bot)),((hi,bot),(hi,top)),((hi,top),(lo,top)),((lo,top),(lo,bot))]:
   metal.poly([wp(*a,.025),wp(*b,.025),wp(*b,-.22),wp(*a,-.22)])
  count=3 if idx==0 else (2 if hi-lo>7 else 1)
  for u in np.linspace(lo,hi,count+1)[1:-1]:frame.tube(wp(u,bot,-.17),wp(u,top,-.17),.035)
 # Conservative separate side109portal. Entry bottom clamped to existing cavity
 # sill1.70 rather than cutting the protected source base. No lettering/interior.
 lo,hi,bot,top=lowerfit['side_portal']['header_uz']
 lower_metal.poly([wp(lo,bot,.25),wp(hi,bot,.25),wp(hi,top,.25),wp(lo,top,.25)],normal=W_N)
 for a,b in [((lo,bot),(hi,bot)),((hi,bot),(hi,top)),((hi,top),(lo,top)),((lo,top),(lo,bot))]:
  metal.poly([wp(*a,.25),wp(*b,.25),wp(*b,-.25),wp(*a,-.25)])
 lo,hi,bot,top=lowerfit['side_portal']['dark_entry_uz'];bot=max(bot,1.70)
 dark.poly([wp(lo,bot,-.25),wp(hi,bot,-.25),wp(hi,top,-.25),wp(lo,top,-.25)],normal=W_N)
 for u in [lo,hi]:metal.poly([wp(u,bot,.25),wp(u,top,.25),wp(u,top,-.25),wp(u,bot,-.25)],normal=W_T if u==lo else -W_T)
 # Right tall hierarchy: landed backset front, narrow louver, glazedcorner,
 # source95 side return, and real shoulder underside. No low artificialsoffit.
 ring95=json.loads((ROOT/'inputs/plateau.json').read_text())['surfaces'][95]['ring']
 p95=np.array(ring95[0][:2]);q95=np.array(ring95[3][:2]);a95=STAIR_INV@(p95-STAIR_BI[:2]);b95=STAIR_INV@(q95-STAIR_BI[:2]);fback=float(a95[1]+(b95[1]-a95[1])*(TOWER_BACK-a95[0])/(b95[0]-a95[0]))
 frontnormal=-unit(STAIR_ALONG);front0=stairp(TOWER_BACK,0,0);front1=stairp(TOWER_BACK,fback,0);split=front0+(front1-front0)*.295;sideend=np.r_[p95,0.];junction=np.array([-130.902,11.533,0.])
 def quadvert(mesh,a,b,z0,z1,n,offset=0):
  mesh.poly([a+np.array([0,0,z0])+n*offset,b+np.array([0,0,z0])+n*offset,b+np.array([0,0,z1])+n*offset,a+np.array([0,0,z1])+n*offset],normal=n)
 # Back plinth stops at glass7.0; no speculative door. Louver starts atlanding5.9.
 quadvert(dark,front0,front1,5.90,7.0,frontnormal)
 quadvert(dark,front0,split,7.0,26.25,frontnormal)
 quadvert(dark,split,front1,7.0,26.25,frontnormal)
 side_t=unit(sideend-front1);side_n=np.array([side_t[1],-side_t[0],0.]);
 if np.dot(side_n,np.array([.43,.9,0]))<0:side_n=-side_n
 quadvert(dark,front1,sideend,7.0,26.25,side_n)
 # Muted solidinner return terminates at preserved cylinder attachment.
 inner_t=unit(front0-junction);inner_n=np.array([inner_t[1],-inner_t[0],0.]);
 if np.dot(inner_n,STAIR_ACROSS)<0:inner_n=-inner_n
 # Full inner sidewall would block the evidenced leftturn; close only the
 # narrow louver end atP, beyondlanding, not the route along its inneredge.
 quadvert(metal,front0,front0+frontnormal*.09,5.90,26.25,-unit(STAIR_ACROSS))
 # Approved fitted NEW lower cylinder-side return. Originalupperfacet vertices
 # remain untouched. Only the intermediate newvertex is inset.20m to clear
 # the registered innerrail; A/Danchors remain exact analyticreferences.
 cylB=np.array([-132.996,12.735,0.]);cylC=np.array([-135.399,12.984,0.]);cylD=cylB+(cylC-cylB)*np.dot(front0-cylB,cylC-cylB)/np.dot(cylC-cylB,cylC-cylB)
 fitB=cylB-.20*unit(STAIR_ACROSS);returnchain=[junction,fitB,cylD,front0]
 for aa,bb in zip(returnchain,returnchain[1:]):
  direction=unit(bb-aa);nn=np.array([direction[1],-direction[0],0.])
  if np.dot(nn,STAIR_ACROSS)<0:nn=-nn
  quadvert(lower_metal,aa,bb,1.17,26.25,nn)
 # Actual projected shoulderunderside only at26.25, bounded by unchangedfrontedge.
 soffitxy=[np.array([-130.615,12.372,0.]),np.array([-129.519,14.188,0.]),front1,front0,cylD,fitB,junction]
 planar_xy(metal,[x+np.array([0,0,26.25]) for x in soffitxy],[0,0,-1])
 # Indexed raisedstrip curtainwall divisions, no expensivecappedtubes.
 for a,b,n,cols in [(split,front1,frontnormal,2),(front1,sideend,side_n,2)]:
  tangent=unit(b-a);length=np.linalg.norm(b-a)
  for u in np.linspace(0,length,cols+1):
   lo=max(0,u-.025);hi=min(length,u+.025)
   quadvert(frame,a+tangent*lo,a+tangent*hi,7.0,26.25,n,.035)
  for z in np.linspace(7.0,26.25,16):
   quadvert(frame,a,b,max(7.,z-.025),min(26.25,z+.025),n,.035)
 # New-only material fit: darkmetal louver blades; geometry unchanged.
 louver=Mesh('phase2_right_tower_dark_louvers',material('phase2_dark_louver_metal',[.035,.04,.045],.55,.5))
 # Narrow separator with horizontal angled blades.2faces/4tri perblade.
 for z in np.arange(5.98,26.20,.18):
  a=front0+np.array([0,0,z]);b=split+np.array([0,0,z]);
  louver.poly([a+frontnormal*.025,b+frontnormal*.025,b+frontnormal*.09+np.array([0,0,-.045]),a+frontnormal*.09+np.array([0,0,-.045])],normal=frontnormal)
  louver.poly([a+frontnormal*.09+np.array([0,0,-.045]),b+frontnormal*.09+np.array([0,0,-.045]),b+frontnormal*.025+np.array([0,0,-.09]),a+frontnormal*.025+np.array([0,0,-.09])],normal=frontnormal)
 additions=[x.d for x in replacement.values() if x.d['triangles']]+[metal.d,dark.d,frame.d,lower_metal.d,lower_frame.d,louver.d]
 manifest={'input_sha256':PIN,'six_slot_bases':[s[0] for s in SLOTS],'slot_depth_m':.42,'entrance_aperture':{'center_xy':PORTAL_C[:2].tolist(),'tangent_xy':PORTAL_R[:2].tolist(),'tangent_bounds_m':[-2.65,2.65],'z_bounds_m':[1.17,4.20],'source_ownership':[123,44,39,132],'method':'Slot and tangent entrance subtraction in one pass per original triangle. XYZ-derived tangent boundary, not arc-width approximation.'},'lower72':{'opening_rects_uz':lowerrects,'generic_overlay_candidate_count':len(lowercandidates),'removal_bounds_uz':[0,42.30549706598424,1.30,7.65],'reveal_depth_m':.22,'panel_pitch_m':1.35,'side_portal_entry_bottom_clamped_z':1.70,'middle72_cleanup':{'bounds_uz':[10.5,42.30549706598424,7.65,26.25],'candidate_validation':'Originalsource72 ownership plus allvertex d.01..30m,planespread<.02m,uwithinfacebounds; clipoutsidefragments retained','joint_pitch_m':1.35,'shell_color_unchanged':True,'slits_preserved':True},'materials':'Reuse existing19 aluminum/existing11 joint and phase2 darkglass/metal/frame. No new material families.','qualification':'All metric seeds estimated;2025 merchant existence supported but precise lower elevation uses auxiliary stable architectural imagery; no tenant lettering or interiors'},'stair_accommodation':{'sources':[37,109,95],'steps':29,'bottom_z':1.38,'top_z':5.90,'landing_extension_m':.75,'t_end':float(STAIR_END),'shoulder_underside_z':26.25,'physical_soffit':True,'back_plinth_top_z':7.0,'tower_back_t':float(TOWER_BACK),'tower_back_inner_xy':front0[:2].tolist(),'tower_back_outer_xy':front1[:2].tolist(),'fitted_cylinder_return':{'anchors_xyz':[junction.tolist(),cylD.tolist(),front0.tolist()],'original_upper_reference_B':cylB.tolist(),'new_intermediate_B':fitB.tolist(),'inset_m':.20,'qualification':'Newlowerreturnfit only; originaluppercylindervertices untouched. Inferrednot surveyed.'},'tower_glass_front_width_m':float(np.linalg.norm(front1-split)),'tower_louver_width_m':float(np.linalg.norm(split-front0)),'tower_sideglass_width_m':float(np.linalg.norm(sideend-front1)),'left_turn':'inner landing edge intentionally open; no arbitrary cylinder excavation','qualification':'29risers/top5.9±0.5, setback0.85m and shoulder underside26.25 are photo-informed fitting assumptions, not measured. Earlier7.9falseoverhang superseded by named37/109/95 hierarchy; upper26.25..33.2band/source102 preserved.'},'wing_cavity_uvz':CAV,'wing_depth_m':2.60,'source86_depth_anchor_m':2.628253,'slits_uvz':SLITS,'new_material_primitives':4,'louver_material_fit':{'rgb':[.035,.04,.045],'metallic':.55,'roughness':.5,'scope':'Only new righttower louverblades, geometry/normals unchanged; visualfit,notmeasured'},'retained_fragment_merge_required':True,'reference_urls':['https://docomomojapan.com/structure/285/?lang=ja'],'qualification':'All fitting dimensions are architectural estimates, not measured construction data. No ads or inferred interiors. Roof, cap and upper logo excluded.'}
 return {'remove':{k:sorted(v) for k,v in removed.items()},'additions':additions,'manifest':manifest,'report':manifest}
if __name__=='__main__':
 result=build();out=ROOT/'output/phase2-contract.json';out.write_text(json.dumps(result,separators=(',',':')));print('written',out,'removed',{k:len(v) for k,v in result['remove'].items()},'added',[(a['name'],len(a['triangles'])) for a in result['additions']])
