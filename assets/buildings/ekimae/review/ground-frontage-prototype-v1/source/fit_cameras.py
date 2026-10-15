"""Conditional perspective camera fits, held-out residuals. No photos copied or bundled."""
import numpy as np,json,math
from scipy.optimize import least_squares
from pathlib import Path
R=Path(__file__).resolve().parents[1]
def project(par,pts,size):
 cu,cd,ch,yaw,pitch,roll,fl=par;f=np.array([math.sin(yaw)*math.cos(pitch),-math.cos(yaw)*math.cos(pitch),math.sin(pitch)]);r=np.array([math.cos(yaw),math.sin(yaw),0]);down=np.cross(r,f);rr=math.cos(roll)*r+math.sin(roll)*down;dd=-math.sin(roll)*r+math.cos(roll)*down
 X=np.array(pts)-[cu,cd,ch];z=X@f
 return np.stack([size[0]/2+fl*(X@rr)/z,size[1]/2+fl*(X@dd)/z],axis=1)
def fit(name,size,pts,pix,held,initial,notes):
 pts=np.array(pts);pix=np.array(pix)
 results=[]
 for start in [initial,[1,5,1.6,.25,.35,0,900],[-2,6,1.6,-.3,.4,0,1000],[4,8,1.6,.3,.3,0,1000]]:
  results.append(least_squares(lambda p:(project(p,pts,size)-pix).ravel(),start,bounds=([-15,.5,1.2,-1.2,-.1,-.15,500],[15,30,1.9,1.2,.9,.15,2200]),max_nfev=3000))
 result=min(results,key=lambda a:np.sum(a.fun**2))
 out={'pixel_size':size,'camera_local_u_d_h_yaw_pitch_roll_focal':result.x.tolist(),'fitted_points':[{'model':m.tolist(),'pixel':p.tolist(),'prediction':q.tolist()} for m,p,q in zip(pts,pix,project(result.x,pts,size))],'fit_RMS_px_not_validation':float(np.sqrt(np.mean((project(result.x,pts,size)-pix)**2))),'held_out':[], 'limitations':notes}
 for label,m,observed in held:
  predicted=project(result.x,[m],size)[0];err=np.linalg.norm(predicted-observed);out['held_out'].append({'label':label,'model':m,'observed':observed,'predicted':predicted.tolist(),'error_px':float(err)})
 out['held_out_RMS_radial_px']=float(np.sqrt(np.mean([v['error_px']**2 for v in out['held_out']])))
 return out
# Four approximate upper glazing corners fit the north facade plane. Ground anchors remain wholly held-out.
view24=fit('daylight2024',[1200,900],[[.474373,.207771,6.55],[5.464777,.207771,6.55],[5.464777,.207771,3.45],[.474373,.207771,3.45]],[[390,295],[875,275],[900,520],[377,535]], [('display right base',[1.20,.1,.145],[481,866]),('entry right base',[3.2,.1,.035],[691,868]),('pale pier right base',[3.7,.115,0],[745,879]),('upper next-floor corner',[.474373,.207771,10],[408,60])],[-1,10,1.5,.1,.15,0,1000],['Upper modeled width/height inherited and not surveyed','No lens distortion or calibrated focal metadata; street camera height constrained1.2..1.9m','Fit anchors approximate; ground coplanarity unverified','Four fitted corners are not held-out validation'])
# Close image has cropped upper endpoints. Fit ONLY outer enclosure, retain inner sidelights/transom corners as held-out.
view25=fit('close2025',[984,1280],[[1.20,.1,.145],[1.2,.1,2.69],[3.2,.1,2.69],[3.2,.1,.035]],[[514,1195],[520,750],[920,750],[941,1195]], [('plant turning corner base',[0,.1,.145],[310,1205]),('left inner frame base',[1.58,.1,.105],[600,1195]),('right inner frame base',[2.82,.1,.105],[840,1195]),('left inner frame head',[1.58,.1,2.36],[600,805]),('right inner frame head',[2.82,.1,2.36],[840,805])],[1.6,5,1.4,0,.1,0,1000],['Close photo crops upper facade endpoints, so independent upper-plane fit is unavailable','Camera fit uses ground outer-frame points; only interior subdivisions are held out','Physical depth is unidentifiable from these coplanar fit points','This is a conditional comparison camera, NOT surveyed photogrammetry'])
import copy
alternative=copy.deepcopy(view24)
alternative['camera_local_u_d_h_yaw_pitch_roll_focal']=[2.866913345084571,8.454639500638699,1.2000000000000002,-.05880679453650675,.3693621473983053,.009843543089333771,818.9100965537552]
for entry in alternative['fitted_points']:
 if entry['model'][0]<1:entry['model'][0]=0
 entry['prediction']=project(alternative['camera_local_u_d_h_yaw_pitch_roll_focal'],[entry['model']],[1200,900])[0].tolist()
for entry in alternative['held_out']:
 entry['predicted']=project(alternative['camera_local_u_d_h_yaw_pitch_roll_focal'],[entry['model']],[1200,900])[0].tolist()
 entry['error_px']=float(np.linalg.norm(np.array(entry['predicted'])-entry['observed']))
alternative['fit_RMS_px_not_validation']=float(np.sqrt(np.mean([(np.array(e['prediction'])-e['pixel'])**2 for e in alternative['fitted_points']])))
alternative['held_out_RMS_radial_px']=float(np.sqrt(np.mean([e['error_px']**2 for e in alternative['held_out']])))
alternative['ground_only_RMS_radial_px']=float(np.sqrt(np.mean([e['error_px']**2 for e in alternative['held_out'][:3]])))
alternative['limitations']=['SOURCECORNER ALTERNATIVE: virtual calibration plane begins at sourceB/u0, not actual generated upper arc endpoint','Actual asset upper geometry is NOT changed to this virtual correspondence','Ground-only RMS32.5px improves on original assumption but is NOT wholemodel validation','Hand-picked corner perturbations make aspect/focal ill-conditioned; no proof upper geometry is wrong']
(R/'evidence/photo-camera-fit.json').write_text(json.dumps({'2024':view24,'2025':view25,'sourcecorner2024':alternative},indent=2))
print({k:{'fit':v['fit_RMS_px_not_validation'],'held':v['held_out_RMS_radial_px'],'camera':v['camera_local_u_d_h_yaw_pitch_roll_focal']} for k,v in [('2024',view24),('2025',view25)]})
