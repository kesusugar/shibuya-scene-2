# SHIBU HACHI BOX counter wall monitor · v001

One unplaced, reference-informed landscape monitor behind the visitor-information counter. This handoff trial contains no full scene, placement code, repository changes, GitHub publication, merge, deployment, walking/FPS, QFRONT or Seibu changes.

## Fixed scope

A thin continuous charcoal bezel, recessed neutral 16:9 display and plain closed rear cover. The dark upper and lower bands in the reference are video letterboxing, not oversized physical bezels. Screen content, logos, text, cables, ports, vents, screws, stands, mounting brackets, wood wall panels, air conditioner and the counter itself are intentionally excluded. The photo does not establish hidden hardware.

The neutral screen is an intentional fidelity boundary: its surface and proportions are modeled, but no source-video pixels or invented interface are included. The source shows the screen on; this delivered neutral/off appearance is not a claim that it was actually off.

## Files and regeneration

- `shibu_hachi_counter_wall_monitor.glb`: two standard-PBR material batches, no lights/cameras, images or external dependencies.
- `shibu_hachi_counter_wall_monitor.blend`: three named editable components and a separate inspection rig. All resources are self-contained; packing is invoked, but there are no external textures to pack.
- `generate.py`: self-contained Blender Python, standard library only.
- `renders/front.png`, `side.png`, `oblique.png`: transparent model-only views.
- `provenance.json`, `attachment_hint.json`, `duplication_check.json`: evidence and placement boundaries.
- `metadata.json`, `validation.json`, `build_stats.json`, `timings.json`, `MANIFEST.json`, `logs/build.log`: verification, measured build/render times, and hashes.

With Blender 4.2.3, run:

    blender -b -t 2 --python generate.py -- /absolute/output/directory

Add `--skip-render` after the directory to export without inspection renders. No downloads, add-ons, installed fonts, photographic pixels or adjacent assets are required. The original delivery was built using Blender 4.2.3. Rebuilding from the supplied generator is supported, but a second independent regeneration was not run during this deliberately bounded trial.

## Coordinates and estimated dimensions

Metres; Blender Z-up, front -Y; GLB standard Y-up. Root is at the bottom-centre of the complete cabinet, `(0,0,0)`. Width 1.550 m, height 0.900 m, total depth 0.070 m. Screen width 1.506 m and height 0.847125 m are a nominal 16:9 approximation. The screen is recessed 6 mm behind the foremost rim. Small bevels, rear taper, reflectance and cabinet depth are estimates, not manufacturer measurements.

Plausible dimension range from this single perspective photo: width 1.35–1.75 m, height 0.78–1.02 m, depth 0.04–0.10 m. The estimated 2.40 m counter helps scale the scene but is itself not surveyed. The upper-right monitor region is partly clipped by the photograph. No product model or exact display diagonal has been identified.

## Evidence, date and rights

Primary: JR East and trip, published 19 September 2024, “渋谷のことは何でもおまかせ！忠犬ハチ公像目の前の観光案内所【SHIBU HACHI BOX】”.

https://www.andtrip.jp/article/006193.html

Direct image: https://www.andtrip.jp/images/5e2dce4101b447931b7a0e70afda38d6ab3ff4ad.jpg

This is a 2024-reference variant. Presence and arrangement in 2026 have not been verified. Source-photo copyright stays with the original rights holder. The source photograph and derived crops are not redistributed. `provenance.json` supplies pixel coordinates for private comparison.

## Duplication and integration limits

The available local pavilion architecture, counter, header and placard sources/assets were checked. No counter wall-monitor geometry was found; the counter README expressly excludes the large background monitor. The parent also verified that the matching incoming directory is absent on main 92f6b3479f62ced9412ef8d73016fab5291595f8. These bounded checks do not prove that no similar differently named object exists in the live scene.

`attachment_hint.json` gives an explicitly tentative counter-local offset and one derived hypothetical pavilion-local offset. These are starting hypotheses only. World position is null. The integration owner must verify the actual counter and wall, clearances, date scenario, duplicate suppression and final orientation before placement. No runtime placement has been performed.

## Validation boundary

The final frozen asset receives one structural/geometry/material validation pass and visual inspection of all three final previews. Native GLB PBR is used with no screen emission, transmission or photographic texture. Successful isolated validation does not establish actual Three.js draw calls, FPS, collision, geographic alignment, scene lighting or integration quality.

## Frozen result

Final validation passed all 18 checks. GLB: 26,604 bytes, 520 triangles, two meshes/primitives and two materials. The blend retains three editable pieces. No model changes or re-render cycles were required. See `timings.json` for the actual elapsed trial duration and per-stage UTC times. The single-object screen batching operation produced a harmless join warning; the final imported geometry and primitive count passed validation.
