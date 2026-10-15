# PARCO terrace production candidate

**Completed scoped delivery prepared for review. Not merged, deployed, surveyed, or navigation/collision-ready.**

This isolated candidate carries the independently reviewed deep-terrace geometry onto the latest roof22-corrected PARCO baseline. It preserves the fixed geographic placement and source footprint, keeps the large corner lift core, and uses actual floor, soffit, supports, side returns, recessed storefront and a changing north walkway level. It is not a painted glass stripe or a uniform 8 m extrusion.

## Files and lineage

- `parco_terrace_candidate.glb`: candidate SHA-256 `7338ad9fcebf455a82383f938c36d58d817b9a8b0e9b75ff1e3b88ad9e0d9179`, 719,392 bytes.
- `parco_terrace_candidate.blend`: Blender 4.2.3 authoring scene. It reopens and matches the GLB mesh bounds and surface areas. No reference images are embedded.
- `inputs/roof22-corrected-base.glb`: immutable base SHA-256 `7dbb2e71338da1d3a5a6db6ec52ec38235f07ba5adbbd7b0585f6bcb15d372cd`.
- Geometry reference: frozen prototype `8a15ad9cf88239e6ccb58cb60c3a548ef86cae8b2cd8e0f6dfe695a0f48692ac`. That prototype and all accepted workspaces remain untouched. It is a geometry reference, **not** the base of this candidate.
- `scripts/`: local-input Python build, verification and render tools.
- `renders/`: licensed CC0 photo/final-model comparison. Other matched material/clay boards can be regenerated with --render; they compare the roof22 predecessor, NOT actual main. The asset-level review/main-before-after.jpg shows actual main versus final.
- `verification/`: scoped checks and evidence. The asset manifest enumerates published files; geometry ownership is tested directly.
- `docs/SOURCES.md`, `docs/MATERIALS.json`: source attribution and explicitly inferred material treatment.

## Bounded changes

Source 171, upper 108 and the eastern 18.73 m of 152 only. Seven original wall triangles and eight obsolete spandrel triangles are clipped; exact outside-aperture fragments are retained with ordinary float32 export quantization. The original attributes, nodes and materials are untouched. Superseded shallow terrace overlays are removed using their existing component ownership. Pale cladding and reveal backing remain.

Two explicit scope exceptions inherited from the reviewed prototype are recorded in `geometry/scope-exceptions.json`:

1. Only old inferred shallow overlays are removed below the western part of the 5F route, source 152 local u = 11.0–18.73 m, z = 26.2–30.178 m. The original opaque wall is retained. The outdoor route shifts to 5F; the opaque finish itself is **not independently confirmed**. No replacement windows are invented.
2. Only the newly created north inner termination/back walls extend down from 5F to 4F, closing demonstrated 74–82 m hollow-shell oblique sightlines. This makes no further original-wall cut.

The redundant `core_base` prism is the only production geometry omission relative to the approved additions. Exact rational intersections prove its whole approximately 171.53 m² plan and full thickness are contained by the retained `core_wrap_4F_floor`. Production retains all 24 serialized floor triangles and removes precisely 20 redundant triangles. Other intersecting assembly joins are not flattened.

Roof22, the prior source108/152 tessellation repairs outside the cut region, source84/141's real 1.82 m notch, roof47, source179 footprint, office tower and off-target facade grids remain preserved. No QFRONT, Seibu or other building files are modified.

## Geometry, coordinates and uncertainty

All source coordinates stay fixed. Blender model z = T.P. − 15 m; glTF stores the usual Y-up conversion `(x, z, -y)`. There is no recentering, scaling, rotation or footprint warp of the original building.

The official 4F schematic is registered by one isotropic similarity: 0.0574326659 m/pixel, y-flip, 17.49095254° rotation, translation (−213.80552624, 301.53978158) m. Fixed footprint corner residual RMS is 0.538 m, maximum 0.685 m. Six structural lift controls give RMS 0.333 m, maximum 0.460 m; independent escalator holdouts are 0.918 and 1.468 m. Approximate uncertainty is 1 m around the core/corners and 1.5 m locally. These are registration/model uncertainty statements, not surveyed tolerances. See `registration/`.

4F, 5F, 6F and 7F model levels are 25.378, 30.178, 34.978 and 39.778 m. The 4.8 m relative increments and 4F being 15.1 m above 1F are supported by the section. Absolute 1F T.P. remains unknown: T.P. 25.278 ± 0.5 m is an explicit **model sensitivity assumption**, not a proven real-world bound. Minimum ground T.P. 23.4 m is not automatically 1F.

Main east-depth samples are 8.59–10.69 m, a southern return is 11.51 m, and a broader throat sample is 15.27 m. Long diagonal cross-throat rays reach 20.25–21.46 m; those are **not terrace-width claims**. Corner-core depths are 3.42–5.08 m and north depths 2.27–6.45 m. The structural-section 8–9 m estimate applies only along its section direction, whose exact transverse cut remains uncertain.

Inferred clear heights: east 4F to soffit 9.322 m; corner 4F to soffit 13.922 m; north 5F to soffit 9.122 m. Slab/soffit thicknesses, support sizes, frame spacing and stair geometry are inferred, not structural or code-compliance data. Details are in `verification/measurements.json`.

## Materials and appearance

Existing materials and image/texture definitions are preserved. Only new terrace materials are added: pale structure, warm-grey paving, light metal, light blue-green reflection proxy, and partially transparent floor-edge rail panels. The core/storefront shader is deliberately an **opaque exterior reflection proxy**, not measured glass transmission. Simple internal shafts and floors are inferred; current shop fitouts are not modeled. No external image texture or copyrighted drawing is packaged.

All geometry proof views use the same opaque grey material on **every** mesh. Thus the visible recess, supports and parallax do not depend on dark glass, alpha tricks, hidden facade planes or a different material color. Material views show the separate appearance proposal, not calibrated photometry.

## Reproduce locally

Requirements: official Blender **4.2.3**, Python 3 with NumPy and Pillow. The file-relative tools do not need any accepted workspace or copyrighted reference bitmap. Use a fresh copy of the portable `source/terrace-v1` folder. For the standalone review root, copy `inputs/`, `scripts/`, `registration/` and `verification/floor_coverage/coverage-proof.json` into a fresh directory instead. Do not copy the outer `CANDIDATE_FREEZE.json`; the build refuses to overwrite a frozen review root:

```sh
python scripts/rebuild.py --blender /absolute/path/to/blender-4.2.3/blender
```

This performs the scoped cut, rebuild, merge, preservation and exact terrace-delta checks, final-floor coverage check, dense/oblique probes and saved-scene reimport check. `--render` also makes the matched views and boards. Blender version is enforced. GLB reproduction is byte-for-byte checked in `verification/reproducibility.json`; `.blend` metadata/path bytes need not reproduce identically, but saved-scene geometry is checked.

Current application material and geometry tests are in tests/parco-terrace.test.ts. They use the unchanged current application material code. These are not browser rendering, full-scene integration, FPS profiling or deployment acceptance.

## Checks and remaining limits

Passed scoped evidence includes 3,200 aperture rays, 475 floor and 475 ceiling probes, 80 return probes, and 1,920 north oblique rays without inappropriate far-shell hits. Original attributes/materials/nodes and all roof indices remain exact. Retained clipped wall vertices move at most 0.0155 mm from float64 clipping coordinates under float32 serialization; retained spandrel vertices at most 0.0069 mm. This is a numeric quantization bound, not a whole-assembly seam or as-built accuracy claim. A separate 0.1 mm welded-edge test must not be misread as a seam-width guarantee.

- Assemblies retain ordinary internal intersections/shared joins. They are not a fused collision or structural shell.
- The eastern 3F-to-4F escalator lower opening remains unmodeled because it would require cutting protected roof47. Only its 4F upper landing is represented.
- Below-5F original opaque finish remains unconfirmed.
- Absolute floor datum, local plan schematic alignment, glass transmission and detailed interiors are unresolved.
- Complete browser scene, transparent-sorting behavior in the actual scene, performance, collision and final production acceptance still require separate review.

This source package does not establish full-scene acceptance; publication and runtime review are separate steps.
