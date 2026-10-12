"""Same-camera photo | before | after boards; python3 scripts/board-c3a.py [evidence/c3a].

Photos are resized only, never retouched. Sources and licences are recorded in
docs/core/C3A_REFERENCE_REGISTER.csv and evidence/c3a/refs/licences.json.
"""
import json
import sys
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

root = Path(sys.argv[1] if len(sys.argv) > 1 else 'evidence/c3a')
before = root / 'validation/base'
after = root / 'final'
out = root / 'boards'
out.mkdir(parents=True, exist_ok=True)
font_path = '/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc'
font = ImageFont.truetype(font_path, 22)
small = ImageFont.truetype(font_path, 17)
refs = json.loads((after / 'metrics.json').read_text())['refs']
titles = {'m027': '昼・MAGNET（M027、写真は2025年）',
          'q032': '昼・QFRONT（Q032、写真は2018年：形・材質の参考）',
          'refa': '昼・駅連絡通路（REF-A、写真は2010年）',
          'refb': '夜・渋谷ストリーム（REF-B、写真は2024年）'}
for name, title in titles.items():
    paths = [Path(refs[name]['photo']), before / f'{name}_beauty.png', after / f'{name}_beauty.png']
    rendered = Image.open(paths[-1])
    size = rendered.size
    images = [Image.open(p).convert('RGB').resize(size, Image.Resampling.LANCZOS) for p in paths]
    w, h = size
    canvas = Image.new('RGB', (w * 3 + 32, h + 228), '#151519')
    draw = ImageDraw.Draw(canvas)
    draw.text((12, 5), title, font=font, fill='white')
    for i, (label, im) in enumerate(zip(['写真', '前：引き継ぎ時の既定値', '後：C3a 採用値'], images)):
        x = 8 + i * (w + 8)
        draw.text((x, 39), label, font=font, fill='white')
        canvas.paste(im, (x, 73))
    draw.text((12, h + 81), f"写真: {refs[name]['licence']} / 出典・条件は C3A_REFERENCE_REGISTER.csv。縮小・並置のみ。", font=small, fill='#dddddd')
    note = 'REF-B はカメラ位置に20〜40pxのずれ。夜の路面は街灯を入れるまでの仮の値。' if name == 'refb' else (
        'REF-A はカメラ位置に20〜40pxのずれ。写真内の別の物が区分に混ざるため判断は限定的。' if name == 'refa' else
        '同じカメラ・同じ描画設定。古い年代の看板・広告は2025年の根拠にしない。')
    draw.text((12, h + 107), note, font=small, fill='#dddddd')
    draw.text((12, h + 134), 'SwiftShader は見た目の比較用。FPS・実機GPU性能の評価ではない。', font=small, fill='#aaaaaa')
    source = 'https://commons.wikimedia.org/wiki/File:' + paths[0].name
    if name == 'm027':
        source = 'https://commons.wikimedia.org/wiki/File:Shibuya_Crossing_20250901_131850.jpg'
    elif name == 'q032':
        source = 'https://commons.wikimedia.org/wiki/File:Q-Front_2018.jpg'
    draw.text((12, h + 160), source, font=small, fill='#aaaaaa')
    if name == 'q032':
        draw.text((12, h + 187), '写真パネル: CC BY-SA 4.0 https://creativecommons.org/licenses/by-sa/4.0/ （Kakidai、縮小・並置）', font=small, fill='#aaaaaa')
    elif name == 'refa':
        draw.text((12, h + 187), '写真: Dick Johnson / CC BY 2.0 https://creativecommons.org/licenses/by/2.0/ （縮小・並置）', font=small, fill='#aaaaaa')
    canvas.save(out / f'{name}_photo_before_after.png')
    print(out / f'{name}_photo_before_after.png')
