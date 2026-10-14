# Four-building preserved-coordinate review

## Scope and result
Actual Blender 4.2.3 renders combine exactly eight explicit GLBs: the latest West ground-floor storefront revision, Daiichi-Kangin/UC, final Ekimae sign alignment, and frozen Center244 geometry, each with its selected dated sign layer. All four geometry inputs retain their original XY coordinates. No model, runtime registration, protected QFRONT/Seibu asset, remote branch or GitHub state was changed by this review.

**This is an isolated asset assembly, not a full scene or a single-date reconstruction.** West, UC and Center244 January 2025 ads coexist with Ekimae November 2025 ads for review only. Center244's January layer is explicitly imported by this script despite being intentionally absent from its runtime viewer registration. No terrain, road, plaza, surrounding buildings, or runtime collision mesh is included. Grey space is the Blender world background, not ground. The latest West ground-floor storefront geometry is present in full.

## Reproduction and provenance
`assembly-input-manifest.json` lists the exact twelve input files (eight GLBs and four viewer JSON files), original source paths, byte sizes and SHA-256 hashes. Rendering verifies every hash before import and asserts exact Blender 4.2.3. The script contains no asset glob. Import conversion is the same as the prior three-building review: native glTF axes converted by Blender, then Z shifted by `groundElevationTP - 15`. There is no XY translation, rotation, scaling or recentering.

From the isolated project root:

```sh
/workspace/shared/blender423/blender-4.2.3-linux-x64/blender -b -t 4 --python-exit-code 1 -P evidence/west-four-building-assembly/render-assembly.py -- "$PWD"
python evidence/west-four-building-assembly/make-board.py
./node_modules/.bin/vitest run tests/west-block.test.ts tests/daiichi-kangin.test.ts tests/ekimae.test.ts
./node_modules/.bin/tsc --noEmit
```

Render settings: Cycles CPU, 32 samples, denoising, AgX, orthographic cameras, 1800×1400. Day-review emission is disabled only in the transient Blender scene. `make-board.py` adds explanatory captions and building callouts without altering the geometry render. `label-projections.json` records camera-projected label anchors.

## Spatial check
All six building-pair AABBs are disjoint using actual imported world-space mesh vertices, not viewer-plan approximations. Therefore none of these four rendered assets can intersect another in this coordinate frame. This is not a runtime collision or road-clearance certification. No overlap-triggered triangle contact check was necessary; the script includes a BVH surface-contact diagnostic if a future input does overlap, with a solid-containment caveat.

Separating axis gaps:
- West–UC: X 2.340004 m.
- West–Ekimae: Y 29.528214 m.
- West–Center244: Y 15.154984 m.
- UC–Ekimae: X 1.796005 m and Y 28.803369 m.
- UC–Center244: Y 15.967983 m.
- Ekimae–Center244: Y 80.231477 m.

These are axis separations, not pedestrian clearance measurements. Complete bounds and signed interval overlaps are in `assembly-bounds.json` and `pairwise-aabb-check.json`.

## Focused validation
12/12 tests pass across the current West, UC and Ekimae focused suites. TypeScript `tsc --noEmit` passes. The strict current West test was copied from `/workspace/shared/west_storefront_review/tests/west-block.test.ts`; it correctly expects the revised east extent −32.535484 m at unchanged 0.5 mm tolerance. An initial test run using the older three-building snapshot is retained as `tests-historical-snapshot.log`; its superseded −32.510506 m assertion is not a current failure. No assertion was weakened here. Test input provenance is recorded separately.

Center244's own tests and concurrent neighbourhood validation are owned by its separate finalization work, not rerun or modified by this review. Full project tests, Vite bundle, fullscene startup/render, terrain anchoring, road/plaza interactions, runtime collision, owner-PC FPS and photographic/geodetic accuracy remain unverified here.

## Visual review
Both views use actual renders. Southeast view shows all four buildings, UC roof structures, Ekimae full-face sign mapping, West curved corner and complete latest ground floor, and Center244's selected January billboard. The plan view identifies all four footprints and gaps without moving the models. Facade quality at detailed storefront scale requires the separate individual asset close-ups. Unmodeled rear surfaces and blank side walls remain visible in this isolated presentation; the render does not imply that surrounding context has been reconstructed.

## Publication boundary
`PUBLICATION_MANIFEST.json` contains only the newly generated evidence directory files, each with byte count and SHA-256. It intentionally excludes all copied source assets, tests, runtime code, node_modules, public outputs and protected buildings. This task performed no GitHub writes, commits, pushes or merges.

## Image attribution and license
The composite renders and labeled review boards are distributed under CC BY-SA 4.0 (https://creativecommons.org/licenses/by-sa/4.0/). They include cropped and rectified photographic textures from Joli Rumi, 2025-11-01, https://commons.wikimedia.org/wiki/File:Shibuya_crossing,_Tokyo,_Japan.jpg (CC BY-SA 4.0), and Syced, 2025-01-31, https://commons.wikimedia.org/wiki/File:Shibuya_crossing,_seen_from_Shibuya_Stream.jpg (CC0 1.0, https://creativecommons.org/publicdomain/zero/1.0/). Changes include texture cropping/perspective correction, mapping to reconstructed geometry, lighting/rendering and explanatory labels. Attribution does not imply endorsement. Advertisements, trademarks and artwork may have separate rights not granted by the photographers' licenses. Individual asset source registers provide the detailed crops, dates and inference records.
