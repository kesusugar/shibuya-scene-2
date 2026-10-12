"""Procedural facade tiles for the C-level context (own work, no photographs). One tile = one bay x one storey.
python3 make_facades.py out_dir
  facade_ribbon.png   continuous window band over a spandrel (office / commercial)
  facade_punched.png  punched windows in a wall (mixed-use / older 雑居ビル)
  facade_*_emit.png   window mask for the night look (white = lit glass)
The material colour multiplies the tile, so the wall tint varies per building while glass stays dark."""
import sys
from PIL import Image, ImageDraw
out = sys.argv[1]
W = H = 256


def tile(kind):
    im = Image.new('RGB', (W, H), (232, 230, 226)); em = Image.new('L', (W, H), 0)
    d, e = ImageDraw.Draw(im), ImageDraw.Draw(em)
    glass = (46, 56, 66)
    if kind == 'ribbon':
        y0, y1 = int(H * 0.08), int(H * 0.64)                   # spandrel at the bottom third, sill line
        d.rectangle([0, y0, W, y1], fill=glass); e.rectangle([0, y0 + 4, W, y1 - 4], fill=255)
        for x in (0, W // 2):                                    # mullions every half bay
            d.rectangle([x - 3, y0, x + 3, y1], fill=(150, 152, 154)); e.rectangle([x - 4, y0, x + 4, y1], fill=0)
        d.rectangle([0, y1, W, y1 + 6], fill=(190, 190, 188))      # sill
        for y in range(y0 + 10, y1, 18):                         # faint reflection banding
            d.line([0, y, W, y], fill=(56, 66, 76))
    else:
        x0, x1, y0, y1 = int(W * 0.22), int(W * 0.78), int(H * 0.18), int(H * 0.70)
        d.rectangle([x0 - 5, y0 - 5, x1 + 5, y1 + 8], fill=(200, 198, 194))   # frame/reveal
        d.rectangle([x0, y0, x1, y1], fill=glass); e.rectangle([x0 + 3, y0 + 3, x1 - 3, y1 - 3], fill=255)
        d.rectangle([(x0 + x1) // 2 - 2, y0, (x0 + x1) // 2 + 2, y1], fill=(150, 152, 154))
        for y in range(y0 + 8, y1, 16):
            d.line([x0, y, x1, y], fill=(56, 66, 76))
    d.line([0, H - 1, W, H - 1], fill=(205, 203, 199))            # floor line
    return im, em


for k in ('ribbon', 'punched'):
    im, em = tile(k)
    im.save(f'{out}/facade_{k}.png', optimize=True); em.save(f'{out}/facade_{k}_emit.png', optimize=True)
print('ok')
