import json,numpy as np
from pathlib import Path
from scipy.optimize import least_squares
F=json.load(open(Path(__file__).resolve().parents[1]/'data/facades.json'))
def corners(center,T,w,h):
 c=np.array(center);T=np.array(T);Z=np.array([0,0,1]);return [c-T*w/2+Z*h/2,c+T*w/2+Z*h/2,c+T*w/2-Z*h/2,c-T*w/2-Z*h/2]
a=np.arctan2(3.501,31.213);T=[np.cos(a),np.sin(a),0]
def front(x,z):return [x,21.279+(x+67.253)*3.501/31.213,z]
r=F['rooftop_sign'];P=corners(r['center_m'],[np.cos(r['yaw_rad']),np.sin(r['yaw_rad']),0],r['width_m'],r['height_m']);Q=[[1438,980],[1746,969],[1758,1339],[1445,1346]]
b=F['fruit_frontage']['roof_back_panel'];P+=corners(front(b['x_m'],b['center_height_m']),T,b['width_m'],b['height_m']);Q += [[813,1175],[1239,1227],[1251,1497],[824,1446]]
b=F['fruit_frontage']['header'];P+=corners(front(b['x_m'],b['center_height_m']),T,b['width_m'],b['height_m']);Q += [[826,1486],[1231,1539],[1235,1675],[831,1619]]
P=np.array(P);Q=np.array(Q)
def project(v):
 az,el,roll,scale,tx,ty=v;D=np.array([np.sin(az)*np.cos(el),-np.cos(az)*np.cos(el),np.sin(el)]);right=np.array([np.cos(az),np.sin(az),0]);up=np.cross(D,right);xy=np.stack((P@right,-P@up),axis=1);R=np.array([[np.cos(roll),-np.sin(roll)],[np.sin(roll),np.cos(roll)]]);return xy@R.T*scale+[tx,ty]
r=least_squares(lambda v:(project(v)-Q).ravel(),[.6,.25,-.02,32,2000,2000],bounds=([.15,.03,-.1,10,-5000,-5000],[1.1,.8,.1,80,5000,5000]))
print(r.x, 'rms',np.sqrt(np.mean((project(r.x)-Q)**2)));print(project(r.x));(Path(__file__).resolve().parents[1]/'data/view_fit.json').write_text(json.dumps({'parameters':r.x.tolist(),'rms_px':float(np.sqrt(np.mean((project(r.x)-Q)**2))),'basis':'Orthographic approximate photo view from three observed sign rectangles; not geospatial recalibration'},indent=2))
