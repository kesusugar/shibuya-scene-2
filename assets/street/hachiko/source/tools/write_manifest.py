import json,hashlib
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2];REPO=ROOT.parents[2]
def info(p):return {'sha256':hashlib.sha256(p.read_bytes()).hexdigest(),'bytes':p.stat().st_size}
stats=json.load(open(ROOT/'source/data/stats.json'))
inputs=['assets/ground/core/web/ground_core.glb','assets/street/tactile/source/data/stats.json']
m={'id':'hachiko','status':'photo-informed sculpture prototype; scale, orientation and October condition unverified','datum_tp_m':15,'coordinates':'Blender east/north/up; web east/up/south','licences':{'model':'CC BY-SA 4.0','reference_photos':'CC BY-SA 4.0 / CC BY 4.0, see SOURCES.json','positions':'OSM contributors, ODbL','terrain':'PLATEAU / MLIT, CC BY 4.0 compatible','font':'Noto Serif CJK, SIL OFL 1.1'},'build_stats':{k:stats[k] for k in ['anchor_tp','max_burial_m','triangles']},'inputs':{p:info(REPO/p) for p in inputs},'files':{str(p.relative_to(ROOT)):info(p) for p in sorted(ROOT.rglob('*')) if p.is_file() and p.name!='manifest.json'}}
(ROOT/'manifest.json').write_text(json.dumps(m,ensure_ascii=False,indent=1)+'\n')
