# Shibuya Stream: cumulative source112 facade revision

This single-asset revision republishes the already delivered upper white-panel rhythm and lower-left six rectangles. It is not a new whole-building reconstruction. Actual main is the earlier modulo-pattern facade, not the accepted upper-stage fixture.

## Actual main → final

- Main Git blob: 981faa7b5ffab3ceffa36367533167f437841f1e; SHA256 16b029fbec71fa753b2c8f5bdbcead325105d9576df2bc636b637f05af130aed.
- Final Git blob: cc801164bff5b6c848e2b87f73f823c8ab716d53; SHA256 e03535bbe29f29524354f76cb8f066b30072fe355abda503d2ddeb8f70f96b32.
- Main 32,532 triangles / 2,022,108 bytes → final 32,538 triangles / 2,022,104 bytes. Eight primitives/materials remain. Net +6 triangles, −4 bytes.
- Upper stage removes 106 overlay triangles and adds 106, retaining source112 glass/mullions. Lower stage removes exactly six pinned legacy triangles and adds twelve, six manually traced rectangles. Cumulative 112 removed / 118 added.
- Source112 upper field z≈90.804–163.436 m; lower-left field q=0..0.55, z≈75.240–90.804 m. Original ±5 mm lower-quad ownership is retained; no neighboring geometry clipped.
- All non-target mesh payloads, shell, roof, ground, materials, nodes and world transforms remain exact. T.P.15, 144 ground samples, zero missing samples retained. No source98/118, crown, podium or other building modification.

## Evidence and limits

Syced's CC0 photograph was taken December 1, 2025, after the October 2025 target. It supports a static architectural inference, NOT October certification. The affine q/z mapping and 5.188 m pitch are estimates, not surveyed storeys or calibrated photography. See source/refs/LOWER-PANEL-SOURCE.md and SOURCE-AND-INFERENCE.md for source URL, crop coordinates, license and bounds. Reference images are packed for review, not runtime textures. Original PLATEAU/OSM provenance and the inherited 2023 reference remain unchanged on main; no blanket license replaces their terms.

The native JPEG pairs in evidence/cumulative-v2/lower compare the exact main fixture to the final runtime with identical cameras, studio lighting and exposure. The folder name identifies the renderer's origin, not a lower-only baseline. comparison-main-final.jpg summarizes whole-facade and lower-field views. Model views are illustrative, not calibrated photographic registrations.

## Portable regeneration

Python 3 with numpy, from repository root:

    python3 assets/buildings/stream/source/blender/build-upper.py assets/buildings/stream/source/data/lower-panel-baseline/stream.glb
    python3 assets/buildings/stream/source/blender/build.py
    python3 assets/buildings/stream/source/blender/test-panel-rhythm.py
    python3 assets/buildings/stream/source/blender/test.py
    python3 assets/buildings/stream/source/blender/test-cumulative.py

Both input GLBs are bundled and hash-pinned. The upper generator is the preserved accepted source, with only its report destination changed to the upper fixture directory. It writes the same upper GLB and trace. Historical accepted-build.py.txt and fixture manifests are historical records, not current manifests. The lower generator is the accepted binary surgery. Neither route needs external ground files, an original checkout, network access or guessed missing binary data. Run in a working copy because generators write reports.

Exact Blender 4.2.3 (includes numpy):

    blender -b -t 2 --python-exit-code 1 -P assets/buildings/stream/source/blender/build.py
    blender -b -t 2 --python-exit-code 1 -P assets/buildings/stream/source/blender/render.py
    blender -b -t 2 --python-exit-code 1 -P assets/buildings/stream/source/blender/verify_blend.py

The editable scene contains final geometry, four cameras, embedded lower-stage source and packed CC0 references at relative paths. Reopened vertex/normal/triangle/transform parity is checked against a separate runtime import. Blend byte identity is not claimed. JPEG rendering is native, no geometry or reference-image generation is used.

## Validation scope

Original upper and lower assertions retained. Direct current-main cumulative validation additionally checks winding-sensitive triangle multisets, exact off-target accessor bytes, scene/material/node preservation and main Git blob identity. Existing nearby-buildings Stream roof/source-parent test and dedicated stream-cumulative-v2.test.ts budget/hash/metadata contract pass. Other assets are not loaded for this focused run; no whole-scene budget, build, browser, day/night, collision or owner-PC FPS acceptance is claimed.

No QFRONT, Seibu, 109, Takagi, Hikarie, walking display, FPS settings or shared runtime changes. Publication/merge/deployment are not performed by this package. Apply only listed delta files without deleting inherited files.
