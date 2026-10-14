"""Reproject licensed EK01 full image, 4032x2268, to November sign crops.
python recrop_ek01.py /path/to/EK01-full.jpg
No generated lettering, no other era ad photographs, no inpainting.
"""
from pathlib import Path
import json,sys,numpy as np
from PIL import Image
root=Path(__file__).resolve().parents[1];cfg=json.loads((root/'data/facades.json').read_text());im=Image.open(sys.argv[1]).convert('RGB')
assert im.size==(4032,2268)
def warp(quad,size):
 w,h=size;dst=[(0,0),(w,0),(w,h),(0,h)];a=[];b=[]
 for (x,y),(u,v) in zip(dst,quad):a.extend([[x,y,1,0,0,0,-u*x,-u*y],[0,0,0,x,y,1,-v*x,-v*y]]);b.extend([u,v])
 coeff=np.linalg.solve(a,b);return im.transform(size,Image.Transform.PERSPECTIVE,coeff,Image.Resampling.BICUBIC)
for name,d in cfg['textures'].items():
 quad=d.get('full_resolution_quad') or [[x*3.15,y*3.15] for x,y in d['quad']]
 d['full_resolution_quad']=quad
 # 1024 width for rooftop; tenant signs 768. Preserve original photo content.
 size=d['size']; size=([1024,640] if name=='samsung' else [768,512] if name=='hit_sky' else [768,160] if name in ['shabu','francais','gusto'] else size)
 d['size']=size;warp(quad,tuple(size)).save(root/'textures'/f'{name}.png',optimize=True)
quad=[[991,850],[1078,882],[948,1477],[851,1460]]
warp(quad,(192,1024)).save(root/'textures/longboard.png',optimize=True)
cfg['textures']['longboard']={'full_resolution_quad':quad,'size':[192,1024],'basis':'EK01 visible right-edge 17LIVE longboard; verified 2025-10-30 to 2025-11-30 campaign, photograph only; small top edge and bottom obstruction retained.'}
cfg['crop_revision']={'source_size':[4032,2268],'method':'Perspective reprojection of full-resolution original; no invented pixels. Roof HiT left edge remains outside photograph.'}
(root/'data/facades.json').write_text(json.dumps(cfg,ensure_ascii=False,indent=2)+'\n')

# Shared-boundary multi-face rectification supersedes original whole-floor quads.
from rectify_restaurant_signs import rectify
rectify(sys.argv[1])
