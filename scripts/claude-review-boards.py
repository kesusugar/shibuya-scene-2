"""Boards for the Claude review of PR #12-#36: reference photo | before (Codex) | after (Claude), same camera."""
import os
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont
F = next(p for p in ('/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc', '/usr/share/fonts/opentype/ipafont-gothic/ipagp.ttf') if os.path.exists(p))
font, small = ImageFont.truetype(F, 20), ImageFont.truetype(F, 17)
import sys
R = Path(sys.argv[1] if len(sys.argv) > 1 else 'evidence/claude-review')


def crop(path, box=None, size=None):
    if not Path(path).exists(): return None   # board of the other round
    im = Image.open(path).convert('RGB')
    if box: im = im.crop(box)
    return im


BOARDS_1 = [
    ('west_corner', [('写真 2025-01（Syced / CC0）', crop('assets/street/core/source/refs/stream_2025.jpg', (400, 200, 1386, 1700))),
                     ('前：Codex', crop(R / 'before/stream.png', (150, 75, 520, 640))), ('後：Claude', crop(R / 'after/stream.png', (150, 75, 520, 640)))],
     '大盛堂書店ビルの角：赤い円筒 → 灰色の金属外装（赤はクスリの細い面と庇だけ）。楽天とDMMの間に横ルーバー、Hisamitsu看板の下を鉄骨トラスに。'),
    ('west_eye', [('前：Codex', crop(R / 'before/west_eye.png')), ('後：Claude', crop(R / 'after/west_eye.png'))],
     '交差点中央からの目線。同じ変更。看板画像・寸法・位置は変えていない。'),
    ('concourse', [('写真 2025-10-18（ウィ貴公子 / CC BY-SA 4.0）', crop('docs/core/station_glazing_refs/oct2025_8427.jpg', (300, 520, 960, 800))),
                   ('前：Codex', crop(R / 'before/concourse.png', (150, 180, 760, 500))), ('後：Claude', crop(R / 'after/concourse.png', (150, 180, 760, 500)))],
     '駅の連絡通路の北面：ガラス帯 3.8 m → 8.5 m（写真で正面の約65%）、上部の無地壁を銀色の帯に。屋根・床・開口は不変。'),
    ('statue_front', [('写真 2025-07-13（RuinDig/Yuki Uchida / CC BY 4.0）', crop('assets/street/hachiko/source/refs/july095.jpg', (0, 600, 3072, 3700))),
                      ('前：Codex', crop(R / 'before/statue_front.png')), ('後：Claude', crop(R / 'after/statue_front.png'))],
     'ハチ公像：緑黒の像 → 茶色の青銅（写真の脚の色）、尖った葉 → 松の丸い房、自然石を大きく。配置・寸法は不変。'),
    ('statue_side', [('前：Codex', crop(R / 'before/statue_side.png')), ('後：Claude', crop(R / 'after/statue_side.png'))], '同じ変更を横から。'),
    ('shibuya109', [('写真 2019（Kakidai / CC BY-SA 4.0）', crop('assets/buildings/shibuya109/source/refs/reference.jpg')),
                    ('前：Codex', crop(R / 'before/b109_street.png')), ('後：Claude', crop(R / 'after/b109_street.png'))],
     '109：白い塗り壁 → 銀色の金属パネル（材質だけ。形・目地・接地は不変）。'),
]
BOARDS = BOARDS_1
BOARDS_2 = [
    ('corner_box', [('写真 2025-02（Syced / CC0）', crop('docs/core/building_refs/crossing_12214.jpg', (540, 40, 760, 360))),
                    ('前（第1回の後）', crop(R / 'before/stream.png', (280, 180, 480, 560))), ('後', crop(R / 'after/stream.png', (280, 180, 480, 560)))],
     '大盛堂ビル：楽天の上を円筒の頂部→灰色の箱（画面の筐体）に、DMMを曲面→黒い枠の平らな画面に。'),
    ('corner_eye', [('前（第1回の後）', crop(R / 'before/west_eye.png')), ('後', crop(R / 'after/west_eye.png'))], '同じ変更を交差点中央の目線で。'),
    ('gate', [('写真 2025-01（Syced / CC0）', crop('assets/street/core/source/refs/stream_2025.jpg', (1100, 1250, 1360, 1430))),
              ('前：Codex', crop(R / 'before/gate.png')), ('後', crop(R / 'after/gate.png'))],
     'センター街ゲート：黒い連続アーチ＋黄色の曲面板 → 先が内側へ曲がる灰色の支柱2本＋平らな横断幕（2025年1月の写真から切り出し、別レイヤー）。'),
    ('station_plaza', [('写真 2025-11-01（Joli Rumi / CC BY-SA 4.0）', crop('assets/street/hachiko/source/refs/hachiko.jpg', (0, 0, 2400, 1350))),
                       ('前：Codex', crop(R / 'before/plaza_se.png')), ('後', crop(R / 'after/plaza_se.png'))],
     '広場から駅側：無地の灰色壁 → 白い仮囲い・足場・10月の広告（駅西側の小施設）、縦ルーバーの設備箱と仮囲い（JR北側）。'),
    ('station_front', [('前：Codex', crop(R / 'before/station_front.png')), ('後', crop(R / 'after/station_front.png'))], '交差点から駅側。同じ変更。'),
]
if R.name == 'claude-review-2': BOARDS = BOARDS_2
for name, tiles, note in BOARDS:
    if any(im is None for _, im in tiles): continue
    h = 640
    tiles = [(l, im.resize((max(1, round(im.width * h / im.height)), h))) for l, im in tiles]
    W = sum(im.width for _, im in tiles)
    board = Image.new('RGB', (W, h + 95), '#151922'); d = ImageDraw.Draw(board); x = 0
    for l, im in tiles:
        board.paste(im, (x, 45)); d.text((x + 10, 10), l, font=font, fill='white'); x += im.width
    d.text((10, h + 58), note + '　前後は同じカメラ・既定品質（SwiftShader）。', font=small, fill='#e6d9b9')
    board.save(R / 'boards' / f'{name}.png'); print('board', name, board.size)
