"""Draws PLATEAU LOD2 outlines of chosen buildings on the Stream 2025 photo with the provisional camera (no occlusion).
python3 scripts/plateau-overlay.py  (edit targets; output in /tmp/claude-0/ov)"""
import json, sys, importlib.util
from PIL import Image, ImageDraw
spec = importlib.util.spec_from_file_location('s', 'scripts/solve-ref-camera.py'); s = importlib.util.module_from_spec(spec)
src = open('scripts/solve-ref-camera.py').read().split("if __name__")[0]
g = {}; exec(compile(src.split('\nL = ')[0] if '\nL = ' in src else src, 'x', 'exec'), g)
cam = json.load(open('assets/street/core/web/projected.json'))['camera']
C = json.load(open('assets/context/core/source/data/context_input.json'))
targets = {'way/136690966': 'red', 'way/136691389': 'yellow', 'way/136691379': 'cyan', 'way/60739635': 'magenta'}
im = Image.open('assets/street/core/source/refs/stream_2025.jpg').convert('RGB').resize((cam['W'], cam['H'])); d = ImageDraw.Draw(im)
for b in C['buildings']:
    if b['id'] not in targets: continue
    for srf in b['surfaces']:
        uv, z = g['project'](cam, srf['ring'])
        pts = [tuple(map(float, q)) for q in uv]
        if len(pts) > 1: d.line(pts + [pts[0]], fill=targets[b['id']], width=1)
im.save('evidence/c1-context/next/stream_plateau_overlay.png'); print('ok')
