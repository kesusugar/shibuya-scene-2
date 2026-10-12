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
