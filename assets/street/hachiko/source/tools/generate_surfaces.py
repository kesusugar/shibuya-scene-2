"""Generate original patina/granite noise and typeset plaque, no photo crops."""
from pathlib import Path
import sys,numpy as np
from PIL import Image,ImageFont,ImageDraw
root=Path(__file__).resolve().parents[1]/'data';rng=np.random.default_rng(42)
# bronze: warm brown patina measured on the lit leg in july095 (2025-07, sRGB ~98,89,81); was a green-grey 76,84,74
for name,base in [('bronze',[94,82,68]),('granite',[118,113,102])]:
 a=rng.normal(0,14 if name=='granite' else 10,(256,256,1))+np.array(base)
 Image.fromarray(np.uint8(np.clip(a,0,255))).save(root/(name+'.png'))
font_path=sys.argv[1] if len(sys.argv)>1 else '/usr/share/fonts/opentype/noto/NotoSerifCJK-Bold.ttc'
im=Image.new('RGB',(128,512),(45,48,44));dr=ImageDraw.Draw(im);font=ImageFont.truetype(font_path,87)
for i,ch in enumerate('忠犬ハチ公'):dr.text((20,i*101-7),ch,font=font,fill=(146,113,83))
im.save(root/'plaque.png')
