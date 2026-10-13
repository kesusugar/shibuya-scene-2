import json,hashlib
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2];REPO=ROOT.parents[2]
def info(p):return {'sha256':hashlib.sha256(p.read_bytes()).hexdigest(),'bytes':p.stat().st_size}
S=json.load(open(ROOT/'source/data/stats.json'))
inputs=['assets/ground/core/web/ground_core.glb','assets/street/hachiko/source/data/layout.json','assets/street/hachiko/source/refs/july094.jpg','assets/street/hachiko/source/refs/july095.jpg','assets/street/tactile/source/data/stats.json']
m={'id':'hachiko-surround','status':'partial photo-informed planter/perch-rail prototype; offsets, dimensions, species, October condition and inscription unverified','datum_tp_m':15,'coordinates':'Blender east/north/up; web east/up/south','licences':{'model':'CC BY-SA 4.0','reference_photos':'RuinDig/Yuki Uchida, CC BY 4.0; SOURCES.json','position_origin':'OSM contributors, ODbL','terrain':'MLIT PLATEAU, CC BY 4.0 compatible'},'build_stats':{'triangles':S['triangles'],'anchors':[{k:r[k] for k in ['id','anchor_tp','max_burial_m']} for r in S['items']]},'inputs':{p:info(REPO/p) for p in inputs},'files':{str(p.relative_to(ROOT)):info(p) for p in sorted(ROOT.rglob('*')) if p.is_file() and p.name!='manifest.json'}}
(ROOT/'manifest.json').write_text(json.dumps(m,ensure_ascii=False,indent=1)+'\n')
