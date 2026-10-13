"""Deterministic, self-authored paver colour atlas. No photographic input.
python make_paving.py paving_layout.json
"""
import json, sys
from pathlib import Path
import numpy as np
from PIL import Image

config=Path(sys.argv[1]);D=json.loads(config.read_text())
tw,th=D['tile_size_m'];nx,ny=D['atlas_tiles'];w,h=D['atlas_px']
x=(np.arange(w)+.5)*tw*nx/w; y=(np.arange(h)+.5)*th*ny/h
X,Y=np.meshgrid(x,y);row=np.floor(Y/th).astype(int)
offset=(row%2)*tw*.5;column=np.floor((X+offset)/tw).astype(int)%nx
local_x=(X+offset)%tw;local_y=Y%th
distance=np.minimum(np.minimum(local_x,tw-local_x),np.minimum(local_y,th-local_y))
pixel_m=max(tw*nx/w,th*ny/h)
blend=np.clip((D['joint_width_m']/2+pixel_m*.5-distance)/pixel_m,0,1)
rng=np.random.default_rng(D['seed']);variation=rng.uniform(-D['tile_variation'],D['tile_variation'],(ny,nx))
level=D['tile_level']+variation[row%ny,column]+rng.normal(0,D['grain'],(h,w))
level=level*(1-blend)+D['joint_level']*blend
rgb=np.repeat(np.clip(np.rint(level*255),0,255).astype(np.uint8)[...,None],3,axis=2)
output=(config.parent/D['texture']).resolve();output.parent.mkdir(parents=True,exist_ok=True)
Image.fromarray(rgb).save(output)
print('PAVING',output.name,w,h,'period_m',tw*nx,th*ny,'mean_srgb',float(rgb.mean()/255))
