"""REAL / v3 / v4 stacked for one crop: python3 tools/triboard.py photo v3_full v4_crop x0,y0,x1,y1 out title"""
import sys
from PIL import Image, ImageDraw
photo, v3, v4, box, out, title = sys.argv[1:7]
x0, y0, x1, y1 = [int(v) for v in box.split(',')]
W = 1200
def fit(im): return im.resize((W, int(W*im.height/im.width)), Image.LANCZOS)
a = fit(Image.open(photo).convert('RGB').resize((1280, 1749)).crop((x0, y0, x1, y1)))
b = fit(Image.open(v3).convert('RGB').resize((1280, 1749)).crop((x0, y0, x1, y1)))
c = fit(Image.open(v4).convert('RGB'))
H = a.height + b.height + c.height + 3*30
im = Image.new('RGB', (W, H), (16, 16, 18)); d = ImageDraw.Draw(im); y = 0
for lab, p in (('REAL  Q032 (Kakidai, CC BY-SA 4.0)', a), ('v3', b), ('v4  ' + title, c)):
    d.text((8, y+8), lab, fill=(255, 255, 255)); im.paste(p, (0, y+30)); y += p.height + 30
im.save(out, quality=90)
