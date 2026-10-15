# SHIBU HACHI BOX counter laptop, 2024-reference prop

An unplaced, editable model of the open laptop visibly standing on the right side of the visitor-information counter. It is **temporary movable counter equipment**, not a permanent pavilion fixture or verified present-day landmark. No manufacturer or model is asserted.

## Contents
- `shibu_hachi_counter_laptop.glb`: 258,516-byte glTF 2 binary with three material batches, 8,904 triangles and no external dependencies.
- `shibu_hachi_counter_laptop.blend`: Blender 4.2.3 LTS scene with 80 separately editable parts. All mesh origins are the common bottom-centre datum. Packing was invoked; materials are plain PBR, so there are no image files to pack.
- `source/generate.py`: deterministic modelling/export script requiring only Blender 4.2.3. No downloaded geometry, fonts, photographic textures or plug-ins.
- `renders/photo_near_rear.png`, `renders/side.png`, `renders/operator_oblique.png`: 900 × 750 transparent-background inspection images rendered by reimporting the delivered GLB. These are model-only views, not a calibrated photograph match.
- `provenance.json`, `build_stats.json`, `qa/`, `PRODUCTION_LOG.md`, and `MANIFEST.json`: evidence, dimensions, checks, timing and hashes.

Generate: `blender -b -t 2 --python source/generate.py -- /absolute/output/directory`.
Render and round-trip check: `blender -b -t 2 --python source/render_validate.py -- /absolute/output/directory`.
Structural check: `python source/check_glb.py /absolute/output/directory`.
Editable-file check: `blender -b -t 2 --python source/check_blend.py -- /absolute/output/directory`.
Use the exact Blender 4.2.3 release. The output directory should have `renders` and `qa` subdirectories for the checking scripts.

## Actual evidence and duplicate check
Primary source: JR East andtrip, [SHIBU HACHI BOX article](https://www.andtrip.jp/article/006193.html), published **19 September 2024**, with photograph labelled 店舗カウンター. The page and original 800 × 600 image were actually inspected. The approximate laptop area is x=542–689, y=273–357. Capture date is not given. The article identifies the counter, not the laptop manufacturer or dimensions.

Visible cues retained: a thin warm-metal rounded rectangular lid, nearly upright open posture, soft manufactured edges and a narrow darker hinge/base edge. The previous counter asset explicitly excludes its computer. The pavilion and other completed detail generators were checked; this object does not duplicate the wall monitor or front information placard.

Source photo and all photographic pixels remain with the publisher. No reuse licence was established. **Do not upload the source photo or a crop as part of this asset.** These files contain only newly authored geometry/materials and model-only renders. The photographed rear stickers and emblem are deliberately omitted, not replaced with invented branding. Maps, pamphlets and the adjacent tabletop sign are not included.

## Dimensions and confidence
All dimensions are estimates, not a measured product or survey:
- Open envelope: **0.304 m wide × 0.247729 m deep × 0.219934 m high**.
- Base nominal footprint: 0.304 × 0.212 m.
- Lid height: 0.207 m; shell thickness: 5.8 mm; lean: 12° from vertical away from the operator.
- Plausible broad width range: 0.28–0.36 m; base depth: 0.19–0.25 m; open height: 0.19–0.26 m. These ranges communicate photographic uncertainty, not a statistical estimate.
- The scale uses the overall counter-photo proportions; the reference has no ruler, calibrated camera, reliable product identification or unobscured base outline.

The **operator-side display, bezel, key arrangement, trackpad, underside, feet and most base depth are occluded** in the photograph. These are restrained, explicitly labelled generic closure geometry, not claimed observations. Key legends and screen UI are absent. The neutral dark screen does not assert whether the real machine was on or off. Ports, cables, badges, screws and a specific product keyboard layout are not invented. The warm metal tone is affected by the source's warm interior illumination and is not a calibrated finish colour.

## Orientation and integration
Metres, Blender Z-up; standard glTF Y-up conversion. Common origin is the **bottom centre of the full open envelope**, not the base-footprint centre or hinge. Visitor-facing lid back is Blender **-Y**, operator side is **+Y**. The model rests at Z=0. The counter photo suggests the right-hand countertop as a candidate location only; no placement transform or attachment is encoded. Check date, position, orientation and duplication before scene integration.

No loader, runtime registration, collision, walking/FPS, QFRONT, Seibu, existing asset, GitHub, merge or deployment changes were made. No claim of current 2026 presence or full Three.js/browser performance validation is made.

## Validation
Final GLB structural check passes finite coordinates, unit normals, legal indices, no zero-area triangles, three meshes/three primitives/three materials, bottom-centre bounds, no external URI, no camera/light and no required extensions. Blender reopening verifies all 80 editable meshes, per-part evidence labels, metre units, applied modifiers and no external data dependencies. GLB reimport verifies final bounds and generates all three previews. See the production log for the initial issues corrected before the final freeze; unchanged successful stages were not repeatedly run.
