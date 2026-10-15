> Historical upper-stage record. Runtime hashes, counts and commands below describe the pinned accepted upper-stage fixture, not the current lower-panel runtime. See LOWER-PANEL-SOURCE.md and the current asset README for the continuation.

# Shibuya Stream: next-batch source112 panel rhythm

## Scope and evidence
A bounded office-facade improvement, not a complete 2025 reproduction. Exact original baseline: `source/data/panel-baseline/stream.glb`. All baseline files verified unchanged against the preceding research hashes. Frozen six-building v3 and ZIP were not opened for writing. QFRONT, Seibu and all other buildings were not touched.

Photograph: Syced, own work, CC0, December 1, 2025. This is after the requested October state. Its permanent facade is used only as a static-facade inference, never evidence of October's exact state. Official ABOUT describes irregular vertically elongated white panels, supporting identity/design rather than a specific capture date.
- Photo: https://commons.wikimedia.org/wiki/File:New_SHIBUYA_sign_over_Saikyo_train_leaving_to_Ebisu,_Shibuya_Stream_and_Sakura_Stage_in_the_background.jpg
- Original: https://upload.wikimedia.org/wikipedia/commons/2/2d/New_SHIBUYA_sign_over_Saikyo_train_leaving_to_Ebisu%2C_Shibuya_Stream_and_Sakura_Stage_in_the_background.jpg
- License: https://creativecommons.org/publicdomain/zero/1.0/
- Official design/identity: https://shibuyastream.jp/about/

The included reference is an ordinary crop from the 6451×4864 panorama at (5000,350)-(6300,3020), with no AI alteration. The historical photo-trace board is not included in this publication. Do not use generated geometry as independent evidence.

## Alignment and limits
First verified `source112-key.png`: source112 is the broad photo-right southeast plane, not the receding source98/118 planes. Local q=0 at (255.985,-290.160), q=1 at (279.103,-264.434), width34.587m. `panel-trace.json` records explicit q/v rectangles and photographic field endpoints. The selected central/upper office field is source-z90.804–163.436m, 14 estimated 5.188m intervals. Mapping the visible photo divisions to source heights is approximate: no camera calibration, survey, real storey-number assignment, or exact floor-height claim. Photo-right/left perspective slope is preserved in the annotated trace. Small 0.011m boundary tolerance accommodates original overlapping row patches.

White-panel positions were manually estimated from visible photo pixels, snapped to a 0.025 face-width half-bay grid and merged only when consecutive observed plate segments align. The 41 plate rectangles have different vertical lengths and lateral steps. This is not a pseudorandom pattern generated from the word “irregular.” White width0.050 of the face is an estimate. Twelve inner spandrel strips use approximately30% of the local pitch, based on visible opaque horizontal zones. The uppermost and lowermost selected intervals retain their original narrow bands for a conservative boundary transition and unchanged triangle budget. Existing materials remain byte-identical; these bands reuse the existing frame material rather than impose a global color change. Thus their neutral color is not a measured photographic color match.

Only source112 overlays are changed. Its original modulo white patches inside the selected field are removed, not hidden under a duplicate lattice. Glazing and mullions are preserved. Transparent crown above the selected field, lower/occluded portions, source98/118, crossing-facing planes, roof, ground skirts and all source wall triangles remain unchanged. No roof equipment, Google logo, guessed recesses, new side-wall details or podium claims.

## Baseline shell audit
Blender4.2.3 imported the exact GLB. Source112 consists of four baseline triangles, total approximately4972.154m², matching its planar ring area within float precision. No gross missing/overlapping triangle detected. Exact source triangles are retained; no shell repair was performed. The historical source112-triangulation.json report is not included here.

## Deliverables and reproduction
- `stream.glb`: changed asset only, deterministic binary surgery of existing overlay primitives.
- `stream.blend`: editable Blender4.2.3 scene, all meshes/materials local; packed; build script, explicit schedule and report embedded as Text datablocks. Cameras and illustrative review renders included, no external texture dependencies.
- `build.py`: run with Python3/numpy; hash-pinned baseline bundled at a portable relative path. Optional argument is output GLB path. It writes no baseline files.
- `render.py`: run with exact `blender -b --python render.py` to create blend and illustrative Workbench images.
- `test.py`: independent exact triangle-multiset/normals/material/node/geometry/budget checks.
- Photo boards are static reviewed evidence; portable render.py regenerates model views.
- `photo-comparison.jpg`, `comparison-southeast.jpg`, `comparison-southwest.jpg`, `comparison-northwest.jpg`, `after-closeup.png`: actual generated asset versus original/reference. Workbench material-color rendering, not calibrated photographic comparison or full-scene day/night acceptance.

Outcome:32532 triangles (unchanged),8 primitives/materials (unchanged),2021776 bytes (332 fewer).106 overlay triangles removed and106 added.144 original ground samples,0 missing, T.P.15 unchanged. Every non-target triangle and normal retained exactly, source/roof/ground geometry unchanged. Repeated GLB regeneration is byte-identical. Editable blend is not claimed byte-identical because Blender stores session metadata. No FPS or full-scene crossing visibility gain claimed. Parent batch review must still run full-scene crossing/elevated day/night and application tests before acceptance.
