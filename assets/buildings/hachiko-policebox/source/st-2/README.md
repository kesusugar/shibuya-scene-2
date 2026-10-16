# Shibuya policebox: visible façade study, v001

**Status: EXTERIOR_ONLY_ESTIMATED_UNPLACED**  
Reference date: **2025-04-09**. Prepared: 2026-10-16. This is not a claim about the October 2026 façade.

A standalone, shallow study of the photographed silver surround/canopy, bowed pale-green lined upper band, silver lower fascia, three independently observed cylindrical support locations and a removable lower doorway proxy. It does not contain the whole police station, an interior, a stairway, an underground passage or neighbouring station geometry. Nothing has been registered, placed, merged or deployed in the runtime scene.

## Files

- `policebox_visible_facade_2025_v001.glb`: self-contained model. No images or texture dependencies.
- `policebox_visible_facade_2025_v001.blend`: editable component-separated scene, including review cameras, lighting and a parametric-curve guide.
- `generate_policebox.py`: deterministic, parameter-driven geometry generator.
- `estimated_dimensions.json`: central dimensions and shape controls, with basis, confidence and `estimated: true` for every parameter.
- `renders/front.png`, `left_oblique.png`, `right_oblique.png`, `top_silhouette.png`: model-only views.
- `renders/estimated_regions_confidence.png`: teal source-visible component categories, orange inferred closure/hidden continuations. Teal does **not** mean surveyed dimensions.
- `SOURCE_REGISTER.md`: source links, dates, rights boundary and modeling provenance.
- `VERIFICATION.md`, `mesh_audit.json`, `glb_validation.json`: bounded visual and technical checks.
- `validate_glb.py`: read-only standard-library container/triangle check.
- `build.log`, `regeneration_no_render.log`, `source_support_correction.log`: initial build, single no-render regeneration and the source-backed lower-left support correction.
- `MANIFEST.sha256`: release-file checksums.

## Coordinates and parameter contract

Blender metres: x left/right, positive y toward the station, z up. The front faces negative y. The GLB exporter performs standard Y-up conversion. The bottom-centre anchor is local x=0, y=0, z=0 at provisional ground, not a geographic anchor and not a surveyed surface.

The nominal outer frame is 5.2 m wide × 6.6 m high. The small optional sign projects about 0.04 m above that nominal frame. All metric dimensions, depth and ground contact are provisional. The front curve is a 24-segment adjustable elliptical arc with a nominal 4.3 m chord and 0.8 m bulge, **not a measured semicircle**. No unrelated kiosk footprint was used.

The shallow lower closure is only 0.16 m thick. It can be removed as a collection, leaving the source-visible exterior. The rear upper aperture is a flat window/frame proxy; it is not a room. The space beneath the canopy and behind the bowed upper band is not filled by a whole-building box.

## Collections

- `SOURCE_VISIBLE_20250409`: observed component categories, all sizes estimated. The three support locations are not mechanically mirrored.
- `ESTIMATED_CLOSURE`: masked lower doorway/frame, threshold, hidden support foot and small hidden shell-thickness transition. Entirely removable.
- `REVIEW_ONLY`: cameras, lights, studio ground and curve guide. Excluded from GLB.

The plain `KOBAN` box/lettering is optional identity assistance, not an exact replica of the original sign. Exact emblems, advertisements, banners, notices and surrounding station copy are omitted. The pale-green horizontal lines are original procedural geometry. The physical surface is not certified as glass blocks or louvers.

## Regeneration

From the task workspace, use exactly the pinned Blender:

```sh
tools/blender-4.2.3-linux-x64/blender -b --threads 8 --python policebox_visible_facade_2025_v001/generate_policebox.py
```

For a no-render output in a separate destination:

```sh
tools/blender-4.2.3-linux-x64/blender -b --threads 8 --python policebox_visible_facade_2025_v001/generate_policebox.py -- --no-render --output-dir policebox_visible_facade_2025_v001/regenerated
python policebox_visible_facade_2025_v001/validate_glb.py policebox_visible_facade_2025_v001/regenerated/policebox_visible_facade_2025_v001.glb
```

Only Blender 4.2.3 and its bundled Python are needed for generation; the validation script uses Python's standard library. No network or photo file is needed.

## Integration boundary

Before/after here means **no separate façade study → this new standalone façade study**. It is not a rendered replacement of the existing scene. The bounded local asset check did not find a dedicated finished policebox asset, but it did not establish whether generic context faces already represent the same building volume. Before scene integration, identify those corresponding generic faces and a verified exterior anchor to avoid duplicate masses. Do not add a complete building shell simply to make this study watertight.

No QFRONT, Seibu Shibuya, pedestrian display, FPS, station/JR assets, loader, registration, budgets or global placement files were changed. No GitHub publication, external upload, merge or deploy was performed for this deliverable.
