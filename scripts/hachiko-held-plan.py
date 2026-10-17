"""Draw the local scene footprint comparison for the held Hachiko assets."""
import json
import sys
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont

out = Path(sys.argv[1] if len(sys.argv) > 1 else 'evidence/hachiko-held-20261017/plan.png')
facilities = json.loads(Path('assets/street/plaza-facilities/source/data/layout.json').read_text())['items']
kiosk = json.loads(Path('assets/buildings/plaza-kiosk/source/data/plateau.json').read_text())
box = json.loads(Path('assets/buildings/shibu-hachi-box/source/placement-and-build.json').read_text())['position_source']['ring_plan_m']
statue = json.loads(Path('assets/street/hachiko/source/data/layout.json').read_text())['xy']
tree = json.loads(Path('assets/street/hachiko-rear-tree/web/placement.json').read_text())['position']
pin = ((139.70068316 - 139.7005) * 111320 * .8123, (35.65890005 - 35.6595) * 110574)
left, right, low, high = 0, 87, -84, -24
scale = 12
image = Image.new('RGB', (1120, 840), '#f5f4ed')
d = ImageDraw.Draw(image)
def font_at(size):
    for name in ['/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf',
                 '/usr/share/fonts/truetype/liberation2/LiberationSans-Regular.ttf',
                 'C:/Windows/Fonts/arial.ttf']:
        if Path(name).is_file():
            return ImageFont.truetype(name, size)
    return ImageFont.load_default()

font = font_at(20)
small = font_at(15)

def xy(p):
    return (int(36 + (p[0] - left) * scale), int(50 + (high - p[1]) * scale))

def polygon(points, fill, outline):
    d.polygon([xy(p) for p in points], fill=fill, outline=outline, width=3)

ground = json.loads(Path('assets/ground/core/source/data/ground_input.json').read_text())['surfaces']
for face in ground:
    if face['class'] == 'island' and len(face['ring']) == 3:
        pts = [p[:2] for p in face['ring']]
        if any(0 < p[0] < 20 and -58 < p[1] < -24 for p in pts):
            d.polygon([xy(p) for p in pts], fill='#d9e6ce')

polygon(box, '#b5d5f5', '#477eaa')
roof = next(s['ring'] for s in kiosk['surfaces'] if s['kind'] == 'RoofSurface')
polygon([p[:2] for p in roof], '#f0d5aa', '#9e7136')
for item in facilities:
    polygon(item['ring'], '#cabee8' if item['id'].endswith('858994297') else '#b9adc6', '#69548c')

for point, color, label, shift in [
    (statue, '#b54f42', 'Hachiko statue', (8, -18)),
    ((tree[0], -tree[2]), '#3c823e', 'rear tree (estimated)', (8, -32)),
    (pin, '#b11fa0', 'lottery official map pin', (8, 12)),
]:
    x, y = xy(point)
    d.ellipse((x - 7, y - 7, x + 7, y + 7), fill=color, outline='white', width=2)
    d.text((x + shift[0], y + shift[1]), label, fill=color, font=small)

for x, y, label in [(24, -39, 'BOX'), (31, -42, 'way/155538676 + PLATEAU'),
                    (7, -58, 'way/155807205'), (8, -62, 'way/858994297')]:
    d.text(xy((x, y)), label, fill='#212121', font=small)

d.text((36, 10), 'Hachiko scene plan | X east, Y north | 12 px / m', fill='#222222', font=font)
d.text((36, 780), 'Outlines: stored OSM/PLATEAU footprints. Pin: lottery official map (approximate).', fill='#333333', font=small)
d.text((36, 803), 'Green areas: current Core island triangles. Official A8 drawing gives order, not a surveyed footprint.', fill='#333333', font=small)
out.parent.mkdir(parents=True, exist_ok=True)
image.save(out)
print(out)
