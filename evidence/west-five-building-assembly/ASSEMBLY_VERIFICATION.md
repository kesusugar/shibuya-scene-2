# Five-building preserved-coordinate assembly review

## Result and scope
The latest West ground-floor storefront, Daiichi-Kangin/UC, final Ekimae, frozen Center244 and final BIG ECHO (legacy asset ID `quattro`) are assembled without XY repositioning or rescaling. This is an isolated asset review, not a complete scene. Only ten explicitly named GLBs are imported, with five viewer JSON files; every input is size/hash checked and Blender must be exactly 4.2.3. BIG ECHO is Shibuya Heiwa Building 21-8, not the adjacent mineo/Heiwa Quattro 21-9.

All January layers plus Ekimae's November layer are intentionally displayed together for review. This is **not a single-date recreation**. Center244 and BIG ECHO January signs remain unregistered at runtime; the render explicitly imports them only into its temporary Blender scene. No runtime or model edits, protected QFRONT/Seibu changes, GitHub writes, commits or merges were performed. The earlier four-building evidence was preserved unchanged.

## Spatial findings: AABB overlap is NOT collision
Nine of ten pairs have strictly disjoint world-space mesh AABBs. West–BIG ECHO has overlapping AABBs: X overlap 17.562336 m, Y overlap 3.332554 m, Z overlap 30.355999 m. The axis-aligned boxes are loose around the diagonal footprints.

For this pair, Blender BVH triangle-surface checking across all object pairs finds **zero surface contacts**, at epsilon 1e-6 m. More importantly, a separating-axis test on the 2D convex hulls of **every imported world-space vertex**, including all architecture, added detail and dated signs, establishes a **positive 8.998440 m separation along an oblique plan axis**. This is a conservative geometric proof that their projected envelopes do not intersect. Thus neither actual triangle contact nor one solid contained within the other is possible in this imported assembly. The result does not depend on meshes being closed/watertight, and avoids unreliable ray-parity tests on architectural shells.

Original/source comparison: West's immutable PLATEAU surface XY and BIG ECHO's exact baseline shell XY likewise have disjoint convex envelopes, with **11.563507 m separation along the strongest tested axis**. Final decoration narrows the conservative envelope gap, but does not create an intersection. The two separation values are axis-projection envelope margins, not measured walking clearances or exact closest-surface distances. Since no contact occurs, there is no intersecting source/addition component to blame, and no geometry fix is recommended.

`pairwise-aabb-check.json`, `geometry-separation.json` and `assembly-bounds.json` contain full diagnostics, actual hull points, separating axis and projected intervals. `separation-input-manifest.json` hashes the two baseline inputs. `check-separation.py` reproduces the proof using the same hash-checked import code.

## Tests and provenance
- Five focused building suites: **22/22 passed** (West, UC, Ekimae, Center244 and BIG ECHO).
- Updated neighbourhood suite filtered to `quattro|center244`: **2 passed, 4 skipped**. This is not an unfiltered suite pass.
- TypeScript `tsc --noEmit`: passed.
- Current West strict test is from `west_storefront_review`; Center244 from `center244_fidelity`; BIG ECHO and updated neighbourhood from `bigecho_fidelity`. Test hashes/sources are in `focused-test-provenance.json`.
- Every render input is hash-checked against both its copied bytes and final producer bytes. BIG ECHO architecture SHA-256: `2e3342cbba74eb71f7975b29ea1b8dbd7567e5085b1b50db733fe042a032f8ea`; January signs: `2c8cd0969a92572a5404284b7e60972eb08f8b4f959e7daa153c4442ed441413`.

## Reproduce
From the isolated project root:

```sh
/workspace/shared/blender423/blender-4.2.3-linux-x64/blender -b -t 4 --python-exit-code 1 -P evidence/west-five-building-assembly/render-assembly.py -- "$PWD"
/workspace/shared/blender423/blender-4.2.3-linux-x64/blender -b -t 4 --python-exit-code 1 -P evidence/west-five-building-assembly/check-separation.py -- "$PWD"
python evidence/west-five-building-assembly/make-board.py
./node_modules/.bin/vitest run tests/west-block.test.ts tests/daiichi-kangin.test.ts tests/ekimae.test.ts tests/center244-fidelity.test.ts tests/quattro-fidelity.test.ts
./node_modules/.bin/vitest run tests/neighbourhood.test.ts -t 'quattro|center244'
./node_modules/.bin/tsc --noEmit
```

Rendering uses Cycles, 32 samples, denoising, AgX, orthographic cameras and 1800×1400 output. Blender's glTF axis conversion is followed only by Z offset `groundElevationTP - 15 m`. The script has no arbitrary file glob. Disabled emission is a review-scene setting only. Board labels are added by Pillow to actual rendered images, never by image generation.

## Limits and visual interpretation
No terrain, road, plaza or other buildings are included; grey space is the world background, not physical ground. The latest West ground-floor geometry is fully included. Single-building facade/crop quality is best judged from each asset's close-up evidence. The southeast view makes BIG ECHO's steep roof and untextured cream side visible, not its full southwest frontage; complementary south and plan views retain the same geometry and coordinates.

This verifies limited imported-asset separation and targeted regressions, not fullscene startup, rendering, complete tests/build, road clearance, terrain anchoring, runtime collision behavior, owner-PC FPS, geodetic/photo accuracy or unseen details. QFRONT/Seibu are absent from the render; this report does not extend their separate source-footprint tests to all protected decorations.

## Publication and rights
`PUBLICATION_MANIFEST.json` contains only newly generated evidence files under this directory. Copied assets, tests, source/runtime code and dependencies are excluded. Parent may publish evidence in its own separate evidence/docs commit according to project practice; this worker makes no commits. Derived renders are CC BY-SA 4.0, with exact photographer/source links and modification notices in `ATTRIBUTION_AND_LICENSE.md` and explicit on-image license notices.
