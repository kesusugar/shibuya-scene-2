"""Plan figure of the C2b layout: python3 plot_layout.py ground_input.json street_input.json street_layout.json out.png"""
import json, math, sys
from PIL import Image, ImageDraw, ImageFont
G, S, L = (json.load(open(p)) for p in sys.argv[1:4])
C, R, W = (6.5, -2.0), 58, 1100
sc = W / (2 * R)
px = lambda x, y: ((x - C[0] + R) * sc, (C[1] + R - y) * sc)
im = Image.new('RGB', (W, W), (40, 42, 46)); d = ImageDraw.Draw(im)
col = {'road': (70, 70, 74), 'intersection': (78, 78, 82), 'sidewalk': (150, 146, 138), 'island': (170, 160, 140)}
for s in G['surfaces']:
    if any(abs(x - C[0]) < R + 5 and abs(y - C[1]) < R + 5 for x, y, *_ in s['ring']):
        d.polygon([px(x, y) for x, y, *_ in s['ring']], fill=col[s['class']])
for c in G['crosswalks']:
    for b in c['bars']: d.polygon([px(*p) for p in b], fill=(230, 230, 225))
for f in S['features']:
    if f['kind'] == 'entrance': d.polygon([px(*p) for p in f['ring']], fill=(60, 90, 160), outline=(255, 255, 255))
    else:
        x, y = px(*f['point']); d.ellipse([x - 9, y - 9, x + 9, y + 9], fill=(40, 120, 40))
for r in L['rail_runs']: d.line([px(*p) for p in r], fill=(255, 255, 255), width=3)
font = ImageFont.load_default()
for i in L['items']:
    x, y = px(*i['xy'])
    if i['kind'] == 'vehicle_signal':
        ax, ay = px(i['xy'][0] + i['arm_dir'][0] * i['arm_m'], i['xy'][1] + i['arm_dir'][1] * i['arm_m'])
        d.line([x, y, ax, ay], fill=(255, 140, 0), width=4); d.ellipse([x - 6, y - 6, x + 6, y + 6], fill=(255, 140, 0))
        fx, fy = i['facing']; d.line([ax, ay, ax + fx * 18, ay - fy * 18], fill=(0, 255, 120), width=3)
    elif i['kind'] == 'ped_signal':
        d.ellipse([x - 5, y - 5, x + 5, y + 5], fill=(255, 60, 60)); fx, fy = i['facing']; d.line([x, y, x + fx * 14, y - fy * 14], fill=(255, 60, 60), width=2)
    else:
        d.rectangle([x - 5, y - 5, x + 5, y + 5], fill=(255, 220, 90))
    d.text((x + 7, y + 4), i['id'].replace('PED_', '').replace('VEH_', 'V'), fill=(255, 255, 255), font=font)
d.text((10, 10), 'C2b layout (plan, north up). orange=vehicle mast arm (green tick=facing), red=ped signal, yellow=photo lamp/sign, white=kerb rail, blue=entrance, green=tree', fill=(255, 255, 255), font=font)
im.save(sys.argv[4])
