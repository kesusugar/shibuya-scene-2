"""Same-camera boards for the C-level context: [photo] | without (?context=off) | with. python3 scripts/c1-context-boards.py"""
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont
import os
F = next(p for p in ('/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc', '/usr/share/fonts/opentype/ipafont-gothic/ipagp.ttf') if os.path.exists(p))
font, small = ImageFont.truetype(F, 20), ImageFont.truetype(F, 17)
root = Path('evidence/c1-context'); out = root / 'boards'; out.mkdir(parents=True, exist_ok=True)
PHOTOS = {'m027': ('実写 2025-09-01（Taufik / CC0）', 'assets/buildings/magnet/source/refs/raw/M027.jpg'),
          'stream': ('実写 2025-01-31（Syced / CC0）', 'assets/street/core/source/refs/stream_2025.jpg')}
NOTES = {
    'm027': 'MAGNET 前。奥の建物が入った（C 段階：PLATEAU の形と共通の外壁）。',
    'stream': 'Stream からの高所。センター街側の街区が入った。看板・ビジョンはまだない。',
    'overview': '俯瞰。交差点の周りの空白が埋まった。',
    'ne_corner': '目線。南西の島から北東の角。',
    'sw_island': '目線。北の横断歩道から南西の島。',
    'hachiko': '目線。駅側から北西。',
    'night': '夜（REF-B の高所カメラ）。窓が弱く光る。',
}
for name, note in NOTES.items():
    b, a = root / 'before' / f'{name}.png', root / 'after' / f'{name}.png'
    if not (b.exists() and a.exists()):
        print('skip', name); continue
    tiles = []
    if name in PHOTOS:
        label, p = PHOTOS[name]; tiles.append((label, Image.open(p).convert('RGB')))
    tiles += [('前：周辺の建物なし', Image.open(b).convert('RGB')), ('後：C 段階 308 棟', Image.open(a).convert('RGB'))]
    w, h = Image.open(a).size
    tiles = [(l, im.resize((w, h))) for l, im in tiles]
    board = Image.new('RGB', (w * len(tiles), h + 90), '#151922'); d = ImageDraw.Draw(board)
    for i, (l, im) in enumerate(tiles):
        board.paste(im, (i * w, 45)); d.text((i * w + 10, 8), l, font=font, fill='white')
    d.text((10, h + 55), note + '　同じカメラ・同じ時刻。仮の位置と形を含む。', font=small, fill='#e6d9b9')
    board.save(out / f'{name}.png'); print('board', name)
