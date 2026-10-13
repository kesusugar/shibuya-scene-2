"""Rebuild the independent drainage supplement manifest from tracked inputs."""
import json,hashlib
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2];REPO=ROOT.parents[2]
def info(p):return {'sha256':hashlib.sha256(p.read_bytes()).hexdigest(),'bytes':p.stat().st_size}
files=['web/drainage.glb','source/data/layout.json','source/data/stats.json','source/blender/build_cover.py','source/tools/write_manifest.py','source/tools/project_cover.mjs','source/refs/SOURCES.json','README.md']
inputs=['assets/ground/core/web/ground_core.glb','assets/buildings/magnet/web/viewer.json','assets/buildings/magnet/source/refs/raw/M027.jpg']
m={'id':'drainage','status':'one photo-derived solid road cover; utility purpose, position and dimensions unverified','datum_tp_m':15,'coordinates':'Blender X east, Y north, Z = T.P.-15; web X east, Y up, Z south','licences':{'terrain':'MLIT Project PLATEAU, CC BY 4.0 compatible','positions':'OSM ODbL and GSI aerial measurements, see ground/core manifest','photos':'reference only, SOURCES.json; no photographic texture'},'build_stats':json.load(open(ROOT/'source/data/stats.json'))['contact_check'],'inputs':{p:info(REPO/p) for p in inputs},'files':{p:info(ROOT/p) for p in files if (ROOT/p).exists()}}
(ROOT/'manifest.json').write_text(json.dumps(m,ensure_ascii=False,indent=1)+'\n')
print('manifest',len(m['files']),'files')
