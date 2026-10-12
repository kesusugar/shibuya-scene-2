"""Sky fraction and mean RGB in the Q032 crown ROI (rows 300-500, x 470-860 of the 1280x1749 frame).
Usage: crown_metric.py image [crop_x0,crop_y0,scale]  (for crop renders: the crop origin in photo px and the zoom)"""
import sys, numpy as np
from PIL import Image
im = np.asarray(Image.open(sys.argv[1]).convert('RGB')).astype(int)
x0, y0, sc_ = (float(v) for v in sys.argv[2].split(',')) if len(sys.argv) > 2 else (0, 0, 1)
ys = slice(int((300-y0)*sc_), int((500-y0)*sc_)); xs = slice(int((470-x0)*sc_), int((860-x0)*sc_))
x = im[ys, xs]; r, g, b = x[..., 0], x[..., 1], x[..., 2]
print('sky_fraction', round(float(((b > r+35) & (b > g+15) & (b > 110)).mean()), 3), 'meanRGB', x.reshape(-1, 3).mean(0).round().astype(int).tolist())
