# Writes assets/buildings/magnet/manifest.json and assets/buildings/eiraku/manifest.json (sources, heights, licences, sha256).
#   python3 assets/buildings/magnet/source/tools/write_manifest.py
import json, hashlib, os, csv, glob, subprocess

HERE = os.path.dirname(os.path.abspath(__file__)); SRC = os.path.dirname(HERE); BLD = os.path.dirname(os.path.dirname(SRC))
M = json.load(open(os.path.join(SRC, 'data', 'measurements.json'))); H = M['heights']
F = json.load(open(os.path.join(SRC, 'data', 'camera_m027_fit.json')))
sha = lambda p: hashlib.sha256(open(p, 'rb').read()).hexdigest()
rev = subprocess.run(['git', 'rev-parse', 'HEAD'], cwd=SRC, capture_output=True, text=True).stdout.strip()
refs = [r for r in csv.DictReader(open(os.path.join(SRC, 'refs', 'REFERENCE_REGISTER.csv'), encoding='utf-8-sig')) if r['status'] == 'used']
axes = {"blender": "X=east, Y=north, Z=up", "gltf_export": "Y-up: (x, y, z)_blender -> (x, z, -y)_gltf = X=east, Y=up, Z=south",
        "webWorld": "X=east, Y=up, Z=south (as Shibuya Scene 1.0 and QFRONT)"}
common = {
    "units": "metres", "pivot": "OSM origin lat 35.6595, lon 139.7005; placed in world coordinates, no local offset",
    "axesTransform": axes, "worldPosition": [0, 0, 0], "rotationY": 0,
    "groundDatum": "0 m = pavement at the south-west corner, elevation 14.561 m (PLATEAU). QFRONT's 0 m is 15.099 m; the 0.54 m step is left for the terrain gate (G4).",
    "renderSettings": "Blender 4.2.3 Cycles CPU, AgX Medium High Contrast; day: sun az 207 / el 57 (M027, 2025-09-01 13:18 JST), camera-ray sky tint; night: deep-blue dome, street area lights; glossy rays see CC0 Poly Haven HDRIs (QFRONT copy)",
    "generator": "assets/buildings/magnet/source/blender/build_magnet.py (Blender 4.2.3 LTS): blender -b -P build_magnet.py -- <out> day|night preview|final view=m027|sw|south|west|roof [era=2025|none] [save] [clay]",
    "exporter": "assets/buildings/magnet/source/blender/export_web.py",
    "generatorRevision": rev or "(uncommitted)",
}
magnet = {
    "id": "magnet", "name": "MAGNET by SHIBUYA109（渋谷区神南1-23-10）", "version": "v1", "status": "G3 v1 - for owner review",
    "referenceYear": 2025,
    "referenceYearNote": "Form from 2019-2026 photos and PLATEAU 2025; signs, ads and screens are the 2025 era layer (source/data/signage_2025.json -> web/magnet_signs_2025.glb). 2026-02/03 photos (M001-M003) were used only to confirm signs still in place.",
    "footprintSource": "PLATEAU 2025 LOD2, Shibuya ward, tile 53393596, bldg_d47d8aa9-e4f5-4599-9d9a-bc129a12d6a8 (OSM way/116806281 'MAGNET SHIBUYA' agrees, PLATEAU share 0.93)",
    "heightSources": {
        "buildingHeight": {"value": H['buildingHeight_m'], "source": "PLATEAU measuredHeight", "note": "body height; not the tower"},
        "roofDeckHeight": {"value": H['west_wing_roofDeck_m'], "source": "PLATEAU LOD2 west-wing roof", "note": "photo M027 puts the wall top at 30.9 m with a 3.3 m truss above; the model follows the photo at the edge (open item)"},
        "parapetTopHeight": {"value": H['tower_parapetTop_m'], "source": "PLATEAU LOD2 tower parapet strips (tower roof 40.37 m)"},
        "steppedRoofs": {"values": [H['tower_front_west_roof_m']] + H['tower_step_roofs_m'] + [H['north_annex_roof_m']], "source": "PLATEAU LOD2"},
        "signTopHeight": {"value": 32.0, "source": "sign box top, photos M014/M027 (estimated)", "geometryConfidence": "photo-estimated"},
    },
    "geometryConfidence": f"high for footprint and roof heights (PLATEAU); medium for west face, drum and tower corner (photo M027, camera fit {F['rms_px']:.1f} px RMS, PARTIAL vs the 15 px target); estimated: north and east faces, rooftop plant, sign box depth",
    "cameras": {"m027": f"source/data/camera_m027_fit.json ({F['rms_px']:.1f} px RMS over 3 points + 4 vanishing lines + eye-level horizon; PARTIAL)"},
    "layers": {"signs_2025": {"file": "web/magnet_signs_2025.glb", "source": "source/data/signage_2025.json", "content": "lettering rebuilt from fonts; ad and screen artwork is original placeholder art (source/tools/make_signs.py); no photo pixels"}},
    "relatedBuildings": {"eiraku": "assets/buildings/eiraku (inside the PLATEAU MAGNET footprint, modelled separately; its finance signs are in this era layer)"},
    "sourceBlend": ["source/blend/magnet_day.blend", "source/blend/magnet_night.blend"],
    "attribution": [f"{r['id']}: {r['commons_file'][5:]} — {r['author'][:80]} — {r['licence']} — {r['url']}" for r in refs],
    "dataLicences": {"PLATEAU": "国土交通省 Project PLATEAU, CC BY 4.0 compatible terms", "HDRI": "Poly Haven CC0 (wide_street_01, shanghai_bund)"},
    **common,
}
eiraku = {
    "id": "eiraku", "name": "栄楽ビル（MAGNET 東隣）", "version": "v1", "status": "G3 v1 - context building",
    "referenceYear": 2025,
    "footprintSource": "PLATEAU 2025 LOD2: the 37.34 m roof inside MAGNET's bldg_d47d8aa9 footprint (a separate building on the ground)",
    "heightSources": {"buildingHeight": {"value": H['eiraku_roof_m'], "source": "PLATEAU LOD2 roof"},
                      "signTopHeight": {"value": H['eiraku_signTop_m'], "source": "photo M002/M014 (sign frame above the roof, estimated)"}},
    "geometryConfidence": "outline and height from PLATEAU; windows estimated from photos",
    "sourceBlend": ["../magnet/source/blend/magnet_day.blend (collection 07_EIRAKU)"],
    **common,
}
for doc, folder, files in ((magnet, os.path.join(BLD, 'magnet'), ['web/magnet.glb', 'web/magnet_signs_2025.glb', 'web/viewer.json', 'web/emissive_day.json', 'web/emissive_night.json',
                                                                  'source/blend/magnet_day.blend', 'source/blend/magnet_night.blend', 'source/blender/build_magnet.py', 'source/blender/export_web.py',
                                                                  'source/data/measurements.json', 'source/data/signage_2025.json', 'source/data/camera_m027_fit.json', 'source/data/magnet_plateau_lod2.json']),
                           (eiraku, os.path.join(BLD, 'eiraku'), ['web/eiraku.glb', 'web/viewer.json', 'web/emissive_day.json', 'web/emissive_night.json'])):
    doc['files'] = {f: {"sha256": sha(os.path.join(folder, f)), "bytes": os.path.getsize(os.path.join(folder, f))} for f in files if os.path.exists(os.path.join(folder, f))}
    json.dump(doc, open(os.path.join(folder, 'manifest.json'), 'w'), indent=1, ensure_ascii=False)
    print(folder, len(doc['files']), 'files')
