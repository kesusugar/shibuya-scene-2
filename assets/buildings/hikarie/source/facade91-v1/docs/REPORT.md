# Source91 bounded upper cleanup: validated asset

## Recommendation after actual-pixel comparison
Prefer **V3 selected upper-overlay cleanup** over the material-only variants for visual evaluation. V1 improved the pale-vs-blue facade hierarchy but preserved an obvious raised grid. V2 gave the selected frames/spandrels a separate brighter matte material (base color0.92/0.92/0.90, roughness1, metallic0); its actual render still has almost the same coarse shadows. The grid's geometry, not only color, was the main remaining mismatch.

V3 exposes the existing opaque pale shell only under the already-selected upper overlay triangles, retaining the estimated dark vertical bay and unknown lower rows. The full-building view and fixed-camera close view show a materially quieter pale field, closer to the June2025 photograph. This is the least invasive *visually effective* option tested: only906 of1110 source91 overlay triangles are omitted, no replacement panel grid is invented, all original shell vertices and triangles remain. It is not a whole-face plain wall substitution.

**Bounded asset validation passed; physical-material and photographic-fit uncertainty remains.** Lower dark rows remain visually conspicuous and unresolved; source91's true material substrate, opening details, subtle panel joints, and upper contour remain approximate. The original asset-isolated lighting also produces a localized triangular shadow near the upper dark bay. No invented emissive material was used to disguise geometric shadows.

## Inspection artifacts (paths relative to evidence/ unless stated)
- `front-before-after.jpg`: accepted baseline / final selected cleanup, same saved full-building camera.
- `photo-before-after.jpg`: actual June2025 photograph / baseline / final selected cleanup, fixed saved model-camera crop.
- `front-after.png` and `photo_jun15_angle-after.png`: actual Blender4.2.3 Cycles16 candidate renders, pixel-inspected.
- `web/hikarie.glb`, `tools/regenerate.py`: local candidate and deterministic builder.
- `evidence/portable-validation.json`, `tools/validate.py`: bounded preservation checks.
- `source/overlay_contract.json`: exact906 removed and204 retained overlay triangle indices; these are index-accessor removals, not recoloring.

## Shell coverage and preservation
The original source91 shell is material `hikarie_wall`: OPAQUE, alpha1, baseColor approximately[0.64,0.66,0.66], metallic0, roughness0.8. Original triangles129/288 span four rectangle corners and share exactly one diagonal. Their area1637.8671875m² agrees with existing source rectangle19.067126317×85.9=1637.866150656m² to0.00104m² floating-point difference. There is no hole needing replacement geometry; exposing it does not rely on a guessed fill plane.

V3 preserves the entire original binary payload unchanged as a prefix and all material definitions unchanged. It changes only index accessor lists for the five source91 overlay-containing meshes, removing the exact906 previously identified triangles;204 source91 overlays remain. All non-target meshes are identical. Source91 shell, roof0 repair, source90 repair, source63, corner71/82, every geographic boundary and elevation, and all other surfaces are preserved. Unused original index bytes remain harmlessly in the binary; this prototype prioritizes reversibility over byte optimization.

Budget:30,562 triangles,15 primitives,2,349,752 bytes, below the existing B limits. Scoped copied-assembly validation passed 178 tests, two Stream assertion scripts, type checking, build and actual asset-loader day/night/day checks. This is not a latest-main or full-scene validation. The pinned predecessor is SHA25614cb88b7d3870512c23a750e7b9f701e85dc184cc1d473954725b6c138a0749d.

## Boundary estimates and uncertainty
Same bounded region as V1/V2: source91 frame origin(277.214,-24.125,0), tangent(0.946393269,0.323016688,0), u0..19.067126317m, z101.1..187m. Only existing source91 overlay triangles with every vertex z>=112m, except centroid u3..4.6m, are removed.

- Actual pale-opening extent is quantized to existing triangles. Glass removal begins z116.7417984m; frame removal begins z113.5602951m. Top glass ends186.5649719m. Exact ranges are recorded in V1 validation; no source boundary is moved.
- Retained dark glass bay occupies u3.2378272..4.7067683m, z116.7417984..186.5649719m. A narrow dark feature is observable in June2025 and December2024 pictures; its interpreted position has a working uncertainty ±2m and width is quantized to one original bay. This is not a statistically calibrated fit or identification of glass versus recess/joint.
- Re-inspected the full June2025 photograph, not just the crop. Source91's lower end is hidden by the TOSEI sign/building. The independent December2024 image also hides it. Consequently the two retained lower rows cannot honestly be described as photo-proven pale or photo-proven glass. They remain inherited unknown geometry. Lower transition uncertainty is at least one inherited row (~5.4m), and no extension through occlusion is claimed.
- Exact silhouette and metric camera fit remain unsolved. Existing source geometry is the boundary constraint. No new camera calibration, floor count, or manufactured survey residual is presented.

## Sources and rights
Board photograph: Nesnad,2025-06-15,CC BY4.0, https://commons.wikimedia.org/wiki/File:Hikarie_and_Shibuya_scramble_square_buildings_2025_June_15.jpeg . License https://creativecommons.org/licenses/by/4.0/ . Existing crop plus rectangular detail crop/resize only. Original reports panorama/TouchRetouch processing. No texture derived, and June is not October2025 temporary-condition proof.

Independent visual corroboration: 武石修, article published2024-12-28, https://www.watch.impress.co.jp/docs/topic/1650501.html , image008 https://asset.watch.impress.co.jp/img/ipw/docs/1650/501/008_o.jpg . Actual capture date unspecified, EXIF absent; publication is only an upper date bound. No reuse license established, so that image is NOT included in these boards/files. Official manufacturer drawings/text did not register material to source91; no GRC/metal/glass substrate claim is made.

The original model and earlier variants are preserved. Blender reported a read-only configuration-cache warning; rendering and save/reopen validation completed successfully. Packaged logs normalize machine-specific paths without changing recorded outcomes.


## Production packaging addendum
The selected V3 upper-overlay cleanup was validated for exact906 removals/204 retention. Shadow-ray checks identified the upper-left triangular mark as an original roof-cast shadow from roof triangle13 onto shell triangle129, not a hole. This package adds a stdlib-only relative generator, explicit removal/retention contract, and Blender4.2.3 editable scene with strict import/save/reopen geometry/normal/material signature parity. Full/front, west-side and photo-angle A/B images are supplied. No original asset was changed during preparation. Portable byte-exact regeneration, editable-scene parity and scoped copied-assembly verification passed. Only the historical scene status property and matching script string were updated to neutral validation wording. Meshes, normals, indices, transforms, materials, cameras/lights and model bytes are unchanged. Current validation status is recorded in this report and the contract.
