from PIL import Image,ImageDraw
from pathlib import Path
import json,hashlib
R=Path(__file__).resolve().parents[1];E=R/'evidence';pairs=[('before-front.png','BEFORE | prior consistency repair'),('prototype-front.png','REVIEW PROTOTYPE | inferred proportions'),('prototype-oblique-east.png','EAST OBLIQUE | recessed entry, glazed return'),('prototype-oblique-west.png','WEST OBLIQUE | terminal pier and remainder'),('prototype-plan-section.png','TRUE SECTION PLAN | h1.5m, no V notch'),('prototype-soffit-upward.png','UPWARD VIEW | closed soffit under preserved fascia')]
board=Image.new('RGB',(1800,1900),(245,245,240));draw=ImageDraw.Draw(board);draw.text((20,12),'EKIMAE GROUND FRONTAGE | REVIEW ONLY | NO PHOTO-CALIBRATION PASS',(25,25,25))
for i,(f,title) in enumerate(pairs):
 x=(i%2)*900;y=50+(i//2)*615;im=Image.open(E/f).convert('RGB').resize((900,600));board.paste(im,(x,y));draw.text((x+12,y+8),title,(20,20,20))
board.save(E/'prototype-review-board.jpg',quality=93)
pins={'candidate_sha256':hashlib.sha256((R/'web/ekimae.glb').read_bytes()).hexdigest(),'status':'Review-only snapshot, not accepted','files':{str(p.relative_to(R)):hashlib.sha256(p.read_bytes()).hexdigest() for p in R.rglob('*') if p.is_file() and p.suffix in ['.py','.json','.glb','.blend','.png','.jpg','.md'] and p.name!='SNAPSHOT.json'}}
(R/'SNAPSHOT.json').write_text(json.dumps(pins,indent=2))
