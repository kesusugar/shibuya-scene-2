"""Before (?sky=flat&detail=off&ao=off) | after, same camera. python3 scripts/look-foundation-boards.py"""
import os
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont
F = next(p for p in ('/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc', '/usr/share/fonts/opentype/ipafont-gothic/ipagp.ttf') if os.path.exists(p))
font, small = ImageFont.truetype(F, 20), ImageFont.truetype(F, 17)
R = Path('evidence/look-foundation'); (R / 'boards').mkdir(exist_ok=True)
NOTE = {'west_eye': '交差点中央の目線。空のグラデーションと遠景のかすみ、路面のムラ、外壁の汚れ筋、壁の足元の陰。',
        'plaza_se': '広場から駅側。歩道の目地（0.30 m）とムラ、建物の足元の陰。',
        'station_front': '交差点から駅側。', 'statue_side': 'ハチ公像の横。像の足元・植え込みの陰。',
        'stream': 'Stream からの高所。遠景がかすみ、奥行きが出る。', 'ekimae_eye': '目線で駅前ビル方向。',
        'entry_night': '夜の初期画面。夜空のグラデーション（夜の路面・看板は変えていない）。'}
for name, note in NOTE.items():
    a, b = Image.open(R / 'before' / f'{name}.png').convert('RGB'), Image.open(R / 'after' / f'{name}.png').convert('RGB')
    w, h = a.size; board = Image.new('RGB', (w * 2, h + 90), '#151922'); d = ImageDraw.Draw(board)
    board.paste(a, (0, 45)); board.paste(b, (w, 45))
    d.text((10, 10), '前：単色の空・質感なし・陰なし', font=font, fill='white'); d.text((w + 10, 10), '後：見た目の土台', font=font, fill='white')
    d.text((10, h + 55), note + '　同じカメラ・既定品質（SwiftShader）。', font=small, fill='#e6d9b9')
    board.save(R / 'boards' / f'{name}.png'); print('board', name)
