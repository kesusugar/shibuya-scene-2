"""Same-camera boards for the C2b fix: [photo] | Codex v1 (before) | v2 (after). python3 scripts/c2b-fix-boards.py"""
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont
import os
F = next(p for p in ('/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc', '/usr/share/fonts/opentype/ipafont-gothic/ipagp.ttf') if os.path.exists(p))
font, small = ImageFont.truetype(F, 20), ImageFont.truetype(F, 17)
root = Path('evidence/c2b-fix'); out = root / 'boards'; out.mkdir(parents=True, exist_ok=True)
PHOTOS = {'m027': ('実写 2025-09-01（Taufik / CC0）', 'assets/buildings/magnet/source/refs/raw/M027.jpg'),
          'stream': ('実写 2025-01-31（Syced / CC0）', 'assets/street/core/source/refs/stream_2025.jpg')}
NOTES = {
    'm027': 'MAGNET 前。右端の信号の腕木（R2）と柵が増えた。写真右側の樹木は OSM になく未配置。',
    'stream': 'Stream からの高所。信号・柵・街灯が入った。カメラは Codex の仮カメラ（位置未検証）。',
    'overview': '俯瞰。出入口はガラス張りの箱に、樹木は大きく、信号の腕木と縁石の柵が入った。',
    'ne_corner': '目線。南西の島から北東の角を見る。',
    'sw_island': '目線。北の横断歩道から南西の島（街灯・標識・出入口）を見る。',
    'hachiko': '目線。駅側から北西を見る。',
    'night': '夜（REF-B の高所カメラ）。街灯 3 基を通常表示で点灯。',
    'night_street': '夜の目線。街灯の下の路面。',
}
for name, note in NOTES.items():
    b, a = root / 'before' / f'{name}.png', root / 'after' / f'{name}.png'
    if not (b.exists() and a.exists()):
        print('skip', name); continue
    tiles = []
    if name in PHOTOS:
        label, p = PHOTOS[name]; tiles.append((label, Image.open(p).convert('RGB')))
    tiles += [('前：Codex C2b（PR #8）', Image.open(b).convert('RGB')), ('後：作り直し（v2）', Image.open(a).convert('RGB'))]
    w, h = Image.open(a).size
    tiles = [(l, im.resize((w, h))) for l, im in tiles]
    board = Image.new('RGB', (w * len(tiles), h + 90), '#151922'); d = ImageDraw.Draw(board)
    for i, (l, im) in enumerate(tiles):
        board.paste(im, (i * w, 45)); d.text((i * w + 10, 8), l, font=font, fill='white')
    d.text((10, h + 55), note + '　同じカメラ・同じ時刻。仮の位置と形を含む。', font=small, fill='#e6d9b9')
    board.save(out / f'{name}.png'); print('board', name)
