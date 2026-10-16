# Hachikō scan candidate v001: local alternate review

## Result

A separate GLB and editable Blender 4.2.3 LTS candidate are ready for review. The complete statue, paws/tail with their bronze seat, main stone, plaque and lower tiled course are preserved. Only surrounding pavement was removed. Front and front-oblique actual renders show the preserved full base and clean removal of the extraneous skirt.

This is an alternate, not a production/runtime substitution. Existing v001 and the uploaded originals remain unchanged. No world placement, collision, performance, QFRONT, Seibu, walking-display, FPS, repository, merge or deployment work was performed.

## Safe trim, not a height cut

The pavement-top ring is a complete original UV-connected component containing source triangle 3: 8,072 faces. After removing that ring, face-edge connectivity on analytically exact-welded positions identifies the statue/base component. This excludes 3,151 remaining pavement perimeter/thickness faces, including one nearly collinear pavement sliver touching the lower course only at a single vertex. The analysis weld does not modify the output geometry.

- Source: 97,157 triangles / 56,273 position–UV–normal records.
- Removed: 11,223 original pavement triangles.
- Retained: 85,934 triangles / 49,256 attribute records.
- All four lower-course wall UV islands are retained completely; no UV island is partially cut. Every removed face lies below source-world Y = −1.6642061, but that height was not used as the cut rule.
- The new underside boundary is one closed 371-edge loop, with degree two at every loop vertex. No underside cap was added.
- Output is one connected component after exact-position analysis, with 378 boundary edges: 371 at the new underside plus the inherited 7-edge statue opening. One inherited nonmanifold edge near the bronze seat/foot region remains.

`source/trim_face_indices.json` records the exact original face IDs and lower-course origin mask. `validation/seam_assessment.json` provides the detailed tests. The original UV/material/texture data are retained rather than reprojected, reconstructed or baked.

## Reversible, uniform estimated scale

The source root matrix is applied once. Plaque-derived front/right axes determine orientation; the retained lower-course horizontal bounds determine its center, and the lowest retained point determines bottom height.

- Retained source height: 4.845029309254364 scan units.
- Uniform scale: 0.49650680036241385.
- Provisional design height: 2.40559 m, inherited from the earlier project estimate, not an on-site measurement.
- Candidate bounds, width × depth × height: 1.0706329 × 1.6644914 × 2.4055901 m after float32 storage.
- Bottom-center origin: effectively (0, 0, 0). glTF +Y up / −Z front; Blender +Z up / +Y front.
- All output object transforms are identity; the one whole-assembly similarity transform is baked and recorded in `model/transform.json`, together with inverse matrices.

No independent width, depth or statue-height adjustment was made. Matrix inversion recovers retained source geometry within float32 precision; restoring deleted triangles requires the bundled unchanged source GLB.

## Essential validation

- Embedded 4096×4096 JPEG: byte-identical to uploaded GLB, 5,109,884 bytes.
- UV float32 values and source material JSON: exact for all retained records.
- Original face ordering/winding and attribute correspondence: preserved.
- Maximum output-position rounding: 1.192 × 10⁻⁷ m; inverse-transform error: 2.407 × 10⁻⁷ source units.
- Zero-area triangles: zero. UV/position values: finite.
- One deterministic regeneration: GLB is byte-identical, SHA-256 `cd20601d57308a1b50892c05d509a6295ca24ca2045cfd37421995a840bf039e`.
- Blender 4.2.3 imported the actual delivered GLB, saved and reopened the editable BLEND with equal geometry, UV and normal digests.
- Editable-file cleanup removed only unused legacy-comparison datablocks. Final BLEND contains one scan mesh, one source material and one packed source JPEG, plus review camera/lights. No comparison mesh or redundant legacy textures are bundled.
- Originals and prior v001 GLB/BLEND hashes still match their preserved values.

One build, two scan renders, one same-camera legacy render, and one GLB regeneration were performed. There were no repeated shape or cosmetic trials. A harmless Blender extension-cache warning concerned a read-only configuration directory; the asset save and reopen checks passed.

## Review evidence and limits

`evidence/legacy_vs_scan_front_oblique.png` compares the unchanged prior v001 against the new scan with the same camera, lighting, framing and estimated total height. It does not use the held/non-adopted handcrafted v002. The comparison geometry is not included in the new GLB or BLEND.

The scan's source photographic shading, weathered highlights, softness in some facial detail and leaves on the retained lower-course top remain. The inherited metallic factor 0.25 and roughness 0.2 apply to the complete scan, including stone; they are not calibrated physical material values. No source statue-opening repair, global leveling, base flattening or underside closure was attempted. The retained bottom rim varies by about 0.058 m in height at this provisional scale. A flat-ground fit is not established.

Only front and front-oblique views were visually reviewed. Back/underside fidelity, watertightness, self-intersections, present-day plaza appearance, real metric dimensions and runtime performance are not certified. The source was published in 2016; its capture date is not established.

Hachikō by Maurice Svay, CC BY 4.0. Keep `PROVENANCE.md` with the derivative and retain attribution in any project distribution.
