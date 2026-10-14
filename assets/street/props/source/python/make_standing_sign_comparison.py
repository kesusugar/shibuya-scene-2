"""Evidence contact sheet; reference and resulting comparison CC BY-SA 4.0."""
from PIL import Image, ImageDraw, ImageFont, ImageOps
from pathlib import Path
p=Path(__file__).parent
f='/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc';b='/usr/share/fonts/opentype/noto/NotoSansCJK-Bold.ttc'
def font(s,bold=False):return ImageFont.truetype(b if bold else f,s)
im=Image.new('RGB',(1600,1390),'#edf0f1');d=ImageDraw.Draw(im)
d.rectangle((0,0,1600,144),fill='#243740');d.text((48,22),'金属枠の自立式案内板',font=font(44,True),fill='white');d.text((50,88),'渋谷・2025年10月の写真を参照  /  単体素材・未配置',font=font(25),fill='#cbd9dd')
for x,title,sub in [(50,'参照写真','2025-10-10 23:13 / 夜間撮影'),(825,'制作モデル','近似視点 / 文字・紋章は意図的に省略')]:
 d.text((x,168),title,font=font(30,True),fill='#243740');d.text((x,213),sub,font=font(21),fill='#58717a')
r=Image.open(p/'reference_crop.png');r=ImageOps.contain(r,(725,865));im.paste(r,(50+(725-r.width)//2,260+(865-r.height)//2))
r=Image.open(p/'view_photo_matched.png').convert('RGB').crop((155,155,680,1060));r=ImageOps.contain(r,(725,865));im.paste(r,(825+(725-r.width)//2,260+(865-r.height)//2))
d.line((50,1150,1550,1150),fill='#bccbd1',width=2)
d.text((50,1168),'推定寸法 約 W 0.56 × D 0.29 × H 1.10 m  |  2,499 tris  |  画像テクスチャなし',font=font(23,True),fill='#243740')
d.text((50,1210),'写真: ウィ貴公子 / Wikimedia Commons · CC BY-SA 4.0（切抜き・拡縮・比較合成）',font=font(21),fill='#58717a')
d.text((50,1244),'出典・ライセンスURL・変更内容は同梱READMEに記載。比較画像・モデルも CC BY-SA 4.0。',font=font(20),fill='#58717a')
d.text((50,1277),'寸法・奥行・昼の色・背面は未確認。カメラ未校正。写真の文字を復元したモデルではありません。',font=font(19),fill='#58717a')
d.text((50,1312),'出典: commons.wikimedia.org/wiki/File:渋谷スクランブル交差点_2025年10月10日の渋谷_202510102313_IMG_6646.jpg',font=font(16),fill='#58717a')
d.text((50,1343),'ライセンス: https://creativecommons.org/licenses/by-sa/4.0/  |  モデル制作: dot, 2026-10-14',font=font(18),fill='#58717a')
im.save(p/'comparison.jpg',quality=92,optimize=True)
for n in ['view_front','view_side','view_photo_matched']:Image.open(p/(n+'.png')).convert('RGB').save(p/(n+'.jpg'),quality=90,optimize=True)
