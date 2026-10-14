from PIL import Image,ImageDraw,ImageFont
from pathlib import Path
import json
p=Path(__file__).resolve().parent; f='/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf'
head=ImageFont.truetype(f,34);body=ImageFont.truetype(f,23);small=ImageFont.truetype(f,20);label=ImageFont.truetype(f,24)
labels={'west-block':'West block | JAN 2025','daiichi-kangin':'Daiichi-Kangin / UC | JAN 2025','ekimae':'Ekimae | NOV 2025','center244':'Center244 | JAN 2025'}
positions={'assembly-southeast':{'west-block':(1260,770),'daiichi-kangin':(540,160),'ekimae':(70,485),'center244':(1330,240)},'assembly-plan':{'west-block':(1250,510),'daiichi-kangin':(60,520),'ekimae':(1200,1110),'center244':(1050,190)}}
coords=json.loads((p/'label-projections.json').read_text())
# Use visibly occupied facade/roof pixels for the oblique callout endpoints.
coords['assembly-southeast'].update({'west-block':[1230,870],'daiichi-kangin':[850,300],'ekimae':[550,750]})
for view,title in [('assembly-southeast','Southeast view'),('assembly-plan','Plan view | +Y up / +X right')]:
 im=Image.open(p/(view+'.png')).convert('RGB');w,h=im.size;board=Image.new('RGB',(w,h+215),'#f4f3ef');board.paste(im,(0,95));d=ImageDraw.Draw(board)
 d.text((32,20),'FOUR-BUILDING ASSET REVIEW  /  '+title,font=head,fill='#20252b')
 for bid,text in labels.items():
  x,y=positions[view][bid];y+=95;tx,ty=coords[view][bid];ty+=95
  bb=d.textbbox((x,y),text,font=label);bb=(bb[0]-10,bb[1]-7,bb[2]+10,bb[3]+7)
  edge=(max(bb[0],min(tx,bb[2])),max(bb[1],min(ty,bb[3])))
  d.line((edge,(tx,ty)),fill='#374958',width=2);d.ellipse((tx-4,ty-4,tx+4,ty+4),fill='#374958');d.rounded_rectangle(bb,radius=5,fill='#f4f3ef',outline='#6e7f8a',width=1);d.text((x,y),text,font=label,fill='#20252b')
 d.text((32,h+115),'MIXED JANUARY / NOVEMBER ADS: review only, NOT a single-date reconstruction.',font=body,fill='#8b3a1a')
 d.text((32,h+150),'Original coordinates preserved. No terrain, roads, QFRONT or Seibu. Full scene / FPS / runtime collision unverified.',font=small,fill='#313943')
 d.text((32,h+180),'Actual Blender 4.2.3 render. Photo textures: Syced (CC0) / Joli Rumi (CC BY-SA 4.0).',font=small,fill='#4a535e')
 board.save(p/(view+'-review.jpg'),quality=95,subsampling=0)
