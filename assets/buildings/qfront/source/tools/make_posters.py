"""Original poster art for the neighbour billboards (no brands, no real people)."""
import random
from PIL import Image, ImageDraw, ImageFont, ImageFilter
random.seed(3)
JP = '/usr/share/fonts/opentype/ipafont-gothic/ipag.ttf'; EN = '/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf'
def poster(path, size, bg, accents, lines, jp):
    W, H = size; im = Image.new('RGB', size, bg); d = ImageDraw.Draw(im)
    for _ in range(7):
        r = random.randint(H//6, H//2); x, y = random.randint(0, W), random.randint(0, H)
        d.ellipse((x-r, y-r, x+r, y+r), fill=random.choice(accents))
    im = im.filter(ImageFilter.GaussianBlur(6)); d = ImageDraw.Draw(im)
    f1 = ImageFont.truetype(JP if jp else EN, int(H*.26)); f2 = ImageFont.truetype(JP, int(H*.11))
    d.text((int(W*.05), int(H*.18)), lines[0], font=f1, fill=(255, 255, 255))
    d.text((int(W*.06), int(H*.62)), lines[1], font=f2, fill=(255, 255, 255))
    im.save(path)
poster('textures/poster_a.png', (1400, 600), (20, 60, 150), [(250, 200, 30), (240, 90, 60), (40, 160, 220)], ['SUMMER BEAT', '夏のライブ 8.12 開催'], False)
poster('textures/poster_b.png', (1000, 620), (180, 20, 60), [(255, 140, 30), (250, 230, 200), (90, 20, 120)], ['新発売', 'のどすっきり ミントタブレット'], True)
poster('textures/poster_c.png', (900, 560), (10, 120, 90), [(240, 240, 220), (20, 60, 50), (250, 200, 60)], ['NEW CITY', '駅前ビジョン 放映中'], False)
