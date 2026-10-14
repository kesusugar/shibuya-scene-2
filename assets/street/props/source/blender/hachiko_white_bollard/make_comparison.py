from PIL import Image, ImageDraw, ImageFont
from pathlib import Path
import argparse, os
a=argparse.ArgumentParser(description='Compose reference crops and Blender studio renders; requires Pillow and a CJK font')
a.add_argument('--renders', type=Path, required=True)
a.add_argument('--evidence', type=Path, required=True)
a.add_argument('--font', default=os.environ.get('CJK_FONT','/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc'))
args=a.parse_args();P=args.renders
font=args.font
f=lambda n:ImageFont.truetype(font,n)
im=Image.new('RGB',(1600,1150),'#f4f5f7');d=ImageDraw.Draw(im)
d.text((40,25),'ハチ公背後の白いボラード ｜ 写真参照による暫定復元',font=f(35),fill='#172535')
d.text((40,85),'絶対寸法は未確認。背景写真と独立モデルの比較であり、写真測量・厳密な位置合わせではありません。',font=f(22),fill='#4b5663')

for title,name,x,w,h in [('元写真・左側支柱','reference_left.jpg',40,360,480),('元写真・右側支柱','reference_right.jpg',430,360,408)]:
 crop=Image.open(args.evidence/name).resize((w,h),Image.Resampling.LANCZOS)
 d.text((x,145),title,font=f(25),fill='#172535');im.paste(crop,(x,190))
 d.text((x,690),'根元は石に隠れ、全高は不明',font=f(20),fill='#9b4d12')
 d.text((x,725),'切り抜き・拡大（色補正なし）',font=f(18),fill='#4b5663')
for title,name,x in [('モデル・正面','front.png',845),('モデル・側面','side.png',1210)]:
 d.text((x,145),title,font=f(25),fill='#172535')
 render=Image.open(P/name).convert('RGBA');render.thumbnail((310,590))
 bg=Image.new('RGB',render.size,'#e4e9ee');bg.paste(render,mask=render.getchannel('A'));im.paste(bg,(x,190))
 d.text((x,800),'全高 0.800 m［仮定］',font=f(21),fill='#172535')
 d.text((x,835),'本体径 0.114 m［仮定］',font=f(21),fill='#172535')
 d.text((x,870),'不可視の下部は直管で補完',font=f(20),fill='#9b4d12')
d.line((40,930,1560,930),fill='#c5cbd1',width=2)
for y,t in [(950,'帯高 0.080 m ／ 天端から帯上端 0.100 m：写真の径に対する比率を概算。絶対値は仮定径に依存。'),(985,'キャップ・底面・材質は簡略化。文字、接続金具、柵、道路は未再現。正面・側面の輪郭は回転対称。'),(1025,'写真：RuinDig/Yuki Uchida ｜ 2025-07-13 ｜ CC BY 4.0 ｜ 切り抜き・拡大・注記を追加'),(1060,'原典：Wikimedia Commons / File:Tokyo-Shibuya-and-Shinbashi---2025-07-13_095.jpg'),(1093,'ライセンス：https://creativecommons.org/licenses/by/4.0/　出典の完全URLは SOURCE_LICENSE.md を参照。')]:
 d.text((40,y),t,font=f(20 if y<1025 else 18),fill='#4b5663')
im.save(args.evidence/'comparison.jpg',quality=90,optimize=True)
