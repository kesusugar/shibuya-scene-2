"""Create factual comparison boards; photographs are resized/cropped only, with attribution."""
from pathlib import Path
import json
from PIL import Image, ImageDraw, ImageFont
root=Path('evidence/c2b');out=root/'boards';out.mkdir(exist_ok=True)
font=ImageFont.truetype('/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc',20)
small=ImageFont.truetype('/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc',17)
def board(name, tiles, size, footer):
    w,h=size;image=Image.new('RGB',(w*len(tiles),h+110),'#161d28');draw=ImageDraw.Draw(image)
    for i,(label,path,crop,measure_size) in enumerate(tiles):
        im=Image.open(path).convert('RGB')
        if measure_size: im=im.resize(measure_size,Image.Resampling.LANCZOS)
        if crop: im=im.crop(crop)
        im=im.resize((w,h),Image.Resampling.LANCZOS)
        image.paste(im,(i*w,45));draw.text((i*w+10,8),label,font=font,fill='white')
    draw.text((10,h+55),footer,font=small,fill='#e6d9b9');image.save(out/name)
board('m027_photo_before_prototype.png',[
 ('実写：2025-09-01（Taufik / CC0）','assets/buildings/magnet/source/refs/raw/M027.jpg',None,None),
 ('C3a：街路設備なし',root/'stages/before/m027_beauty.png',None,None),
 ('C2b：座標のある試作を追加',root/'selected/m027_beauty.png',None,None)],(640,853),
 '出入口候補6件・樹木6件。形状は仮。右側の樹木や信号など、写真にある未実装の物も残る。')
board('stream_photo_projection.png',[
 ('実写：2025-01-31（Syced / CC0）','assets/street/core/source/refs/stream_2025.jpg',(180,650,875,895),(900,1195)),
 ('出入口候補と樹木のみ',root/'final/stream_known.png',(180,650,875,895),(900,1195)),
 ('写真投影の仮配置（橙色）',root/'final/stream_projected.png',(180,650,875,895),(900,1195))],(695,245),
 '同じ仮カメラ。根元を地面へ投影したが、別のカメラ前提では位置が最大2.86 m変わる。確定配置には未採用。')
board('night_lighting.png',[
 ('参考実写：2024年（Syced / CC0）','evidence/c3a/refs/Shibuya_scramble_av_night_from_Stream.jpg',None,None),
 ('基準：路面発光0・街灯消灯',root/'final/night_zero.png',None,None),
 ('実験：路面発光0・街灯3基',root/'final/night_lamps.png',None,None)],(640,482),
 '同じREF-Bカメラ。比較用の仮照明。位置・高さ・1800 cdの光量は未確認。2025年の夜を検証した写真ではない。')
metrics=[]
for s in ['trees','leaves','crown','corefill']:
 metrics.append(json.loads((root/f'stages/{s}/street_metrics.json').read_text())['vegetation']['iou'])
tiles=[('実写の左側の樹木','assets/buildings/magnet/source/refs/raw/M027.jpg',(0,345,160,500),(640,853))]
for label,s,v in zip(['軽い試作（採用）','葉を細密化（非採用）','樹冠を深く（非採用）','密度を補う（非採用）'],['trees','leaves','crown','corefill'],metrics):
 tiles.append((f'{label} IoU={v:.3f}',root/f'stages/{s}/m027_beauty.png',(0,345,160,500),(640,853)))
board('tree_trials.png',tiles,(320,310),
 '同じカメラ・樹木座標。IoUは写真の葉と描画の葉の近似マスクで計測し、未実装の右側の樹木も含む。実写：Taufik / CC0。')
board('overview.png',[
 ('通常表示：地図座標を使う試作',root/'final/overview_known.png',None,None),
 ('比較用：仮配置の支柱・標識・柵',root/'final/overview_projected.png',None,None)],(800,600),
 '橙色は位置・形状の確認待ち。全設備の再現や、写真品質の合格を示す画像ではない。')
print('boards',len(list(out.glob('*.png'))))
