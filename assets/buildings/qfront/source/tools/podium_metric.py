"""Mean RGB of the podium ROIs (Q032 photo px) in an image. Usage: podium_metric.py image [crop_x0,crop_y0,scale]"""
import sys, numpy as np
from PIL import Image
im = np.asarray(Image.open(sys.argv[1]).convert('RGB')).astype(int)
x0, y0, s_ = (float(v) for v in sys.argv[2].split(',')) if len(sys.argv) > 2 else (0, 0, 1)
for n, (ya, yb, xa, xb) in {'2F_blinds': (1380, 1420, 480, 820), '2F_band': (1440, 1470, 480, 780), '1F': (1490, 1540, 480, 700)}.items():
    r = im[int((ya-y0)*s_):int((yb-y0)*s_), int((xa-x0)*s_):int((xb-x0)*s_)]
    print(n, r.reshape(-1, 3).mean(0).round().astype(int).tolist(), end='  ')
print()
