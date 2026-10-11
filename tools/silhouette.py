"""Silhouette residual between a photo and a render at the same camera: sky mask by colour, per-row building edges."""
import sys, json
import numpy as np
from PIL import Image
def mask(path, W, H):
    a = np.asarray(Image.open(path).convert('RGB').resize((W, H), Image.LANCZOS)).astype(float)
    r, g, b = a[..., 0], a[..., 1], a[..., 2]
    return (b > r + 25) & (b > g + 5)          # sky: blue clearly above red
def edges(m, rows):
    out = {}
    for y in rows:
        nz = np.where(~m[y])[0]
        # building = the longest run of non-sky pixels touching the image centre
        c = m.shape[1]//2
        if m[y, c]: out[y] = None; continue
        L = c
        while L > 0 and not m[y, L-1]: L -= 1
        R = c
        while R < m.shape[1]-1 and not m[y, R+1]: R += 1
        out[y] = (L, R)
    return out
photo, render = sys.argv[1], sys.argv[2]; W, H = 1280, 1749
mp = mask(photo, W, H)
mr = np.asarray(Image.open(render).convert('L').resize((W, H), Image.NEAREST)) < 128   # matte: building white, so 'sky' = dark
top = lambda m: int(np.argmax(~m[:, W//2-60:W//2+60].all(axis=1) == False)) if False else int(np.where((~m[:, W//2-60:W//2+60]).any(axis=1))[0][0])
rows = list(range(int(sys.argv[3]) if len(sys.argv) > 3 else 600, 1150, 25))   # side edges against open sky (Q032: below the crown corners, above the neighbours)
ep, er = edges(mp, rows), edges(mr, rows)
res = []
for y in rows:
    if ep[y] and er[y]: res += [abs(ep[y][0]-er[y][0]), abs(ep[y][1]-er[y][1])]
out = {'crown_top_px': {'photo': top(mp), 'render': top(mr)}, 'rows': len(rows), 'edge_residual_px_mean': round(float(np.mean(res)), 1),
       'edge_residual_px_max': int(np.max(res)), 'edge_residual_px_median': float(np.median(res)), 'edge_residual_px_p80': float(np.percentile(res, 80)), 'per_row': {y: [ep[y], er[y]] for y in rows[::4]}}
print(json.dumps(out, indent=1, default=str))
