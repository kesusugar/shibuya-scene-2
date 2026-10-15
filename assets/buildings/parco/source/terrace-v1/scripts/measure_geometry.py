from pathlib import Path
import json,math,hashlib
from PIL import Image,ImageDraw,ImageFont
import numpy as np
ROOT=Path(__file__).resolve().parents[1];L=json.loads((ROOT/'geometry/layout.json').read_text());V=ROOT/'verification'
def area(poly):return abs(sum(a[0]*b[1]-a[1]*b[0] for a,b in zip(poly,poly[1:]+poly[:1])))/2
s=L['core_south_stair'];run=float(np.linalg.norm(np.array(s['end'])-s['start']));report={'candidate_sha256':hashlib.sha256((ROOT/'parco_terrace_candidate.glb').read_bytes()).hexdigest(),'levels':L['levels'],'inferred_oneF_TP_range_m':[24.778,25.778],'clearances_m':{'east4F_to_soffit':34.7-25.378,'corner4F_to_soffit':39.3-25.378,'north5F_to_soffit':39.3-30.178,'under5F_walkway':30.178-.30-25.378},'slab_plan_areas_m2':{key:area(L[key]) for key in ['east_floor_polygon','corner_floor_polygon','core_polygon','north_fiveF_polygon','core_west_fiveF_walkway']},'area_limit':'Component footprint areas; overlapping/interior core and under-walkway regions are included. Do not sum as net usable exterior area.','core_south_stair':{'run_m':run,'rise_m':s['rise'],'risers':s['steps'],'riser_m':s['rise']/s['steps'],'tread_run_m':run/s['steps'],'width_m':s['width'],'pitch_degrees':math.degrees(math.atan(s['rise']/run)),'status':'Inferred geometry; not a certified as-built stair or code-compliance model.'},'registration_uncertainty_m':{'core_corner_approx':1,'local_schematic_approx':1.5},'normal_ray_sample_depths_m':{'east_main_shopfront':[8.589,10.688],'east_south_return':11.505,'east_throat_sample':15.274,'corner_core':[3.417,5.075],'north':[2.272,6.445]},'independent_dense_max_cross_throat_depths_m':{'face171':20.2536401,'face108':21.4641195,'interpretation':'Oblique crossings through the wider south-of-core throat to stepped rear shopfront; not uniform terrace widths.'},'section_8_to9m_limit':'Estimated along structural-x section direction, exact transverse cut unknown. It is not a uniform facade-normal setback.'}
(V/'measurements.json').write_text(json.dumps(report,indent=2)+'\n')
# Original clean vector-like geometry plot, with no reference bitmap.
im=Image.new('RGB',(1500,1150),'white');d=ImageDraw.Draw(im);fontpath='/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf'
def font(n):
 try:return ImageFont.truetype(fontpath,n)
 except OSError:return ImageFont.load_default(size=n)
# TargetedNE plan: worldx[-151,-105], worldy[269,310].
def p(q):return (90+(q[0]+151)*26,100+(310-q[1])*23)
for key,col in [('east_floor_polygon',(228,232,236)),('corner_floor_polygon',(228,232,236)),('north_fiveF_polygon',(180,192,204)),('core_west_fiveF_walkway',(180,192,204)),('core_polygon',(125,145,160))]:d.polygon([p(q)for q in L[key]],fill=col,outline=(30,45,60))
for z,col in zip(L['zones'],[(170,45,35),(150,40,150),(30,120,70)]):d.line([p(z['a']),p(z['b'])],fill=col,width=5)
d.line([p(q)for q in L['shopfront_polyline']],fill=(30,55,75),width=5)
# Draw selected ray from exact finalgeometry report.
rays=json.loads((V/'raycast-depth.json').read_text())['raycast_tests']
for row in rays:
 if (row['face'],row['u_m'],row['z']) not in [(171,10,27.5),(108,7,27.5),(152,6,27.5),(152,16,32.5)]:continue
 z=next(v for v in L['zones']if v['face']==row['face']);a=np.array(z['a']);tt=(np.array(z['b'])-a)/z['length'];start=a+tt*row['u_m'];end=row['hit_xyz'][:2];x,y=p(start);xx,yy=p(end);d.line((x,y,xx,yy),fill=(170,70,20),width=3);d.text(((x+xx)/2,(y+yy)/2),f"{row['first_hit_inward_depth_m']:.2f}m",font=font(23),fill=(130,45,10))
d.text((65,20),'Registered terrace geometry plan / fixed source footprint',font=font(33),fill='black')
d.text((65,65),'Dark: retained lift core | Light:4F slabs | Blue-grey:5F route | Red/purple/green:171/108/eastern152',font=font(22),fill='black')
d.text((70,1060),'Measured depths belong to this inferred geometry. Core/corner registration~1m; local schematic uncertainty~1.5m.',font=font(22),fill='black')
d.text((70,1100),'The broad south-of-core throat has longer cross-rays20–21m. No uniform8m extrusion. No copyrighted bitmap.',font=font(22),fill='black');im.save(ROOT/'renders/geometry-plan-depths.png')
print('Measurements saved')
