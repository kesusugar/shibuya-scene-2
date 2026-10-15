from PIL import Image, ImageDraw, ImageFont
from pathlib import Path
P=Path(__file__).resolve().parent
im=Image.new('RGB',(768,1024),(244,244,236)); d=ImageDraw.Draw(im)
d.rounded_rectangle((12,12,755,1011),radius=45,fill=(24,41,151))
d.ellipse((159,119,609,569),fill=(245,246,235))
latin='/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf'
serif='/usr/share/fonts/truetype/dejavu/DejaVuSerif-BoldItalic.ttf'
jp='/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc'
def center(s,y,font,size,color):
 f=ImageFont.truetype(font,size); box=d.textbbox((0,0),s,font=f); w=box[2]-box[0];d.text(((768-w)/2-box[0],y-box[1]),s,font=f,fill=color)
center('i',191,serif,340,(201,22,26))
center('Tourist',646,latin,76,(250,250,242))
center('Information',740,latin,76,(250,250,242))
center('観光案内所',858,jp,46,(250,250,242))
im.save(P/'placard_albedo.png')
