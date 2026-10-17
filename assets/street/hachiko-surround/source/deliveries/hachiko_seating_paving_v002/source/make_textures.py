#!/usr/bin/env python3
"""Deterministic authored PBR textures. No photographic pixels are used."""
from pathlib import Path
import numpy as np
from PIL import Image, ImageDraw, ImageFilter
ROOT=Path(__file__).resolve().parents[1]; OUT=ROOT/'textures'; OUT.mkdir(exist_ok=True)
rng=np.random.default_rng(1973402)
def save(a,n): Image.fromarray(np.uint8(np.clip(a,0,255))).save(OUT/n)
def smooth_noise(n,s):
 a=Image.fromarray(np.uint8(rng.random((s,s))*255)).resize((n,n),Image.Resampling.BICUBIC)
 return np.asarray(a,dtype=float)/255
n=1024
fine=rng.normal(0,1,(n,n));mid=smooth_noise(n,180);broad=smooth_noise(n,26)
# Cool neutral salt-and-pepper granite, not a painted uniform flat gray.
value=77+fine*5+(mid-.5)*25+(broad-.5)*10
quartz=rng.random((n,n));value+=np.where(quartz>.94,35,0);value-=np.where(quartz<.065,28,0)
stone=np.stack([value*.975,value*1.005,value*1.035],-1)
save(stone,'granite_basecolor.png');save(188+(mid-.5)*32+(broad-.5)*15,'granite_roughness.png')
height=(mid-.5)*.0003+fine*.000025;dy,dx=np.gradient(height,.65/n,.65/n)
normal=np.stack([-dx,-dy,np.ones_like(dx)],-1);normal/=np.linalg.norm(normal,axis=-1,keepdims=True)
save((normal*.5+.5)*255,'granite_normal.png')
# Authored linear brushed steel roughness: non-photographic microvariation only.
stripe=rng.normal(0,1,(n,1));steel=79+stripe*8+rng.normal(0,1,(n,n))*2
save(steel,'steel_roughness.png')
# Full-footprint, nonrepeating paving layout candidate. Center/radius/bands are inferred.
w,h=3072,2068; xmin,ymin,xmax,ymax=-5.2,-4,5.2,3
scale=w/(xmax-xmin)
im=Image.new('RGB',(w,h),(59,61,60));d=ImageDraw.Draw(im);heightim=Image.new('L',(w,h),55);hd=ImageDraw.Draw(heightim)
def pt(x,y): return ((x-xmin)*scale,(ymax-y)*scale)
def poly(points,c):
 p=[pt(*v) for v in points];d.polygon(p,fill=c);hd.polygon(p,fill=182)
def stonecolor():
 v=int(rng.uniform(98,123));return (v-1,v+1,v+3)
# Outside the circular court: laid rectangular setts. Broad radial bands interrupt them.
pitch=.11;j=.004
for iy in range(int((ymax-ymin)/pitch)+1):
 y=ymin+iy*pitch
 for ix in range(int((xmax-xmin)/pitch)+1):
  x=xmin+ix*pitch+(iy%2)*pitch/2
  poly([(x+j/2,y+j/2),(x+pitch-j/2,y+j/2),(x+pitch-j/2,y+pitch-j/2),(x+j/2,y+pitch-j/2)],stonecolor())
# Four foreground divider strips are supported in the undated reference but exact angle/width inferred.
R=3.48
for ang in [30,65,90,115,150]:
 a=np.radians(ang); ux,uy=np.cos(a),np.sin(a);px,py=-uy,ux;wide=.045
 # Front is +Y in the existing local frame.
 poly([(ux*R+px*wide,uy*R+py*wide),(ux*7+px*wide,uy*7+py*wide),(ux*7-px*wide,uy*7-py*wide),(ux*R-px*wide,uy*R-py*wide)],(77,81,82))
# Repaint one single circular composition, not repeated fan tiles.
for row in range(33):
 r0=row*.103;r1=r0+.099;rm=(r0+r1)/2
 if row==0:
  points=[(r1*np.cos(a),r1*np.sin(a)) for a in np.linspace(0,2*np.pi,24,endpoint=False)];poly(points,stonecolor());continue
 count=max(8,round(2*np.pi*rm/.108));offset=(row%2)*np.pi/count
 for k in range(count):
  a0=offset+2*np.pi*k/count+.004/(2*rm);a1=offset+2*np.pi*(k+1)/count-.004/(2*rm)
  aa=np.linspace(a0,a1,4)
  points=[(r1*np.cos(a),r1*np.sin(a)) for a in aa]+[(r0*np.cos(a),r0*np.sin(a)) for a in aa[::-1]]
  poly(points,stonecolor())
# Three continuous border rows distinguish the outer court edge.
for row in range(3):
 r0=3.40+row*.055;r1=r0+.05;count=round(2*np.pi*((r0+r1)/2)/.13)
 for k in range(count):
  a0=2*np.pi*k/count+.0008;a1=2*np.pi*(k+1)/count-.0008;aa=np.linspace(a0,a1,3)
  poly([(r1*np.cos(a),r1*np.sin(a)) for a in aa]+[(r0*np.cos(a),r0*np.sin(a)) for a in aa[::-1]],(78+row*3,82+row*3,84+row*3))
arr=np.asarray(im,dtype=float);grain=rng.normal(0,2.0,(h,w));arr+=grain[:,:,None];save(arr,'paving_ring_candidate_basecolor.png')
he=np.asarray(heightim.filter(ImageFilter.GaussianBlur(.65)),dtype=float)/255*.0015
ny,nx=np.gradient(he,1/scale,1/scale);normal=np.stack([-nx,ny,np.ones_like(nx)],-1);normal/=np.linalg.norm(normal,axis=-1,keepdims=True)
save((normal*.5+.5)*255,'paving_ring_candidate_normal.png');save(208+grain,'paving_ring_candidate_roughness.png')
print('Authored textures written:',OUT)
