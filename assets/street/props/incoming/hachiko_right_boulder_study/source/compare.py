from PIL import Image,ImageDraw,ImageFont
from pathlib import Path
import sys
p=Path(__file__).resolve().parents[1]
src=Path(sys.argv[1]);im=Image.open(src);assert im.size==(3072,4096)
ref=im.crop((2100,1630,2600,1980));ref.save(p/'evidence'/'reference_crop.jpg',quality=95)
W=1500;H=520;can=Image.new('RGB',(W,H),'#f1f0ec');d=ImageDraw.Draw(can);font=ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf',18);small=ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf',14)
for i,(img,label) in enumerate([(ref,'July 2025 photograph (cropped)'),(Image.open(p/'evidence'/'source_algorithm_baseline.png'),'Previous algorithm example; not exact main'),(Image.open(p/'evidence'/'front.png'),'Photo-informed replacement study')]):
 img=img.convert('RGB');img.thumbnail((490,380));can.paste(img,(i*500+(500-img.width)//2,60+(380-img.height)//2));d.text((i*500+10,20),label,font=font,fill='black')
d.text((12,452),'Photo: RuinDig / Yuki Uchida | CC BY 4.0 | 13 July 2025 | Crop/resize only. No photo texture on model.',font=small,fill='black')
d.text((12,477),'Model dimensions, back and depth inferred. Not camera-calibrated. 2026 continued existence unconfirmed. Unplaced study.',font=small,fill='black')
can.save(p/'evidence'/'comparison.jpg',quality=94)
