from PIL import Image,ImageOps,ImageDraw,ImageFont
from pathlib import Path
R=Path(__file__).resolve().parent;repo=R.parents[1]
f=ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf',24);small=ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf',19)
def board(name,items,footer):
 w=550;h=1030;im=Image.new('RGB',(w*len(items),h+115),(245,245,240));d=ImageDraw.Draw(im)
 for i,(path,title,sub) in enumerate(items):
  a=Image.open(path).convert('RGB');a=ImageOps.contain(a,(w-14,h-88),Image.Resampling.LANCZOS)
  im.paste(a,(i*w+(w-a.width)//2,85+(h-88-a.height)//2));d.text((i*w+12,12),title,fill=(25,30,35),font=f);d.text((i*w+12,47),sub,fill=(65,65,65),font=small)
 d.text((15,h+10),'BIG ECHO / Shibuya Heiwa 21-8 | legacy asset ID: quattro',fill=(25,30,35),font=f)
 for k,line in enumerate(footer):d.text((15,h+47+k*25),line,fill=(50,50,50),font=small)
 im.save(R/name,quality=93,subsampling=0)
photo=repo/'assets/buildings/quattro/source/refs/WB01-target-2025-01.png'
board('comparison-photo.jpg',[(photo,'Reference photo','Syced / CC0 / 31 Jan 2025'),(R/'before-photo.png','BEFORE','Original generic facade'),(R/'after-photo.png','AFTER: architecture','No image textures / normal asset'),(R/'after-photo-january.png','AFTER: January preview','Optional dated layer, NOT registered')],['Before/after share one camera. Photo angle is approximate, not survey-calibrated; neighbours omitted in renders.','Visible roof features reconstructed; exact spans/depths, storefront divisions and unseen faces remain inferred.'])
for view in ['front','side']:
 board('comparison-'+view+'.jpg',[(R/f'before-{view}.png','BEFORE: '+view,'Original generic facade'),(R/f'after-{view}.png','AFTER: '+view,'Architecture only / no dated pixels')],['Same camera; original shell, datum and steep roof retained.','No protected QFRONT or Seibu geometry modified.'])
