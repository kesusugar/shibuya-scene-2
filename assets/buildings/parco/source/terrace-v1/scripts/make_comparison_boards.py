"""Label matched generated renders only. No source reference image pixels are used."""
from pathlib import Path
from PIL import Image,ImageDraw,ImageFont
import json,hashlib,datetime
ROOT=Path(__file__).resolve().parents[1];R=ROOT/'renders'
fontpath=Path('/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf')
def font(n):
 try:return ImageFont.truetype(str(fontpath),n)
 except OSError:return ImageFont.load_default(size=n)
rows=[]
for state in ['before','candidate']:
 data=json.loads((R/f'render-manifest-{state}.json').read_text())['renders'];assert len(data)==10
 expected=hashlib.sha256((ROOT/('inputs/roof22-corrected-base.glb'if state=='before'else'parco_terrace_candidate.glb')).read_bytes()).hexdigest()
 for row in data:
  assert row['asset_sha256']==expected and hashlib.sha256((R/row['file']).read_bytes()).hexdigest()==row['image_sha256'];rows.append(row)
(R/'render-manifest-final.json').write_text(json.dumps({'all_twenty_verified':True,'renders':rows,'scope':'Matched generated before/after materials and one-material clay, not source photographs.'},indent=2)+'\n')
boards=[]
for mode in ['material','clay']:
 im=Image.new('RGB',(1700,1810),(246,247,248));d=ImageDraw.Draw(im)
 d.text((28,20),'PARCO | scoped terrace review candidate',font=font(35),fill=(27,36,45))
 d.text((28,68),'Material proposal'if mode=='material'else'Geometry proof: ONE identical opaque grey material on every mesh',font=font(24),fill=(50,62,72))
 for i,state in enumerate(['before','candidate']):
  d.text((28+i*840,114),'BEFORE | roof22-corrected baseline'if state=='before'else'AFTER | deep terrace candidate',font=font(26),fill=(23,43,58))
 for j,view in enumerate(['ne-photo-angle','north-matched']):
  for i,state in enumerate(['before','candidate']):
   src=Image.open(R/f'{state}-{mode}-{view}.png').convert('RGB');src.thumbnail((810,742));x=28+i*840;y=158+j*780;im.paste(src,(x,y));d.text((x,y+744),'Matched NE perspective'if j==0 else'Matched north view',font=font(20),fill=(50,62,72))
 d.text((28,1736),'Inferred architecture, not survey or runtime acceptance. Fixed footprint, roof and office tower retained.',font=font(23),fill=(30,50,65))
 d.text((28,1771),'Opaque core glass is an exterior proxy; below-5F opaque finish remains unconfirmed. No copyrighted reference pixels.',font=font(20),fill=(65,74,83))
 path=R/f'comparison-{mode}-NE-north.png';im.save(path);boards.append({'file':path.name,'sha256':hashlib.sha256(path.read_bytes()).hexdigest(),'source_files':[f'{state}-{mode}-{view}.png'for view in ['ne-photo-angle','north-matched']for state in ['before','candidate']]})
# All five paired views: smaller contact sheets serve as QA indexes, not substitutes for full-size images.
for mode in ['material','clay']:
 im=Image.new('RGB',(2500,1040),'white');d=ImageDraw.Draw(im)
 for j,state in enumerate(['before','candidate']):
  for i,view in enumerate(['ne-photo-angle','north-matched','east-matched','depth-eye-level','roof-context']):
   src=Image.open(R/f'{state}-{mode}-{view}.png').convert('RGB');src.thumbnail((488,447));im.paste(src,(i*500+6,j*520+45));d.text((i*500+6,j*520+10),f'{state} | {view}',font=font(18),fill='black')
 im.save(R/f'contact-{mode}-all-views.png')
(R/'board-manifest.json').write_text(json.dumps({'boards':boards,'no_copyrighted_reference_pixels':True},indent=2)+'\n')
print('20 render hashes verified; paired boards complete')
