"""Rectify only WB01 (Syced CC0, 2025-01-31); no generated lettering.
Usage: python extract_fullres.py /path/to/WB01.jpg
"""
from pathlib import Path
from PIL import Image, ImageFilter
import numpy as np,json,sys
root=Path(__file__).resolve().parents[1]; f=json.loads((root/'data/facades.json').read_text());im=Image.open(sys.argv[1]).convert('RGB');sx,sy=im.width/900,im.height/1195
entries=dict(f['textures'])
entries['sanzenri']={'quad':[[0,0]]*4,'size':[192,512]}
entries['taiseido_left']={'quad':[[0,0]]*4,'size':[320,128]}
entries['taiseido_right']={'quad':[[0,0]]*4,'size':[384,128]}
entries['curtain']={'quad':[[280,488],[350,498],[350,520],[280,510]],'size':[512,160]}
entries['clinic_upper']={'quad':[[275,536],[350,545],[350,555],[275,546]],'size':[512,96]}
entries['clinic_lower']={'quad':[[274,573],[350,581],[350,591],[274,584]],'size':[512,96]}
entries['sushi']={'quad':[[335,602],[363,606],[363,626],[335,623]],'size':[192,160]}
entries['middle_tenants']={'quad':[[372,523],[384,523],[384,599],[372,599]],'size':[96,384]}
entries['fruit_shop_band']={'quad':[[274,611],[335,619],[335,626],[274,618]],'size':[384,64]}
# Full-resolution re-read corrects inherited 900px crop errors. Coordinates remain native pixels here.
native={
'matsukiyo':[[670,1662],[808,1681],[833,2096],[693,2071]],
'nishimura':[[826,1486],[1231,1539],[1235,1675],[831,1619]],
'hisamitsu':[[1442,986],[1742,975],[1753,1332],[1448,1340]],
'monja':[[1233,1381],[1320,1392],[1336,1685],[1250,1670]],
'sanzenri':[[1333,1491],[1434,1507],[1447,1751],[1345,1735]],
'asbi_flank':[[1342,1761],[1445,1777],[1467,2184],[1354,2164]],
'taiseido_left':[[1475,2135],[1609,2160],[1610,2221],[1477,2205]],
'taiseido_right':[[1609,2160],[1779,2124],[1780,2195],[1610,2221]],
'dmm':[[1610,1907],[1790,1879],[1790,2096],[1613,2120]],
}
for name,quad in native.items():entries[name]['quad']=[[x/sx,y/sy] for x,y in quad]
entries['rakuten']['method_override']='rakuten_boundary_landmarks.json'
entries['rakuten']['final_output_size']=[640,576]
for name,spec in entries.items():
 w,h=spec['size'];src=np.array(spec['quad'],float)*[sx,sy];dst=[(0,0),(w,0),(w,h),(0,h)];A=[];B=[]
 for (x,y),(u,v) in zip(dst,src):A.extend([[x,y,1,0,0,0,-u*x,-u*y],[0,0,0,x,y,1,-v*x,-v*y]]);B.extend([u,v])
 coeff=np.linalg.solve(A,B);out=im.transform((w,h),Image.Transform.PERSPECTIVE,coeff,Image.Resampling.BICUBIC)
 if name == 'curtain':
  # Remove broad baked sun/shadow colour from the architectural sample only; retain observed fine folds.
  a=np.asarray(out,dtype=float);illum=np.asarray(out.filter(ImageFilter.GaussianBlur(18)),dtype=float)
  a=np.clip(a/np.maximum(illum,35)*np.array([177,197,188]),0,255).astype('uint8');out=Image.fromarray(a)
 out.save(root/'textures'/f'{name}.jpg',quality=92,subsampling=0)
(root/'data/fullres_texture_sources.json').write_text(json.dumps({'source':'https://commons.wikimedia.org/wiki/File:Shibuya_crossing,_seen_from_Shibuya_Stream.jpg','author':'Syced','license':'CC0','date':'2025-01-31','original_size':im.size,'coordinate_basis':[900,1195],'entries':entries},indent=2))

# Curved Rakuten display: piecewise unwrapping follows observed top/bottom boundary; not a planar homography.
U=[0,.25,.5,.75,1]
top=[(1441,1527),(1525,1535),(1610,1530),(1695,1519),(1780,1505)]
bot=[(1453,1834),(1538,1842),(1622,1834),(1707,1820),(1792,1805)]
def xy(points,u):return tuple(np.interp(u,U,np.array(points)[:,i]) for i in (0,1))
W,H=640,576;mesh=[]
for i in range(64):
 x0,x1=i*W//64,(i+1)*W//64;u0,u1=x0/W,x1/W
 tl,bl,br,tr=xy(top,u0),xy(bot,u0),xy(bot,u1),xy(top,u1)
 mesh.append(((x0,0,x1,H),(*tl,*bl,*br,*tr)))
im.transform((W,H),Image.Transform.MESH,mesh,Image.Resampling.BICUBIC).save(root/'textures/rakuten.jpg',quality=92,subsampling=0)
(root/'data/rakuten_boundary_landmarks.json').write_text(json.dumps({'source':'WB01','original_top_landmarks':top,'original_bottom_landmarks':bot,'method':'64 strip boundary warp, approximate cylinder geometry; overrides planar rakuten entry in fullres_texture_sources.json','output_size':[W,H],'output_file':'textures/rakuten.jpg'},indent=2))
