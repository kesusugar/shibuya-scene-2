from PIL import Image,ImageDraw,ImageFont
from pathlib import Path
import sys
R=Path(__file__).resolve().parents[2];P=Path(__file__).parent;src=Image.open(sys.argv[1]).convert('RGB');crop=(-230,90,1560,2450)
ref=Image.new('RGB',(1790,2360),'#c6c6c2');ref.paste(src.crop((0,90,1560,2450)),(230,0));d=ImageDraw.Draw(ref)
# Mark only directly visible target areas; do not outline the occluding neighbour as target.
d.rounded_rectangle((230+8,300-90,230+475,805-90),radius=10,outline='#ffe36a',width=8)
d.line([(230+550,1610-90),(230+535,1560-90),(230+430,1560-90)],fill='#ffe36a',width=8)
ref.save(P/'photo-target.jpg',quality=91)
W,H=600,791;out=Image.new('RGB',(1840,960),'#eeeeea');d=ImageDraw.Draw(out);f=ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf',23);sm=ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf',18)
for i,(name,label) in enumerate([('photo-target.jpg','PHOTO | UC building marked'),('before.jpg','BEFORE | main baseline'),('after.jpg','WIP | identity-corrected')]):
 im=Image.open(P/name).convert('RGB').resize((W,H),Image.Resampling.LANCZOS);x=10+i*610;out.paste(im,(x,65));d.text((x+8,21),label,font=f,fill='#222')
d.text((18,875),'Jan 31, 2025 / Syced / CC0. Photo target is partly hidden by the adjacent Ekimae building.',font=sm,fill='#333');d.text((18,906),'Same approximate view; full isolated models. January signs, inferred architecture. October not verified.',font=sm,fill='#333');out.save(P/'comparison.jpg',quality=93)
