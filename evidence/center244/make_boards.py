from PIL import Image,ImageDraw,ImageFont
from pathlib import Path
import sys
R=Path(__file__).resolve().parents[2];E=Path(__file__).parent
font='/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc';f=ImageFont.truetype(font,28);sm=ImageFont.truetype(font,20)
src=Image.open(sys.argv[1]);photo=src.crop((1500,600,2250,1970));photo.save(E/'photo-2025-01.jpg',quality=94)
W,H=500,913;out=Image.new('RGB',(1540,1105),'#eeeee9');d=ImageDraw.Draw(out)
for i,(im,label) in enumerate([(photo,'写真：2025年1月31日'),(Image.open(E/'before-full.png'),'変更前：元のGLB'),(Image.open(E/'after-full.png'),'改善案：個別外装＋1月看板')]):
 x=10+i*510;out.paste(im.convert('RGB').resize((W,H),Image.Resampling.LANCZOS),(x,72));d.text((x+8,20),label,font=f,fill='#222')
d.text((18,1000),'センター244 ／ Syced・CC0写真。近似カメラを前後で固定。周辺の遮蔽物は模型では省略。',font=sm,fill='#333')
d.text((18,1032),'寸法・背面支持材は推定。広告の隠れた部分は中立面。1月看板は通常の10月表示へ登録しない。',font=sm,fill='#333')
d.text((18,1064),'元PLATEAU・原点・上端T.P.49.843mを保存。全シーン・実機FPSは未検証。',font=sm,fill='#333');out.save(E/'comparison-ja.jpg',quality=94)
for view in ['front','side','close']:
 ims=[Image.open(E/(w+'-'+view+'.png')).convert('RGB') for w in ['before','after']];w=600;h=round(ims[0].height*w/ims[0].width);o=Image.new('RGB',(1230,h+120),'#eeeee9');dd=ImageDraw.Draw(o)
 for i,im in enumerate(ims):o.paste(im.resize((w,h),Image.Resampling.LANCZOS),(10+i*610,60));dd.text((20+i*610,12),('変更前' if i==0 else '改善案')+' / '+{'front':'正面','side':'側面','close':'接写'}[view],font=f,fill='#222')
 dd.text((20,h+75),'前後は同一カメラ。単体資産比較。1月広告を明示的に追加。',font=sm,fill='#333');o.save(E/('comparison-'+view+'.jpg'),quality=93)
# Close photo comparison uses the same recorded crop as render_evidence.py.
photo_close=src.crop((1740,1180,2110,1800));W,H=420,704;o=Image.new('RGB',(1300,845),'#eeeee9');dd=ImageDraw.Draw(o)
for i,(im,label) in enumerate([(photo_close,'写真：1月の外装'),(Image.open(E/'before-close.png'),'変更前：同一視点'),(Image.open(E/'after-close.png'),'改善案：同一視点')]):
 x=10+i*430;o.paste(im.convert('RGB').resize((W,H),Image.Resampling.LANCZOS),(x,65));dd.text((x+8,18),label,font=f,fill='#222')
dd.text((18,786),'写真は周辺による遮蔽あり。模型は単体。低解像度・未観測部分は補完しない。',font=sm,fill='#333');o.save(E/'comparison-close-photo-ja.jpg',quality=94)
