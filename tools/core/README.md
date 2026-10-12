# Gate C0 tools (read-only audit)

Run in this order. Inputs come from the old repository (`kesusugar/shibuya-scene`, read-only) and PLATEAU 2025 Shibuya (tile 53393596); nothing here edits assets, the viewer or the old repository.

1. `python3 tools/core/extract_buildings.py <old>/public/data/shibuya-scene-data.json <old_building_model.json> docs/core/coverage/buildings_c0.json`
   - One record per OSM building (666), with the height source written out.
2. `blender -b -P tools/core/visibility_pano.py -- docs/core/coverage/buildings_c0.json tools/core/cameras_c0.json <vis_dir> 1440`
   - Object-ID equirectangular panoramas from the five viewpoints; writes `<cam>_ids.npy` and `<cam>_coverage.json`.
   - `docs/core/coverage/<cam>_ids16.png` is the same ID map as a 16-bit PNG: 0 = ground, 1 = sky, k + 1 = building k (1-based index into `buildings_c0.json`).
3. `python3 tools/core/build_register.py docs/core/coverage/buildings_c0.json <vis_dir> docs/core`
   - Writes `ASSET_REGISTER.csv`, `VIEW_COVERAGE.csv`, `coverage/top40.json` and the status panoramas.
4. `python3 tools/core/merge_references.py docs/core/REFERENCE_REGISTER.csv [seibu meta.json]`
5. `python3 -I tools/core/terrain_probe.py <53393596_tran.gml> docs/core/coverage/terrain_probe.json`

`identity_notes.json` holds the inferred identities of unnamed buildings ("推定" = not verified).
6. `python3 tools/core/sensitivity.py <vis_dir>` - re-scores the ranking under other weights, a walker view band and leave-one-view-out (self-review).

## C0 supplement (PLATEAU LOD2, structures, elevated views)
7. `python3 -I tools/core/plateau_core.py <plateau_dir> <plateau_core.json> 320` - PLATEAU 2025 bldg/brid/frn/veg/tran within 320 m (tile 53393596 + neighbouring bldg tiles, codelists/).
8. `python3 -I tools/core/build_records_v2.py docs/core/coverage/buildings_c0.json <plateau_core.json> <records_v2.json>` - LOD2 surfaces, PLATEAU-only buildings, bridges; datum T.P. 15.000.
9. `blender -b -P tools/core/visibility_pano_v2.py -- <records_v2.json> tools/core/cameras_v2.json <vis_v2> 1440` - 7 views with a 200-ray burial check. X01 is re-run with its host (way/355250634 and brid_bd5e7fe1) removed, because the photo was taken through that corridor's windows.
10. `python3 tools/core/build_register_v2.py <records_v2.json> docs/core <cam>=<vis>[:<records>] ...` - `ASSET_REGISTER_V2.csv`, `coverage_v2/`.
11. `python3 tools/core/structure_register.py <old data json> <plateau_core.json> docs/core` - `STRUCTURE_REGISTER.csv`.
12. `python3 -I tools/core/ground_contact.py <plateau_core.json> docs/core/terrain/ground_contact.json` - building ground vs pavement at each corner.
13. `python3 -I tools/core/commons_survey.py <out.json> 250` - polite Commons count by year/licence; HTTP 429 = "unverified", never "none".
