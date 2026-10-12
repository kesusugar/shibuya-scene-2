# Side-by-side boards (before | after) from evidence/c2a for the C2a report. Same camera, same settings.
#   python3 scripts/board-c2a.py evidence/c2a
import sys, os
from PIL import Image, ImageDraw, ImageFont
d = sys.argv[1]
try: F = ImageFont.truetype('/usr/share/fonts/opentype/ipafont-gothic/ipag.ttf', 22)
except OSError: F = ImageFont.load_default()
LABEL = {'c01_to_qfront': 'C01 交差点中心 → QFRONT', 'c02_to_crossing': 'C02 ハチ公口 → 交差点', 'c03_to_station': 'C03 QFRONT前 → 駅',
         'c04_to_crossing': 'C04 MAGNET前 → 交差点', 'c05_to_crossing': 'C05 センター街入口 → 交差点', 'x01_ref_a': 'X01 駅連絡通路の窓（REF-A）',
         'x02_ref_b': 'X02 渋谷ストリーム（REF-B）', 'top_down': '真上（交差点の上 190 m）', 'base_qfront_front': 'QFRONT 正面の根元',
         'base_magnet_sw': 'MAGNET 南西の根元', 'base_magnet_se': 'MAGNET 南東の根元', 'kerb_ne_corner': '北東の角の縁石',
         'm027_day': 'M027（MAGNET 写真カメラ）昼', 'm027_night': 'M027 夜', 'q032_day': 'Q032（QFRONT 写真カメラ）昼', 'q032_night': 'Q032 夜'}
os.makedirs(os.path.join(d, 'boards'), exist_ok=True)
for k, lab in LABEL.items():
    a, b = os.path.join(d, f'{k}_before.png'), os.path.join(d, f'{k}_after.png')
    if not (os.path.exists(a) and os.path.exists(b)): print('missing', k); continue
    A, B = Image.open(a).convert('RGB'), Image.open(b).convert('RGB')
    s = 640 / A.width; A = A.resize((640, int(A.height * s))); B = B.resize((640, int(B.height * s)))
    W, H = 1300, A.height + 70
    im = Image.new('RGB', (W, H), (20, 20, 22)); dr = ImageDraw.Draw(im)
    im.paste(A, (0, 40)); im.paste(B, (660, 40))
    dr.text((8, 8), f'{lab}  前（地面なし・高さ基準なし）', font=F, fill=(230, 230, 230)); dr.text((668, 8), '後（C2a：PLATEAU の地面・共通の高さ基準）', font=F, fill=(230, 230, 230))
    dr.text((8, H - 26), 'Three.js / headless SwiftShader（見た目の確認用。FPS ではない）。同じカメラ・同じ設定。', font=F, fill=(160, 160, 160))
    im.save(os.path.join(d, 'boards', f'{k}.png')); print('board', k)
