# Mark City: completed cumulative WEST cap revision

One building only. Existing accepted EAST facade and roof repairs, WEST source240 ribbons and source299 lower bands, plus source235 cap dark 10×3 panel and two short glazed ribbons are preserved in this delivered final. No new modeling in this publication. Not a claim that the whole building is photographically complete.

Canonical runtime: web/mark-city.glb. Editable scene: source/west-cap-v1/source/blender/mark-city.blend. Final SHA256 8dc763dcd1e242de07f7846ba7789a40252c6efb0eed88d531faf6d1c3b4cd5d. 25,312 triangles, 28 primitives, 2,387,000 bytes, within unchanged level B budget. Current main: 23,908 triangles, 8 primitives, 1,458,728 bytes. Delta +1,404 triangles, +20 primitives, +928,272 bytes.

## Reproduce

With Blender4.2.3: blender -b -t 2 --python-exit-code 1 -P assets/buildings/mark-city/source/blender/build.py -- /absolute/output/mark-city.glb

The current stage is regenerated from packaged pinned before-cap GLB/stats, source geometry, scope and parameter JSON. No network or external Python dependencies beyond Blender NumPy. The predecessor includes cumulative earlier work; this is NOT replay of every earlier modeling stage from raw PLATEAU. Omitting output updates canonical runtime and canonical count metadata. The generated editable scene is an import of the exact GLB, not a promise that arbitrary manual edits export byte-identically. Adjacent packaged generator also works independently.

## Preservation and evidence

Geographical origin and T.P.15m datum remain unchanged. Original source ground samples, groundElevationTP=15 and shared C-parent exclusion remain unchanged. No other building, scene setting or runtime source is changed. Immediate cap step appends only190 triangles,3 meshes/nodes,2 materials; every predecessor payload byte, mesh, node, accessor and material remains exact.

See evidence/west-cap-v1/main-before-after.jpg for actual-main versus final from two identical cameras/settings. The original main fixture is source/main-baseline-v1/mark-city.glb. Comparison is asset-only Blender Workbench, not whole-scene/browser/FPS evidence. Tests: unchanged nearby-building targeted tests plus dedicated TypeScript runtime and Python cap conservation tests. The remainder of the multi-building test suite was not rerun.

## Sources and limitations

Source photograph Asanagi, June12,2025, CC0: https://commons.wikimedia.org/wiki/File:Shibuya_Mark_City_West_2025-06-12.jpg . Original included as source/west-cap-v1/source/refs/JUN12-west.jpg, already the same CC0 photograph in existing main. It is not used as a model texture. June does not prove October2025 appearance. Metric dimensions, colors and glazing counts are estimates; panel proxy is not evidence of actual vents, holes or interior. G2 photo association has a boundary uncertainty relative to source279; no neighboring face was moved to hide it.

SOURCE_AND_LICENSE_JA.md inside the source package preserves exact photo license and upstream provenance limitations. Existing PLATEAU/OSM-derived baseline is retained under its original conditions, not relicensed CC0. Complete asset-specific upstream license closure was not supplied; no blanket redistribution claim is made. Full-scene rendering, collision, walking and real-device FPS remain unproven. Historical179-test delivery claims are not current-main acceptance claims.
