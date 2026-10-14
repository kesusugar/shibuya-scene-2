from PIL import Image
import numpy as np,json
from pathlib import Path
import sys
root=Path(__file__).resolve().parents[1]
im=Image.open(sys.argv[1])
# Source coordinates in full original, manually read quadrilaterals. No generative filling.
items={
'roof_campaign':([[541,419],[1075,397],[1090,685],[557,704]],[1024,560]),
'uc_east':([[152,342],[445,313],[474,750],[174,790]],[512,768]),
'uc_south':([[14,308],[152,342],[174,790],[31,758]],[320,768]),
'vanguard':([[593,1119],[675,1095],[695,1444],[605,1467]],[160,640]),
'mizuho':([[523,1842],[551,1835],[571,2021],[536,2034]],[128,512])}
for name,(q,size) in items.items():
 w,h=size; dst=[(0,0),(w,0),(w,h),(0,h)];A=[];B=[]
 for (x,y),(u,v) in zip(dst,q):A.extend([[x,y,1,0,0,0,-u*x,-u*y],[0,0,0,x,y,1,-v*x,-v*y]]);B.extend([u,v])
 coef=np.linalg.solve(np.array(A),np.array(B));out=im.transform((w,h),Image.Transform.PERSPECTIVE,coef,Image.Resampling.BICUBIC);out.save(root/'textures'/f'{name}.png')
(root/'data/texture_quads.json').write_text(json.dumps({'date':'2025-01-31','source':'https://commons.wikimedia.org/wiki/File:Shibuya_crossing,_seen_from_Shibuya_Stream.jpg','author':'Syced','license':'CC0','quads':items},indent=2))
