"""C2b geometry and vegetation checks. These are measurements, not a quality gate.
Usage: python scripts/street-metrics.py evidence/c2b/stages/trees out.json
Photo mask: HSV-filtered manually bounded regions; pedestrians/occlusion and camera error remain limitations.
"""
import json, math, sys
from pathlib import Path
import numpy as np
from PIL import Image, ImageDraw

stage, out = map(Path, sys.argv[1:3])
D = json.loads(Path('assets/street/core/source/data/photo_projections.json').read_text())
C = D['camera']; y, p, r = map(math.radians, (C['yaw'], C['pitch'], C['roll']))
fwd = np.array([math.sin(y)*math.cos(p), math.cos(y)*math.cos(p), math.sin(p)])
r0 = np.array([math.cos(y), -math.sin(y), 0]); u0 = np.cross(r0, fwd)
right = r0*math.cos(r)-u0*math.sin(r); up = u0*math.cos(r)+r0*math.sin(r)
f = C['H']/2/math.tan(math.radians(C['vfov'])/2)
def project(v):
    d = np.array(v)-C['pos']; depth = d@fwd
    return np.array([C['W']/2+f*(d@right)/depth, C['H']/2-f*(d@up)/depth])
heads = []
for row in D['observations']:
    if 'head_px' not in row or 'point' not in row: continue
    xy = row['point']; z = row['anchor_tp']-15
    px = project([*xy, z+row['height_m']])
    heads.append({'id': row['id'], 'height_m': row['height_m'], 'observed_px': row['head_px'],
                  'model_pole_top_px': px.round(2).tolist(), 'error_px': round(float(np.linalg.norm(px-row['head_px'])), 2),
                  'pixel_sensitivity_m': row['pixel_error_ground_radius_m']})
mask_img = Image.open(stage/'m027_class.png').convert('RGB'); w,h = mask_img.size
photo = Image.open('assets/buildings/magnet/source/refs/raw/M027.jpg').convert('RGB').resize((w,h))
# Region coordinates are in the original 1280x1707 M027 image; right-hand tree is deliberately included even if absent in the model.
regions = [[(0,750),(64,737),(130,782),(202,736),(279,776),(273,885),(233,939),(62,980),(0,962)],
           [(760,840),(822,810),(974,812),(1048,896),(1026,999),(900,1050),(812,1014),(770,958)]]
roi_img = Image.new('1',(w,h)); draw = ImageDraw.Draw(roi_img)
for polygon in regions: draw.polygon([(x*w/1280,y*h/1707) for x,y in polygon],fill=1)
hsv = np.array(photo.convert('HSV'))/255; roi=np.array(roi_img,dtype=bool)
reference=roi&(hsv[:,:,0]>.12)&(hsv[:,:,0]<.46)&(hsv[:,:,1]>.19)&(hsv[:,:,2]>.10)&(hsv[:,:,2]<.85)
classes = np.array(mask_img)
render_hsv = np.array(Image.open(stage/'m027_beauty.png').convert('HSV'))/255
# The vegetation class includes bark: use the same green-leaf filter on the render to avoid comparing trunks with photo foliage.
predicted=np.all(classes==[0,128,0],axis=2)&(render_hsv[:,:,0]>.12)&(render_hsv[:,:,0]<.46)&(render_hsv[:,:,1]>.19)&(render_hsv[:,:,2]>.10)&(render_hsv[:,:,2]<.85)
intersection=int((reference&predicted).sum()); union=int((reference|predicted).sum())
raw_class = np.all(classes==[0,128,0],axis=2)
def lab(rgb):
    c = rgb / 255
    c = np.where(c <= .04045, c/12.92, ((c+.055)/1.055)**2.4)
    xyz = c @ np.array([[.4124,.3576,.1805],[.2126,.7152,.0722],[.0193,.1192,.9505]]).T / [.95047,1,1.08883]
    f = np.where(xyz>.008856,np.cbrt(xyz),7.787*xyz+16/116)
    return np.stack([116*f[...,1]-16,500*(f[...,0]-f[...,1]),200*(f[...,1]-f[...,2])],-1)
photo_lab=lab(np.array(photo,dtype=float))[reference].mean(axis=0)
render_lab=lab(np.array(Image.open(stage/'m027_beauty.png').convert('RGB'),dtype=float))[predicted].mean(axis=0)

metrics={'photo':'M027', 'resolution':[w,h], 'mask_method':'manual regions plus HSV filter; approximate, not hand-segmented ground truth',
         'reference_regions_original_px':regions, 'render_mask_method':'vegetation class intersected with the same HSV leaf-colour filter; bark excluded',
         'reference_pixels':int(reference.sum()),'render_pixels':int(predicted.sum()),
         'intersection_pixels':intersection,'iou':round(intersection/union,4),
         'reference_recall':round(intersection/reference.sum(),4),'render_precision':round(intersection/max(1,predicted.sum()),4),
         'photo_leaf_mean_Lab':photo_lab.round(2).tolist(),'render_leaf_mean_Lab':render_lab.round(2).tolist(),
         'leaf_mean_delta_Lab':(render_lab-photo_lab).round(2).tolist(),
         'class_vs_photo_leaf_iou':round(float((reference&raw_class).sum()/(reference|raw_class).sum()),4),
         'unmodelled_right_tree_included':True,'camera_rms_original_px':11.38869}
visual=np.zeros((h,w,3),dtype=np.uint8); visual[reference]=[255,80,80];visual[predicted]=[80,180,255];visual[reference&predicted]=[255,255,255]
Image.fromarray(visual).save(stage/'m027_vegetation_overlap.png')
result={'pole_heads':heads,'vegetation':metrics,'limitations':['Pole heads use the same provisional camera as placement: not independent position validation.',
 'Pixel sensitivity is not a confidence interval for whole-camera uncertainty.', 'Tree masks are approximate; people, buildings and camera error affect their edges.']}
out.parent.mkdir(parents=True,exist_ok=True);out.write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n')
print(json.dumps(result,ensure_ascii=False,indent=2))
