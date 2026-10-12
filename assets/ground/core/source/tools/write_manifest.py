# Writes assets/ground/core/manifest.json: sources with SHA-256, parameters, counts and the shipped files.
#   python3 source/tools/write_manifest.py [plateau_tran.gml] [plateau_core.json] [old shibuya-scene-data.json]
import json, hashlib, os, sys, subprocess
HERE = os.path.dirname(os.path.abspath(__file__)); SRC = os.path.dirname(HERE); ROOT = os.path.dirname(SRC)
sha = lambda p: hashlib.sha256(open(p, 'rb').read()).hexdigest()
ext = {}
for k, p in zip(('plateau_tran_gml', 'plateau_core_json', 'old_scene_data_json'), sys.argv[1:4]):
    if os.path.exists(p): ext[k] = {'file': os.path.basename(p), 'sha256': sha(p), 'bytes': os.path.getsize(p)}
inp = json.load(open(os.path.join(SRC, 'data', 'ground_input.json'))); st = json.load(open(os.path.join(SRC, 'data', 'ground_stats.json')))
rev = subprocess.run(['git', 'rev-parse', 'HEAD'], cwd=SRC, capture_output=True, text=True).stdout.strip()
files = ['web/ground_core.glb', 'source/data/ground_input.json', 'source/data/ground_stats.json', 'source/data/crosswalks_measured.json',
         'source/blender/build_ground.py', 'source/tools/prepare_ground.py', 'source/tools/measure_crosswalks.py',
         'source/data/ground_anchors.json', 'source/blender/ground_anchor.py']
m = {
    'id': 'ground_core', 'name': 'Core ground (Shibuya Scramble Crossing, radius 150 m)', 'version': 'C2a v1', 'status': 'foundation: positions and heights; flat colours, no surface detail',
    'datum': {'definition': 'world Y = T.P. elevation - 15.000 m', 'doc': 'docs/core/C2A_PLAN.md'},
    'axes': 'Blender X east, Y north, Z up (datum metres) -> glTF/web X east, Y up, Z south',
    'sources': {
        'road_surfaces': 'PLATEAU 2025 Shibuya-ku tran (53393596), TrafficArea LOD3 (road 1000, intersection 1020, sidewalk 2000) and AuxiliaryTrafficArea LOD3 (island 3000); LOD2 only where no LOD3 covers the spot (none needed within 150 m)',
        'building_footprints_for_fill': 'PLATEAU 2025 bldg GroundSurface (tiles 53393585/86/95/96)',
        'crosswalks': 'OSM footway=crossing ways (old project data, fetched 2026-09-08), widths and centre lines measured on the GSI seamless aerial photo (国土地理院 シームレス空中写真, zoom 18, 0.485 m/px; measurement only, not used as texture; capture year not stated per tile)',
        'licences': {'PLATEAU': 'CC BY 4.0 compatible (国土交通省 Project PLATEAU)', 'OSM': 'ODbL (© OpenStreetMap contributors)', 'GSI': '国土地理院コンテンツ利用規約 (CC BY 4.0 compatible) - 出典：国土地理院'},
        'external_inputs': ext,
    },
    'parameters_not_measured': {k: inp['params'][k] for k in ('kerb_height_m', 'kerb_low_m', 'landing_flat_m', 'landing_ramp_m', 'zebra_bar_m', 'zebra_gap_m', 'default_crosswalk_width_m')},
    'parameter_notes': {'kerb_height_m': '道路構造令 standard; PLATEAU LOD3 has no kerb step (2,125 shared vertices, max 0.008 m)', 'kerb_low_m': 'barrier-free landing value',
                        'zebra': 'Japanese road-marking standard 45 cm / 45 cm; check on photos in C3'},
    'prepare_stats': inp['stats'], 'build_stats': st,
    'building_anchors': json.load(open(os.path.join(SRC, 'data', 'ground_anchors.json'))),
    'generator': ['python3 source/tools/measure_crosswalks.py <old data json> <gsi tiles> source/data/crosswalks_measured.json',
                  'python3 source/tools/prepare_ground.py <plateau_core.json> source/data/crosswalks_measured.json source/data/ground_input.json 150',
                  'blender -b -P source/blender/build_ground.py -- source/data/ground_input.json web/ground_core.glb source/data/ground_stats.json',
                  'blender -b -P source/blender/ground_anchor.py -- web/ground_core.glb <plateau_core.json> source/data/ground_anchors.json'],
    'generatorRevision': rev or '(uncommitted)',
    'files': {f: {'sha256': sha(os.path.join(ROOT, f)), 'bytes': os.path.getsize(os.path.join(ROOT, f))} for f in files if os.path.exists(os.path.join(ROOT, f))},
}
json.dump(m, open(os.path.join(ROOT, 'manifest.json'), 'w'), ensure_ascii=False, indent=1)
print('manifest', len(m['files']), 'files')
