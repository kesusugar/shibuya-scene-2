"""Night ROIs on the Q031 frame (1280x1887). Usage: night_metric.py image"""
import sys, numpy as np
from PIL import Image
a = np.asarray(Image.open(sys.argv[1]).convert('RGB').resize((1280, 1887))).astype(int)
DY = int(sys.argv[2]) if len(sys.argv) > 2 else 0   # podium offset of the render (camera fit residual), applied to podium ROIs only
R = {'sky': (150, 300, 20, 100), 'left_face_lit': (500, 900, 140, 280), 'right_face_lit': (500, 900, 1030, 1150), 'front_glass': (600, 800, 450, 850),
     'crown': (150, 330, 360, 960), 'podium_2F': (1460, 1560, 380, 780), 'band_tsutaya': (1560, 1610, 790, 1000), 'podium_1F': (1620, 1690, 380, 760)}
print(' '.join(f"{k}={a[y0+(DY if k.startswith(('podium','band')) else 0):y1+(DY if k.startswith(('podium','band')) else 0), x0:x1].reshape(-1, 3).mean(0).round().astype(int).tolist()}" for k, (y0, y1, x0, x1) in R.items()))
