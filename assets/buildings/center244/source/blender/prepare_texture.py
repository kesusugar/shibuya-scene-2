"""Offline photo derivative; Python with Pillow/numpy. Only CC0 WB01, never official site imagery.
Usage: python prepare_texture.py /path/to/WB01.jpg. Saves single-plane rectification.
"""
from PIL import Image
import numpy as np,json,sys
from pathlib import Path
im=Image.open(sys.argv[1]).convert('RGBA');a=np.array(im)
y,x=np.indices(a.shape[:2]);a[(x<1752)&(y>969),3]=0 # actual foreground Hisamitsu sign occlusion, not guessed ad text
im=Image.fromarray(a);q=[(1716,761),(2013,733),(2021,1054),(1724,1080)];w,h=420,550;A=[];B=[]
for (x,y),(u,v) in zip([(0,0),(w,0),(w,h),(0,h)],q):
 A.extend([[x,y,1,0,0,0,-u*x,-u*y],[0,0,0,x,y,1,-v*x,-v*y]]);B.extend([u,v])
c=np.linalg.solve(A,B);S=Path(__file__).resolve().parents[1]
im.transform((w,h),Image.Transform.PERSPECTIVE,c,Image.Resampling.BICUBIC).save(S/'refs/billboard-2025-01.png')
(S/'data/texture_quad.json').write_text(json.dumps({'source':'WB01.jpg','source_size':im.size,'quad_TL_TR_BR_BL':q,'corner_evidence':'TL/TR/BR observed; BL extrapolated from visible left/right vertical borders, lower-left occluded','occlusion_mask':'Source x<1752 and y>969 alpha=0; underlying neutral billboard backing remains, no invented lettering','output_size':[w,h],'method':'single projective homography; no full-facade projection'},indent=2)+'\n')
# Only the right fragment of the 4F panel is unoccluded; its left text is not reconstructed.
im=Image.open(sys.argv[1]).convert('RGB');q2=[(1770,1466),(1826,1461),(1827,1527),(1774,1522)];w,h=220,220;A=[];B=[]
for (x,y),(u,v) in zip([(0,0),(w,0),(w,h),(0,h)],q2):
 A.extend([[x,y,1,0,0,0,-u*x,-u*y],[0,0,0,x,y,1,-v*x,-v*y]]);B.extend([u,v])
im.transform((w,h),Image.Transform.PERSPECTIVE,np.linalg.solve(A,B),Image.Resampling.BICUBIC).save(S/'refs/davinci-2025-01.png')
p=S/'data/texture_quad.json';data=json.loads(p.read_text());data['davinci_quad_TL_TR_BR_BL']=q2;data['davinci_note']='Observed woman/4F right fragment only, left obscured; map to right42% of chamfer with neutral full panel backing. No stretching fragment across entire sign; no invented lettering.';p.write_text(json.dumps(data,indent=2)+'\n')
