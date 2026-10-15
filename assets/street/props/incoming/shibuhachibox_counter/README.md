# SHIBUHACHIBOX visitor-information counter

An **unplaced** model of the light-oak counter with its integrated left two-tier brochure rack. This is a furniture asset, not a reconstruction of the entire information pavilion.

## Delivery and orientation
- Blender 4.2.3 editable scene: `shibuhachibox_counter.blend`
- Embedded-texture glTF 2 binary: `shibuhachibox_counter.glb`
- Generator: `generate.py`; original procedural texture: `oak_grain.png`
- Model-only transparent-background inspection images: `front.png`, `side.png`, `photo_near.png`
- `validation.json` and `build.log` record the actual generation checks.
- Metres; bottom-centre origin; authored front is Blender **-Y**. glTF export uses standard Y-up conversion.
- Generate with Blender 4.2.3: `blender -b -t 2 --python generate.py -- /path/to/output`.
- No reference photo or extracted photographic pixels are redistributed. Texture grain is original deterministic procedural artwork, packed into the blend and embedded in GLB.

## Evidence and time boundary
1. JR East andtrip article, published 19 September 2024: https://www.andtrip.jp/article/006193.html . The interior photograph is the principal shape and colour reference: oak front/top, two recessed compartments at the left, pale backing, retaining bars and centre dividers.
2. CASIO PR article, 10 December 2024: https://note-pr.casio.co.jp/n/n848d1c101d53 . Exterior photograph provides context for the tourist-information zone, not reliable cabinet dimensions.

The model describes a counter visible in **2024** imagery. Its continued existence, position and appearance after subsequent construction have **not** been verified. It must not be labelled a measured 2026 survey. Source photographs remain with their respective publishers; no redistribution permission is asserted.

## Explicit dimensional estimates
- Counter: width 2.40 m, depth 0.56 m, height 0.98 m. Plausible uncertain envelope from perspective photo: width 2.2–2.6 m, depth 0.45–0.65 m, height 0.90–1.00 m.
- Rack clear width 0.57 m; two open tiers with approximately 0.31/0.33 m clear height.
- Top thickness 45 mm; stiles 70 mm; front veneer assembly 34 mm; approximately 130 mm rack recess. These are modelling estimates, not measured construction specifications.
- Rail thicknesses, bevels, finish and rear/bottom shell are provisional. A simple closed rear is supplied to avoid an open mesh; no hidden storage hardware, hinges or drawers are invented.
- The known pavilion room height does not remove perspective and unknown depth ambiguities. No claim of survey-scale precision is made.

## Photo comparison / intentional exclusions
The photo-near render aims to reproduce the reference's elevated front-right viewing angle, not a solved calibrated camera. Compare the front/top proportions, left rack fraction, two-tier division, pale recess, thin horizontal rails and vertical wood grain. The source photograph contains promotional posters, leaflets, maps, computer, mascots and a large background monitor. Those are intentionally **not** part of this asset; their absence is not evidence that the real counter was bare. Advertising and paper artwork should be dated and sourced independently before a separate overlay asset is made.

The rack has three horizontal retaining bars per tier and a central divider; empty compartments make its construction inspectable. Its exact small fasteners and brochure support mechanism cannot be resolved from the available image.

## Integration handoff
Use in the information-service part of SHIBUHACHIBOX, not the left gallery bay. The parent transform and exact placement belong to the scene integration owner (Codex). Do not replace unrelated counters or add a duplicate without checking the existing scene. No runtime placement, collision, walking/FPS, QFRONT or Seibu code was modified.

## Validation limits
Generator validates finite coordinates, 2.40 m width, 0.98 m height, base at Z=0 and a triangle ceiling of 8,000. Asset is intended for standard glTF PBR, with two materials and one embedded PNG. A separate GLB structure check is included. Render and authoring-rig lights/camera are excluded from the exported asset. Actual Three.js/browser integration and placement are not claimed by this isolated deliverable.

## Reproduction check
A second build in a separate output directory, using Blender 4.2.3 with `COUNTER_SKIP_RENDER=1`, reproduced the GLB, original oak PNG and geometry-validation JSON byte-for-byte. `regeneration_validation.json` records both SHA-256 values. Full render generation remains the default; this optional environment variable skips only the three preview renders. The maximum overall depth including projecting rails is 0.564 m, rather than the 0.560 m cabinet top depth.

## Final two-batch export
The GLB contains **two meshes / two primitives**, one for oak and one for the pale rack. The blend retains 27 independently editable parts. `batch_export.py` directly combines the canonical exporter accessors by material, baking translation only; it preserves the source normals, UVs, triangle winding and material assignment exactly. `batch_identity.json` records exact float32 world-space triangle identity against the pre-batched model. The original front/photo-near PNGs therefore remain valid geometry previews. `glb_reimport.png` is a fresh render of the final GLB after importing it into Blender; the corrected `side.png` also uses the imported final GLB and gives full top/bottom margins.

To export edited blend contents with the same batching route, run Blender 4.2.3 with `--background --python export_editable.py -- /path/to/output.glb`. A direct editable export and independent generator output both reproduce the final GLB byte-for-byte in the unchanged delivered asset. Keep `batch_export.py` next to the generation/export scripts. `verify_batch_semantics.py /path/to/prebatch.glb` is an audit utility requiring the pre-batch baseline; it is not required for normal regeneration. The scene's actual draw-call count and FPS are still integration-dependent.
