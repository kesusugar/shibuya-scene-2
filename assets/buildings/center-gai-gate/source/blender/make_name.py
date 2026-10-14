"""Self-authored permanent label only; Noto Sans CJK JP Bold (SIL OFL 1.1).
The observed wording is 渋谷センター街; glyph style and physical spacing are approximated.
Run with Pillow and Noto Sans CJK Bold installed; no advertising reproduced.
"""
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont
font=ImageFont.truetype('/usr/share/fonts/opentype/noto/NotoSansCJK-Bold.ttc',170,index=0)
im=Image.new('RGB',(256,1536),(202,208,199));d=ImageDraw.Draw(im)
for i,ch in enumerate('渋谷センター街'):
    box=d.textbbox((0,0),ch,font=font); w=box[2]-box[0]; h=box[3]-box[1]
    d.text(((256-w)/2-box[0],40+i*207+(170-h)/2-box[1]),ch,font=font,fill=(63,71,65))
im.save(Path(__file__).parent.parent/'textures'/'permanent_name.png')
