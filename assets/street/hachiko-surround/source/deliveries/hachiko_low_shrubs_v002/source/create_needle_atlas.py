from PIL import Image,ImageDraw
from pathlib import Path
import random,math
R=Path(__file__).resolve().parents[1]
S=1024; im=Image.new('RGBA',(S,S),(72,100,42,0));d=ImageDraw.Draw(im)
# Four wholly procedural sprays. No photograph pixels or external textures used.
for v in range(4):
 rng=random.Random(6623+v);x0=(v%2)*512;y0=(v//2)*512
 for k in range(23):
  root=(256+rng.uniform(-22,22),470+rng.uniform(-15,10));ang=(-.79+k*.0718)+rng.uniform(-.07,.07)
  length=rng.uniform(300,410);width=rng.uniform(11,17)
  bend=rng.uniform(-45,45);drop=rng.uniform(8,48)
  pts=[];right=[]
  for i in range(25):
   u=i/24;xx=root[0]+math.sin(ang)*length*.72*u+bend*.55*u*u;yy=root[1]-math.cos(ang)*length*u+drop*u*u
   dx=math.sin(ang)*length*.72+2*bend*.55*u;dy=-math.cos(ang)*length+2*drop*u;n=math.hypot(dx,dy);nx=-dy/n;ny=dx/n
   w=width*(.38+.62*math.sin(math.pi*min(u/.85,1)))*max(.025,(1-u)**.33)
   pts.append((x0+xx+nx*w/2,y0+yy+ny*w/2));right.append((x0+xx-nx*w/2,y0+yy-ny*w/2))
  shade=rng.choice([(62,91,36),(74,105,42),(83,111,46),(96,122,51),(55,83,31)])
  d.polygon(pts+right[::-1],fill=(*shade,255))
  # restrained central highlight gives thin folded needles depth without a ball core
  center=[((a[0]+b[0])/2,(a[1]+b[1])/2) for a,b in zip(pts,right)]
  d.line(center,fill=(min(255,shade[0]+12),min(255,shade[1]+13),shade[2]+6,255),width=2)
im.save(R/'textures/needle_spray_atlas.png')
print('Self-generated four-spray atlas written')
