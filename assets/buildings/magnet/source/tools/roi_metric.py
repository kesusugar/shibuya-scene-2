# Mean RGB of fixed regions in the M027 frame (photo pixels, 1280 x 1707) for the photo and a render of the same camera.
#   python3 tools/roi_metric.py refs/raw/M027.jpg renders/v1/day_m027_final.png [out.json]
# The boxes sit inside surfaces in both images; with a 16 px camera fit, values compare tone, not exact pixels.
import sys, json
from PIL import Image, ImageStat

ROI = {
    'west_wall_white': (20, 540, 170, 620),
    'drum_wrap_white': (450, 400, 530, 560),
    'tower_glass':     (575, 160, 660, 300),
    'sign_box_grey':   (690, 330, 740, 470),
    'sky':             (860, 30, 980, 180),
}
photo, render = (Image.open(p).convert('RGB').resize((1280, 1707)) for p in sys.argv[1:3])
out = {}
for k, box in ROI.items():
    a = [round(v) for v in ImageStat.Stat(photo.crop(box)).mean]; b = [round(v) for v in ImageStat.Stat(render.crop(box)).mean]
    out[k] = {'box': box, 'photo': a, 'render': b, 'delta_luma': round((0.299*b[0]+0.587*b[1]+0.114*b[2]) - (0.299*a[0]+0.587*a[1]+0.114*a[2]), 1)}
    print(f"{k:16s} photo {a}  render {b}  dLuma {out[k]['delta_luma']:+.1f}")
if len(sys.argv) > 3: json.dump(out, open(sys.argv[3], 'w'), indent=1)
