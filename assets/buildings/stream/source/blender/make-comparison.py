from pathlib import Path
from PIL import Image,ImageDraw,ImageFont
A=Path(__file__).resolve().parents[2];E=A/'evidence/cumulative-v2';D=E/'lower';font=ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf',24);small=ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf',18)
board=Image.new('RGB',(1700,1630),'#f2f4f6');draw=ImageDraw.Draw(board)
draw.text((24,15),'Shibuya Stream | actual main -> delivered final',font=font,fill='#172536')
for col,stage in enumerate(['before','after']):
 draw.text((24+col*850,57),('MAIN 981faa7b' if col==0 else 'FINAL cc801164'),font=font,fill='#172536')
 im=Image.open(D/f'{stage}-southeast.jpg');im.thumbnail((780,1000));board.paste(im,(col*850+(850-im.width)//2,100))
 im=Image.open(D/f'{stage}-lower-field.jpg');im.thumbnail((470,470));board.paste(im,(col*850+(850-im.width)//2,1110))
draw.text((24,1595),'Same cameras / studio lighting. December 2025 facade inference; not October certification.',font=small,fill='#172536')
board.save(E/'comparison-main-final.jpg',quality=92)

