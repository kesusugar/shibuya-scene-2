"""Build only from actual model-render PNGs; no reference-only photographs."""
from PIL import Image,ImageDraw,ImageFont
from pathlib import Path
import json
R=Path(__file__).resolve().parents[1];E=R/'evidence';O=E/'boards';O.mkdir(exist_ok=True)
font=ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf',24);small=ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf',17)
def thumb(path,w,h):
 im=Image.open(path).convert('RGB');im.thumbnail((w,h));bg=Image.new('RGB',(w,h),'#eeeeea');bg.paste(im,((w-im.width)//2,(h-im.height)//2));return bg
for name in ['entry-front','overall','front','left','right','rear']:
 im=Image.new('RGB',(1800,840),'#f5f5f1');d=ImageDraw.Draw(im);d.text((20,14),'SHIBUYA109 | '+name+' | actual Blender 4.2.3 before / after',font=font,fill='#182027')
 for k,(folder,label) in enumerate([('before-final','Accepted predecessor'),('final','Architectural revision 3')]):
  d.text((20+k*900,55),label,font=small,fill='#182027');im.paste(thumb(E/folder/(name+'.png'),890,700),(5+k*900,88))
 d.text((20,800),'Same camera and light. Architectural no-ad state; fitted dimensions, not a survey. No full-game validation.',font=small,fill='#39434a');im.save(O/(name+'-before-after.jpg'),quality=93)
views=['front','left','right','rear','overall','entry-stair'];im=Image.new('RGB',(1800,1390),'#f5f5f1');d=ImageDraw.Draw(im);d.text((20,15),'SHIBUYA109 | complete architectural views',font=font,fill='#182027')
for k,name in enumerate(views):
 x=(k%3)*600;y=65+(k//3)*630;d.text((x+12,y),name,font=small,fill='#182027');im.paste(thumb(E/'final'/(name+'.png'),590,590),(x+5,y+28))
d.text((20,1345),'Actual model renders. Roof, upper logo and unrelated geometry preserved; undocumented rear remains simplified.',font=small,fill='#39434a');im.save(O/'whole-building-views.jpg',quality=93)
