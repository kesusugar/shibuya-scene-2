from pathlib import Path
from PIL import Image,ImageDraw,ImageFont
R=Path(__file__).resolve().parents[1]
font=ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf',29)
small=ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf',22)
for view in ['close','context']:
 before=Image.open(R/'evidence'/f'before_{view}.png').convert('RGB');after=Image.open(R/'evidence'/f'after_{view}.png').convert('RGB')
 canvas=Image.new('RGB',(before.width*2,before.height+110),(244,243,239));d=ImageDraw.Draw(canvas)
 d.text((26,16),'BEFORE | radial triangles + exposed spherical cores',fill=(45,45,40),font=font)
 d.text((before.width+26,16),'AFTER | curved dense sprays, no spherical cores',fill=(45,45,40),font=font)
 canvas.paste(before,(0,62));canvas.paste(after,(before.width,62));d.text((26,before.height+76),'Matched camera + lighting. Component render only, not a full app capture. Existing stone / rails unchanged.',fill=(60,60,55),font=small)
 canvas.save(R/'evidence'/f'comparison_{view}.png')
print('Comparison PNGs written from unchanged render pixels')
