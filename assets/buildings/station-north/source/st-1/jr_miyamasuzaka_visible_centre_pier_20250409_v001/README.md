# JR Miyamasuzaka visible centre-pier cladding

One small, standalone **2025-04-09 exterior candidate**, not a complete pier or entrance. Front pale cladding, shallow right return and two clearly source-visible lower green/white edge bands only. No photograph or crop is packaged.

- Nominal, **unmeasured** envelope: **2.2 m wide × 4.2 m high × 0.20 m deep**.
- Origin: bottom centre `(0, 0, 0)`. Blender: Z up, front −Y; GLB: Y up, front +Z.
- One open L-shaped surface mesh, 68 triangles, three flat PBR materials, no textures. Double-sided by design; no back, left wall, top, underside or hidden structural core.
- Edge protection: independent diagonal material geometry, no reproduced poster artwork. Width 0.17 m, height 2.73 m and stripe spacing are approximate visual interpretations, not measurements.
- GLB contains only the asset. The Blender file also contains a clearly named preview-only studio collection. Import/export the `ASSET_export_only_this_collection` collection, not the studio.
- Existing fascia, canopy, entrance, buildings and supports are unchanged. This is unplaced and not fit-ready. If a later scene overlap is found, reuse/refine the existing part instead of stacking a duplicate.

## Files

- `model/*.glb`: standalone asset.
- `model/*.blend`: editable Blender 4.2.3 LTS scene.
- `source/build_centre_pier.py`: procedural source, no external dependencies beyond Blender.
- `source/check_glb.py`: small standard-library actual-buffer validator.
- `evidence/front_oblique.png`: one studio preview, no source-photo pixels.
- `SOURCES_AND_ESTIMATES.md`: reference and uncertainty record.
- `validation/glb_checks.json`: final actual-buffer checks plus one clean regeneration comparison.

Regenerate with Blender 4.2.3:

`blender --background --factory-startup --python source/build_centre_pier.py -- --out /your/output/directory`

Validate with ordinary Python:

`python source/check_glb.py model/jr_miyamasuzaka_visible_centre_pier_20250409_v001.glb`

The preview is model-only, not an on-site placement comparison. No interior, underground connection, floor, ceiling, ticket gates, services, structure, footing, posters, signs or full facade were made. No runtime integration, collision, scene placement, GitHub changes, merge or deployment are part of this package.
