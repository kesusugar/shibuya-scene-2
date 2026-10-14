from PIL import Image,ImageDraw,ImageFont
from pathlib import Path
p=Path(__file__).resolve().parent
im=Image.open(p/'assembly-east.png').convert('RGB');w,h=im.size
board=Image.new('RGB',(w,h+190),'#f5f5f3');board.paste(im,(0,85));d=ImageDraw.Draw(board)
f='/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf'
head=ImageFont.truetype(f,29);body=ImageFont.truetype(f,20);small=ImageFont.truetype(f,18)
d.text((32,23),'3-building geometry assembly | not full scene',font=head,fill='#222222')
d.text((32,h+105),'January/November ads shown together for asset review only; not a single-date reconstruction',font=body,fill='#222222')
d.text((32,h+139),'Photo-derived textures: Syced (CC0) / Joli Rumi (CC BY-SA 4.0). Corrected Ekimae full-face mapping.',font=small,fill='#454545')
board.save(p/'three-building-assembly-final.jpg',quality=94,subsampling=0)
