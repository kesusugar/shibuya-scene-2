"""One continuous local fan-sett atlas, not repetition of a nonseamless delivery sample."""
from pathlib import Path
import numpy as np
from PIL import Image

w,h=1024,688
X,Y=np.meshgrid((np.arange(w)+.5)*10.4/w-5.2,(np.arange(h)+.5)*7/h-4)
# Staggered semicircular fan fields; metric values are recorded production estimates.
row=np.floor((Y+4)/1.0)
cx=(np.floor((X+(row%2)*.85)/1.7)+.5)*1.7-(row%2)*.85
cy=row*1.0-4
dx,dy=X-cx,Y-cy
r=np.hypot(dx,dy);angle=np.arctan2(dy,dx)
ring=np.floor(r/.10);pitch=np.maximum(3,np.round((ring+.5)*np.pi))
radial=np.minimum(r%.10,.10-r%.10)
phase=(angle/np.pi*pitch+(ring%2)*.5)%1
tangent=np.minimum(phase,1-phase)*.10
distance=np.minimum(radial,tangent)
joint=np.clip((.004-distance)/.005,0,1)
rng=np.random.default_rng(173)
value=.70+.035*np.sin(np.floor(angle/np.pi*pitch)*31+ring*19)+rng.normal(0,.003,(h,w))
value=value*(1-joint)+.43*joint
rgb=np.clip(np.round(value[...,None]*np.array([1.0,1.01,1.0])*127)*2,0,255).astype(np.uint8)
Image.fromarray(rgb).save(Path(__file__).with_name('fan-paving.png'))
