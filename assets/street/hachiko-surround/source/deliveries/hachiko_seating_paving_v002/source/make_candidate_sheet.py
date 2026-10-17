#!/usr/bin/env python3
"""Technical QA sheet drawn from authored candidate parameters and authored texture.
No external/reference image is included. Left is a plan diagram, not a photoreal render.
"""
from pathlib import Path
from PIL import Image,ImageDraw,ImageFont
import math,json
R=Path(__file__).resolve().parents[1];im=Image.new('RGB',(1800,1100),(243,244,240));d=ImageDraw.Draw(im)
font='/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf'
def f(n):return ImageFont.truetype(font,n)
def text(x,y,s,size=24,fill=(34,42,45)):d.text((x,y),s,font=f(size),fill=fill)
d.rectangle((0,0,1800,140),fill=(39,48,52));text(60,28,'LAYOUT CANDIDATES',40,(255,255,255));text(60,85,'NOT VERIFIED CURRENT  |  NOT A SCENE-INTEGRATION RESULT',23,(240,204,117))
d.rounded_rectangle((40,170,870,968),radius=18,fill=(255,255,255));d.rounded_rectangle((900,170,1760,968),radius=18,fill=(255,255,255))
text(70,193,'A. Partial curved stone / silver rails',27);text(70,237,'Plan diagram. Unseen back / full ring NOT reconstructed.',19,(89,100,104))
# Plan mapping of the exact candidate assumptions in build_assets.py.
ox,oy=455,590;sc=87
pt=lambda x,y:(ox+x*sc,oy-y*sc)
for x in range(-4,5):
 d.line([pt(x,-2.4),pt(x,3.6)],fill=(229,233,231),width=1)
for y in range(-2,4):d.line([pt(-4.4,y),pt(4.4,y)],fill=(229,233,231),width=1)
for deg0,deg1 in [(200,258),(282,340)]:
 aa=[math.radians(deg0+(deg1-deg0)*i/100) for i in range(101)]
 points=[pt(4.245*math.cos(a),2.4+4.245*math.sin(a)) for a in aa]+[pt(3.975*math.cos(a),2.4+3.975*math.sin(a)) for a in aa[::-1]]
 d.polygon(points,fill=(103,112,114));d.line(points+[points[0]],fill=(48,59,63),width=2)
 for rr in [3.88,4.1]:d.line([pt(rr*math.cos(a),2.4+rr*math.sin(a)) for a in aa],fill=(191,208,216),width=5)
 for i in range(6):
  a=math.radians(deg0)+.02+(math.radians(deg1-deg0)-.04)*i/5
  d.line([pt(3.88*math.cos(a),2.4+3.88*math.sin(a)),pt(4.1*math.cos(a),2.4+4.1*math.sin(a))],fill=(207,218,223),width=3)
# Origin is not statue geometry.
x,y=pt(0,0);d.line((x-10,y,x+10,y),fill=(176,87,56),width=2);d.line((x,y-10,x,y+10),fill=(176,87,56),width=2)
text(315,618,'Equipment local origin',18,(160,72,43));text(70,838,'Radius 4.0 m, center (0, 2.4): inferred',21);text(70,877,'Two open partial strips. Default OFF.',21);text(70,916,'No statue, plants or large-tree enclosure included.',18,(89,100,104))
text(930,193,'B. Single circular paving layout',27);text(930,237,'Authored atlas only. Flat GLB = PREVIEW ONLY.',19,(89,100,104))
pav=Image.open(R/'textures/paving_ring_candidate_basecolor.png').convert('RGB');pav.thumbnail((790,600),Image.Resampling.LANCZOS);im.paste(pav,(935,300));d=ImageDraw.Draw(im)
text(930,838,'Fixed patch: 10.4 x 7.0 m. No ground edits.',21);text(930,877,'Circle / divider positions remain inferred.',21);text(930,916,'Front circle edge is clipped by the accepted patch.',18,(89,100,104))
text(60,1000,'Surface detail: July 2025 photos. Wide layout: undated user reference.',23);text(60,1042,'Generated geometry and textures only. External photographs are not redistributed.',20,(85,97,103))
im.save(R/'previews'/'04_candidate_layout_contact_sheet.png')
(R/'qa'/'candidate_sheet.json').write_text(json.dumps({'file':'previews/04_candidate_layout_contact_sheet.png','type':'technical plan diagram plus authored atlas preview','not_photoreal_render':True,'not_scene_validation':True,'no_external_image_pixels':True,'geometry_parameters_match':'source/build_assets.py','texture':'textures/paving_ring_candidate_basecolor.png'},indent=2))
