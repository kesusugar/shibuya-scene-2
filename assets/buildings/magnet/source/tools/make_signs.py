# Original placeholder artwork for the MAGNET 2025 sign layer (no photo pixels, no third-party artwork).
#   python3 tools/make_signs.py textures/
# Ads and screens only need the right tone, colour blocks and layout seen in the photos; their real content
# changes weekly and is not reproduced.
import sys, os, random, math
from PIL import Image, ImageDraw, ImageFilter, ImageFont

out = sys.argv[1]; os.makedirs(out, exist_ok=True); random.seed(25)
JP = '/usr/share/fonts/opentype/ipafont-gothic/ipag.ttf'

def font(sz):
    try: return ImageFont.truetype(JP, sz)
    except OSError: return ImageFont.load_default()

def blobs(im, n, cols, rmin, rmax):
    d = ImageDraw.Draw(im)
    for _ in range(n):
        x, y = random.uniform(0, im.width), random.uniform(0, im.height); r = random.uniform(rmin, rmax)
        d.ellipse([x-r, y-r, x+r, y+r], fill=random.choice(cols))

# LED in the grey box (M027: deep red/black motion graphic)
im = Image.new('RGB', (760, 900), (18, 8, 12)); blobs(im, 40, [(150, 20, 30), (220, 60, 50), (90, 10, 25), (240, 170, 150)], 30, 140)
im = im.filter(ImageFilter.GaussianBlur(18)); d = ImageDraw.Draw(im)
d.rectangle([60, 700, 700, 760], fill=(240, 235, 230)); d.text((80, 708), 'NEW SEASON  2025', font=font(44), fill=(30, 20, 25))
im.save(os.path.join(out, 'led_box.png'))

# STARTS corner screen (M027: dark red/purple scene)
im = Image.new('RGB', (720, 480), (40, 20, 50)); blobs(im, 30, [(170, 40, 60), (90, 40, 120), (230, 120, 140), (30, 20, 60)], 20, 100)
im.filter(ImageFilter.GaussianBlur(12)).save(os.path.join(out, 'led_starts.png'))

# Drum wrap (M027: white sheet, two lines of black text, black foot band with a red arrow)
W, H = 1024, 2048; im = Image.new('RGB', (W, H), (244, 244, 240)); d = ImageDraw.Draw(im)
d.text((140, 620), '【いつもの街に、', font=font(92), fill=(25, 25, 25)); d.text((260, 760), 'あたらしい物語】', font=font(92), fill=(25, 25, 25))
d.text((560, 1180), '近日公開', font=font(56), fill=(60, 60, 60))
d.rectangle([0, 1560, W, H], fill=(12, 12, 12)); d.polygon([(140, 1760), (300, 1660), (300, 1720), (520, 1720), (520, 1800), (300, 1800), (300, 1860)], fill=(220, 40, 30))
d.text((600, 1700), '10th', font=font(110), fill=(220, 40, 30))
im.save(os.path.join(out, 'drum_wrap.png'))

# West banner (M027/M001: pastel idol-group banner, 6 portrait tiles + title block)
W, H = 512, 2048; im = Image.new('RGB', (W, H), (236, 240, 250)); d = ImageDraw.Draw(im)
for k in range(6):
    y0 = 180 + k*250; x0 = 40 if k % 2 == 0 else 200
    d.rounded_rectangle([x0, y0, x0+270, y0+230], 20, fill=(250, 222, 228))
    d.ellipse([x0+85, y0+30, x0+185, y0+130], fill=(238, 205, 190)); d.ellipse([x0+70, y0+15, x0+200, y0+95], fill=(70, 50, 45))
    d.rectangle([x0+60, y0+140, x0+210, y0+230], fill=random.choice([(150, 190, 235), (240, 240, 245), (200, 180, 230)]))
d.text((40, 40), 'NEW SINGLE', font=font(64), fill=(60, 110, 200)); d.rectangle([20, 1700, 492, 1880], fill=(70, 130, 220))
d.text((50, 1730), '全国進出開始', font=font(70), fill=(255, 255, 255)); d.text((60, 1920), 'NOW ON SALE', font=font(40), fill=(60, 60, 80))
im.save(os.path.join(out, 'west_banner.png'))

# Simplified M mark (red/blue chevrons; an approximation, not the registered artwork)
im = Image.new('RGBA', (512, 512), (0, 0, 0, 0)); d = ImageDraw.Draw(im)
for k in range(4):
    c = (210, 30, 40, 255) if k < 2 else (40, 80, 190, 255); o = k*34
    d.polygon([(60, 100+o), (256, 300+o), (452, 100+o), (452, 130+o), (256, 330+o), (60, 130+o)], fill=c)
im.save(os.path.join(out, 'magnet_mark.png'))
print('signs ->', out)
