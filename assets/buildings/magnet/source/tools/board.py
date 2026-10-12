# Comparison boards for G3 (same camera only): photo | Cycles | 50 % overlay, plus close crops.
#   python3 tools/board.py <photo> <render> <out_dir> <tag>
import sys, os
from PIL import Image, ImageDraw, ImageFont

photo_p, render_p, out, tag = sys.argv[1:5]; os.makedirs(out, exist_ok=True)
P = Image.open(photo_p).convert('RGB'); R = Image.open(render_p).convert('RGB').resize(P.size)
try: F = ImageFont.truetype('/usr/share/fonts/opentype/ipafont-gothic/ipag.ttf', 26)
except OSError: F = ImageFont.load_default()

def label(im, text):
    d = ImageDraw.Draw(im); d.rectangle([0, 0, im.width, 40], fill=(0, 0, 0)); d.text((10, 6), text, font=F, fill=(255, 255, 255)); return im

W = 640; s = W / P.width; H = int(P.height * s)
p, r = P.resize((W, H)), R.resize((W, H)); o = Image.blend(p, r, .5)
board = Image.new('RGB', (W*3, H), 'black')
for i, (im, t) in enumerate(((p, '写真'), (r, 'Cycles（同じカメラ）'), (o, '重ね合わせ 50%'))): board.paste(label(im.copy(), t), (W*i, 0))
board.save(os.path.join(out, f'A_{tag}_whole.jpg'), quality=88)

crops = {'drum_tower': (380, 40, 860, 560), 'west_wall': (0, 200, 480, 720), 'podium': (100, 700, 860, 1060)}
for k, box in crops.items():
    a, b = P.crop(box), R.crop(box); w = a.width
    c = Image.new('RGB', (w*2, a.height), 'black'); c.paste(label(a, f'写真 {k}'), (0, 0)); c.paste(label(b, 'Cycles'), (w, 0))
    c.save(os.path.join(out, f'B_{tag}_{k}.jpg'), quality=88)
print('boards ->', out)
