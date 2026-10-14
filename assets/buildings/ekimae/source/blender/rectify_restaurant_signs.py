"""Rectify full-height facade faces FIRST, then slice restaurant floors.
Shared physical corner and vertical correspondence across 9F/8F/7F prevent
independent per-floor shearing. All pixels are licensed EK01 photographs.
"""
from pathlib import Path
import json,numpy as np
from PIL import Image
FACES={
 'front':[[420,660],[800,750],[715,1010],[320,934]],
 'return':[[800,750],[1000,848],[930,1073],[715,1010]]}
BANDS=[('shabu',27.7,31.0),('francais',24.35,27.7),('gusto',21.15,24.35)]
def warp(im,quad,size):
 w,h=size;dst=[(0,0),(w,0),(w,h),(0,h)];a=[];b=[]
 for (x,y),(u,v) in zip(dst,quad):a.extend([[x,y,1,0,0,0,-u*x,-u*y],[0,0,0,x,y,1,-v*x,-v*y]]);b.extend([u,v])
 return im.transform(size,Image.Transform.PERSPECTIVE,np.linalg.solve(a,b),Image.Resampling.BICUBIC)
def rectify(path):
 root=Path(__file__).resolve().parents[1];im=Image.open(path).convert('RGB');assert im.size==(4032,2268);cfg=json.loads((root/'data/facades.json').read_text())
 # Both full-height face quads share the exact same central physical corner.
 # The 2:1 developed-width ratio is inferred; no independent horizontal shifts by floor.
 whole=Image.new('RGB',(1024,768));whole.paste(warp(im,FACES['front'],(682,768)),(0,0));whole.paste(warp(im,FACES['return'],(342,768)),(682,0))
 details=[]
 # After full-face rectification, straighten floor borders in Y only.
 # X/U is NEVER shifted per floor: the same mullions remain at the same station.
 row_edges=[[0,0,0],[260,240,260],[505,480,510],[768,768,768]]
 def edge_y(edge,x):
  a,b=(0,1) if x<=682 else (1,2);xs=[0,682,1024];t=(x-xs[a])/(xs[b]-xs[a]);return edge[a]*(1-t)+edge[b]*t
 for bi,(name,z0,z1) in enumerate(BANDS):
  mesh=[]
  for x0 in range(0,1024,32):
   x1=x0+32;t0=edge_y(row_edges[bi],x0);t1=edge_y(row_edges[bi],x1);b0=edge_y(row_edges[bi+1],x0);b1=edge_y(row_edges[bi+1],x1)
   mesh.append(((x0,0,x1,256),(x0,t0,x0,b0,x1,b1,x1,t1)))
  whole.transform((1024,256),Image.Transform.MESH,mesh,Image.Resampling.BICUBIC).save(root/'textures'/f'{name}.png',optimize=True)
  details.append({'name':name,'z0':z0,'z1':z1,'rectified_upper_y_at_u_knots':row_edges[bi],'rectified_lower_y_at_u_knots':row_edges[bi+1]})
 cfg['restaurant_alignment']={'source':'EK01 4032x2268, Joli Rumi,2025-11-01,CC BY-SA4.0','method':'Two full-height facade-plane projective rectifications first, sharing exact central corner, then Y-only floor-edge straightening with fixed common U stations. No independent horizontal shifts by floor.','face_quads_px':FACES,'central_corner_px':[[800,750],[715,1010]],'full_stack_size':[1024,768],'face_split_u':682/1024,'bands':details,'geometry':'No generic uprights across continuous advertising; outer floor strips only. Physical facade widths/curvature and floor heights inferred.'};(root/'data/facades.json').write_text(json.dumps(cfg,ensure_ascii=False,indent=2)+'\n')
if __name__=='__main__':
 import sys;rectify(sys.argv[1])
