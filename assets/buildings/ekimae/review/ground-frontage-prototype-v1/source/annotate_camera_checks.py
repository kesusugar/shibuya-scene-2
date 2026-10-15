from pathlib import Path
from PIL import Image,ImageDraw
import json
R=Path(__file__).resolve().parents[1];fits=json.loads((R/'evidence/photo-camera-fit.json').read_text())
for name,c in fits.items():
 im=Image.open(R/'evidence'/f'conditional-camera-{name}.png').convert('RGB');d=ImageDraw.Draw(im)
 d.rectangle((0,0,im.width,65),fill=(245,245,238));d.text((12,10),f'{name}: CONDITIONAL CAMERA | NOT A PHOTO-REGISTRATION PASS',fill=(15,15,15));d.text((12,30),'Red X: observed photo anchors. Green circle: model held-out prediction.',fill=(15,15,15));d.text((12,47),'Blue: fit anchors (virtual sourcecorner plane in alternative). Reference photos are not reproduced.',fill=(15,15,15))
 for i,p in enumerate(c['held_out']):
  x,y=p['observed'];xx,yy=p['predicted'];d.line((x-6,y-6,x+6,y+6),fill=(230,35,35),width=3);d.line((x-6,y+6,x+6,y-6),fill=(230,35,35),width=3);d.ellipse((xx-6,yy-6,xx+6,yy+6),outline=(0,210,80),width=3);d.line((x,y,xx,yy),fill=(230,100,40),width=2);d.text((max(0,xx+7),max(65,yy)),str(i+1),fill=(0,180,40))
 for p in c['fitted_points']:
  x,y=p['prediction'];d.rectangle((x-4,y-4,x+4,y+4),outline=(30,90,240),width=2)
 im.save(R/'evidence'/f'camera-anchor-check-{name}.jpg',quality=94)
