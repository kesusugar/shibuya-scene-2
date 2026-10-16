# Attribution and derivative changes

Hachikō by Maurice Svay (https://sketchfab.com/mauricesvay).
Source: https://sketchfab.com/3d-models/hachiko-fffee43c3cbc4b7ea20d6556a360b25f
License: Creative Commons Attribution 4.0 International, https://creativecommons.org/licenses/by/4.0/ .
Legal text: https://creativecommons.org/licenses/by/4.0/legalcode.en .

The user supplied the original GLB and corresponding download ZIP. The preceding source inspection verified the public listing, embedded author/license/source metadata, and correspondence with the ZIP's original OBJ geometry. This package uses the exact uploaded GLB as its sole geometry, UV, material and texture source. The unchanged copy is `inputs/hachiko_source_unchanged.glb`, SHA-256 `053f4137aac044f6e16786c10fe888b6a39ac8e14256df33c9e28d1c342154be`.

## Changes made, 2026-10-16

- Removed only the extraneous pavement top ring and detached pavement perimeter/thickness, using identified original UV islands and exact-position-welded face-edge connectivity. Exact original removed face IDs are distributed in `source/trim_face_indices.json`.
- Compacted unused attribute records after face removal without welding, remeshing, decimation, sculpting, independent part movement, texture cropping or UV alteration.
- Applied the original root transform exactly once, then a plaque-derived horizontal rotation, one uniform estimated scale to the prior design height of 2.40559 m, and bottom-center translation based on the retained lower-course footprint. Full forward/inverse matrices are in `model/transform.json`.
- Rotated original vertex normals using the appropriate normal transform. No normal-map creation or recomputed smoothing.
- Preserved the exact original embedded JPEG bytes, UV float32 values and material JSON, including inherited metallic factor 0.25 and roughness 0.2. These material values are not a physically calibrated bronze/stone separation.
- Produced neutral studio renders, a same-camera comparison with the preserved prior handcrafted v001, an editable Blender 4.2.3 file, regeneration code and validation documents. No generated-image replacement or cosmetic retouching was used.

No underside cap or statue-opening repair was added. The source scan's documented small opening and one retained nonmanifold edge remain. Source photographic shading and weather-related highlights remain in the image atlas. Publication in January 2016 is not a certified capture date; this derivative does not establish the current plaza appearance.

Attribution and this description of changes must accompany redistribution, including project credits when copied into a larger project. The CC BY 4.0 attribution covers the scan derivative; no creator endorsement, metric survey accuracy or separate third-party rights clearance is claimed. The previous handcrafted comparison asset is a separate project artifact, not claimed as Maurice Svay's work. Its source remains unchanged and is not bundled into the candidate mesh.

## Runtime derivative for this project, 2026-10-16

The original canonical candidate is retained in project source. Runtime JPEG resized from 4096 x 4096 to 1536 x 1536 with Lanczos and encoded as JPEG quality 80, 4:2:0. Geometry, indices, UVs, normals and material parameters remain byte/value identical; only the material name changes to the project furniture class. The complete assembly is rigidly translated and yawed at runtime using an estimated OSM/project placement and sampled sidewalk fit. No nonuniform scale, sculpting or hole repair. Physical dimensions, photographic shading and scan openings remain limitations. Attribution: Hachiko by Maurice Svay, CC BY 4.0; source and license links above.
