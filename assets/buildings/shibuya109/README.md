# SHIBUYA109: architectural revision3, bounded publication successor

Initial implementation was merged in [PR35](https://github.com/kesusugar/shibuya-scene-2/pull/35), grounding in [PR36](https://github.com/kesusugar/shibuya-scene-2/pull/36), and silver material in [PR37](https://github.com/kesusugar/shibuya-scene-2/pull/37). This revises an existing implemented building. It is not a new building and does not claim a new original PLATEAU reconstruction. Main 8633c1b7 shipped GLB 152920785e92f2c11a95b2cf2b29aec8a7aac76c71d119fd9045442dfde491a5 (373,996 bytes, 5,690 triangles, 11 primitives); its manifest SHA/byte count was stale. This publication carries the already delivered revision3 output unchanged: 0ef0583ab368e3d2265aa299292bd6306ef68901e859265b94f214090d8b239e (2,763,184 bytes, 45,727 triangles, 37 primitives).

## Current entrypoints
- Runtime: web/shibuya109.glb and both web/emissive_*.json tables. Existing web/viewer.json is unchanged.
- Packed editable scene: source/blender/shibuya109.blend; Blender 4.2.3.
- Portable generator: source/architectural-revision3/scripts/build.py.
- Fixed predecessor: source/architectural-revision3/inputs/prior.glb, SHA256 a31e295bf8ce9bbef9ddc0c6164526db84cb7b08a6caf1957352be142854db90. This is an intermediate accepted source stage, NOT the main-branch output. Its duplicate at source/entrance-panel-v1/output/shibuya109.glb is the exact historical regression fixture, not the current entrypoint.

## Reproduce independently
Copy source/architectural-revision3 to a new writable directory and run from that directory with official Blender 4.2.3 on PATH:

    blender -b --python-exit-code 1 -P scripts/build.py -- --phase2
    mkdir -p evidence
    python3 scripts/verify.py
    python3 scripts/verify_feet_materials.py

Blender supplies NumPy and mathutils. Verification uses Python3 standard library. No network or other checkout is needed. Output is output/combined/shibuya109.glb and shibuya109.blend. Compare the GLB SHA256 above before integration; copy the generated GLB to the asset's web/shibuya109.glb and the scene to source/blender/shibuya109.blend. Keep the shipped day/night tables. Scene save timestamps can differ; byte-exact scene reproduction is not claimed. The delivered packed scene is pinned separately, SHA256 e8b7ed6099659f76dbdb8e157b45f39480026e6f4cc2c9e8b1dde7939760a946. Manual scene edits do not update the generator.

## Scope and evidence
The cumulative main-to-final delta includes all later cylinder, roof, cap, upper logo and wing changes as well as the final entrance/stair/aperture revision. The pinned intermediate input already carries those previous cylinder, roof, cap, logo and wing stages; their original creation chain is not replayed by this package. Revision3 adds the gold four-column/truss entrance, white lower identity, fitted feet, external colored stair/rails, six recessed tower openings and recessed wing glass/frame/slits. Original live attributes, retained triangles, upper logo, roof/cap, nodes and transforms are tested against the pinned intermediate predecessor, not asserted byte-identical to the older main model. All dimensions and hidden details are estimates. Stair base contact and continuous second-floor circulation are not guaranteed.

Model-only JPEG comparison boards and original camera JSON are under source/architectural-revision3/evidence. Those before-final/final/boards folders are historical delivery evidence against the intermediate a31 predecessor, NOT current main. The separate evidence/main-vs-revision3 folder contains freshly rendered main8633c1b7 versus accepted revision3 overall and entry-front comparisons with identical cameras, lights and staging; see its comparison receipt. JPEGs are review derivatives, not pixel-identical PNGs. Ground shown in renders is contextual and not part of the GLB. No reference photograph or advertising artwork is newly distributed here.

Coordinates remain inherited scene coordinates: one unit is one metre; local Blender Z = T.P. altitude minus15 m; glTF (X,Y,Z) = Blender (X,Z,-Y). Viewer/placement and application source are unchanged. No QFRONT, Seibu, walking display, FPS, merge or deployment work is included.

## Validation and limits
See source/architectural-revision3/PUBLICATION_VALIDATION.json. A relocated Blender4.2.3 run reproduced the exact accepted GLB; Python preservation/feet checks and seven unchanged revision3 regression tests passed against pinned actual-main buildings/look modules. Tests cover retained geometry, independent fixture hash,150 aperture rays, contact geometry, budgets and day/night/day material behavior. These are asset-level checks. Full-scene assembly, whole-suite tests, browser pixels, typecheck/build, collision, walking and FPS were not run.

## Sources and rights
ARCHITECTURE_SOURCES.json and inputs/sources.json retain source URLs, attribution, reference-only designations and date uncertainty. SPACE MEDIA, Signs & Displays/Aoi Neon, SHIBUYA109 Entertainment and DOCOMOMO photographs/drawings are references only and excluded. No licensed-photo crops are needed or included in this bounded package. Existing base-branch reference files are preserved without modification, not newly redistributed as part of this source backup.

Base geometry inherits Project PLATEAU provenance: bldg_aba50b67-9267-4c80-9004-08ebfc7682d8, OSM way/55895868. Source and third-party rights remain applicable. No new blanket model/trademark licence is granted; a reference photograph's licence does not license model geometry, logos or trademarks.

The manifest inventories this bounded package plus unchanged viewer dependency only. Historical files left in the repository remain historical and are not current generation dependencies. Source/data/stats.json retains geographic/pavement provenance while explicitly labeling prior counts. This document and manifest are newly authored, not recovered missing historical prose.
