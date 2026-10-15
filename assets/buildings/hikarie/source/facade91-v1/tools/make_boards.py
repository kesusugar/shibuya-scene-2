from pathlib import Path
from PIL import Image,ImageDraw,ImageFont
R=Path(__file__).resolve().parents[1];E=R/'evidence';font=lambda n:ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf',n)
for view in ['front','west_side','photo_jun15_angle']:
 b=Image.new('RGB',(1600,1060),'#f5f7fa');d=ImageDraw.Draw(b)
 for i,(tag,title) in enumerate([('before','Accepted baseline'),('after','Source91 bounded candidate')]):
  d.text((i*800+20,18),title,font=font(26),fill='#223040');im=Image.open(E/f'{view}-{tag}.png');im.thumbnail((790,940));b.paste(im,(i*800+(800-im.width)//2,70))
 d.text((20,1020),'Actual same-camera renders; shell/roof/neighbor63 preserved. Lower rows remain unresolved.',font=font(22),fill='#223040');b.save(E/f'{view}-before-after.jpg',quality=93)
b=Image.new('RGB',(1800,1030),'#f5f7fa');d=ImageDraw.Draw(b)
for i,(title,im) in enumerate([('Photo: June15,2025',Image.open(R/'source/JUN15-hikarie-crop.jpg').crop((70,70,640,620))),('Accepted baseline',Image.open(E/'photo_jun15_angle-before.png').crop((225,250,410,650))),('Bounded candidate',Image.open(E/'photo_jun15_angle-after.png').crop((225,250,410,650)))]):
 x=i*600+15;d.text((x,22),title,font=font(25),fill='#223040');im.thumbnail((570,700));b.paste(im,(x+(570-im.width)//2,90))
for y,s in [(820,'Pale dominant field corrected; narrow dark feature retained as estimate. Lower rows remain occluded/unknown.'),(860,'Actual fixed-camera model renders. Photo pose/lens uncalibrated; no synthetic after or photograph texture.'),(900,'Photo: Nesnad,2025-06-15,CC BY4.0. Crop+resize only; original reports panorama/TouchRetouch.'),(940,'commons.wikimedia.org/wiki/File:Hikarie_and_Shibuya_scramble_square_buildings_2025_June_15.jpeg'),(978,'License: https://creativecommons.org/licenses/by/4.0/ | Candidate only, not final whole-scene validation.')]:d.text((18,y),s,font=font(19 if y<940 else 17),fill='#223040')
b.save(E/'photo-before-after.jpg',quality=94)
