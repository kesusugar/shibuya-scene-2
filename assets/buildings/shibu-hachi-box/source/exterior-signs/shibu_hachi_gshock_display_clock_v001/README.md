# SHIBU HACHI BOX giant display clock · A15 / H-SG-006

Source-based, independently authored reconstruction of the giant G-SHOCK-design exhibition clock in the pavilion's left display bay. This is the enlarged watch **head and display stand**, not a normal wearable wristwatch. No full strap, buckle or loop has been added.

## Delivered asset

- `shibu_hachi_gshock_display_clock_v001.glb`: consolidated render asset, five material batches, embedded original face texture.
- `shibu_hachi_gshock_display_clock_v001.blend`: editable separated components in Blender **4.2.3 LTS**, packed original image and fonts, no external library links, cameras or lights.
- `source/make_artwork.py`: original printed face artwork generator (Python + Pillow).
- `source/generate.py`: deterministic geometry/export/evidence-render generator for Blender 4.2.3.
- `source/validate.py`: source mesh and GLB reimport checks.
- `textures/`: independently drawn face artwork and its metadata, not a photograph or photo crop.
- `fonts/`: redistributed DejaVu fonts with their license.
- `evidence/01_front.png`, `02_back.png`, `03_oblique.png`, `04_rear_oblique.png`: renders of the **exported GLB**, with no photography in the image.
- `PROVENANCE.md`, `component_estimates.json`, `placement_hint.json`, `ledger_handoff.json`, `manifest.json`, `timings.json`: source evidence, explicit estimates, validation and handoff records.

## Coverage

The model covers H-SG-006 only: thick black clipped-corner body, layered face inset, short lug stubs, the observed lower-lug circular recess, four side controls, independently drawn dial and seven-segment LCD, pale bezel labels, silver-finished rear plate, circular six-notch screwback, legible major rear lettering including boxed 240 and DW-5000, twin supports, triangular gussets and flat base.

The rear text is shallow decorative relief using neutral open-license font contours, **not exact proprietary lettering or measured engraving**. Tiny unresolved face microtext is deliberately omitted rather than invented. The stand's concealed fastening, actual construction and internal clock mechanism are not established.

## Date and appearance

The geometry is interpreted from official November/December 2024 installation photography. The same design is visibly present in a photograph captured **2026-08-08 at 08:08:08**. The static authored LCD reads `SA`, `8-8`, `AM`, `8:08:08`, with no leading zero on the displayed hour, matching that dated snapshot. It is not a live clock and is not a claim about the current date/time.

The later daylight photo supports a pale gray/green LCD with dark digits. Cyan reflections from the 2024 promotional photograph are not baked into the albedo. Material colors, roughness, metallic response and engraving depths are inferred, not physically sampled measurements. Metallic-looking surfaces do not establish the material of the full-size sculpture.

## Coordinate contract

- Units: metres.
- Origin: bottom-center of the complete display's common floor base.
- Blender axes: +Z up, **-Y front**; glTF uses the standard Y-up conversion.
- Complete dimensions: **1.74 W × 0.68 D × 2.25 H m**, estimated.
- Nominal head: approximately **1.60 W × 1.80 H m**, including controls; approximately 1.125 H/W, consistent with the source-derived ~1.13 ratio.
- Visible support height: approximately 0.45 m, about 0.28 head widths.
- World position, yaw and installation height: **null / unresolved**. The asset is not placed in the production scene.

Place semantically in SHIBU HACHI BOX's left exhibition bay, facing outward through the short-end window toward the crossing; rear toward the gallery. Calibrate against an approved pavilion bay and dated scene before setting dimensions or transforms. Do not silently use this file to replace another scene object.

## Rebuild and check

1. Run `python source/make_artwork.py` if changing the authored dial. This requires Pillow and the bundled fonts.
2. Run `blender-4.2.3 -b --python source/generate.py` to rebuild GLB, packed editable blend and all four views.
3. Run `blender-4.2.3 -b --python source/validate.py -- /absolute/path/to/this/package`.
4. Use `--no-render --output /another/directory` after `generate.py --` for a clean regeneration without the inspection images. The generator reads only its bundled artwork/fonts, not the reference photographs.

The renderer staging scene is deliberately not saved in the editable model. All renders are made by reimporting the same GLB that is delivered.

## Important limits

Exact metric dimensions, body thickness, hidden top/underside details, opposite-side control construction, stand fixings and October 2026 persistence are unconfirmed. This is a visual exhibit asset, not product CAD, a fabricated structure, a collision mesh or a working timepiece. Decorative font cleanup may leave degenerate-area boundary edges, which are reported; zero-area triangles are prohibited and checked. The asset comprises intersecting closed components, not a single boolean-unioned watertight solid.

H-SG-004 roof sponsorship, H-SG-005 fence advertising and H-SG-007 exhibition walls/floor/side advertisements remain separate and untouched. No pavilion shell, QFRONT, Seibu Shibuya, pedestrian display, FPS code, runtime, Codex environment, GitHub, merge or deployment changes were made. Private Drive upload is handled separately by the parent task.

## Final QA outcome

32,395 triangles; five GLB material batches; one embedded original texture; zero degenerate triangles. All structural shells are closed. Decorative lettering has 39 boundary edges after cap cleanup, recorded in validation. Source regeneration in a relocated directory is exactly identical after canonical triangle ordering, including normals and UVs; raw vertex/index order can differ. Direct export from the packed editable blend is byte-identical. See `evidence/reproducibility.json`. No copyrighted reference photo is needed to rebuild.
