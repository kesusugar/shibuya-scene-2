import sys
from PIL import Image,ImageDraw,ImageFont
photo,render,out=sys.argv[1:4];label=sys.argv[4] if len(sys.argv)>4 else ''
F=ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf',20)
a=Image.open(photo).convert('RGB');b=Image.open(render).convert('RGB').resize(a.size)
H=900;a=a.resize((int(a.width*H/a.height),H));b=b.resize(a.size)
o=Image.new('RGB',(a.width*2+10,H+40),(16,18,22));o.paste(a,(0,40));o.paste(b,(a.width+10,40));d=ImageDraw.Draw(o)
d.text((6,8),'REAL',fill=(255,255,255),font=F);d.text((a.width+16,8),'RENDER '+label,fill=(255,255,255),font=F)
o.save(out,quality=88)
