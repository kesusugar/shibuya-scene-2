"""Photo crop (upscaled) above the matching render crop: python3 tools/cropboard.py photo render x0,y0,x1,y1 out label"""
import sys
from PIL import Image, ImageDraw
photo, render, box, out, label = sys.argv[1:6]
x0, y0, x1, y1 = [int(v) for v in box.split(',')]
a = Image.open(photo).convert('RGB').resize((1280, 1749)).crop((x0, y0, x1, y1))
b = Image.open(render).convert('RGB')
W = 1200; a = a.resize((W, int(W*a.height/a.width)), Image.LANCZOS); b = b.resize((W, int(W*b.height/b.width)), Image.LANCZOS)
im = Image.new('RGB', (W, a.height + b.height + 60), (16, 16, 18)); d = ImageDraw.Draw(im)
im.paste(a, (0, 28)); im.paste(b, (0, a.height + 58))
d.text((8, 6), 'REAL (Q032 crop, upscaled)', fill=(255, 255, 255)); d.text((8, a.height + 36), 'RENDER ' + label, fill=(255, 255, 255))
im.save(out, quality=90)
