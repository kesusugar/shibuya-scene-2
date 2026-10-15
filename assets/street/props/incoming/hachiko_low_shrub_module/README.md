# Hachiko low shrub: unplaced replacement study

Single low planting cluster, not a tree replacement or a new garden layout. No runtime file, existing high tree, protected building, placement, collision or FPS code is changed. Intended for Codex to evaluate against the existing low shrub only.

- Blender 4.2.3; metres; mesh bounding-box bottom centre at (0,0,0).
- Estimated dimensions: 1.1065 × 0.8163 × 1.1854 m. No surveyed scale available.
- 3,824 triangles, one mesh/two primitives/two materials. The foliage uses a self-authored 256×256 RGBA procedural needle spray, embedded in GLB and packed in blend, glTF MASK alpha at 0.5, double-sided. Bark is opaque.
- Preselected budget: at most 6,000 triangles and 2 materials. No runtime performance claim: crossed masked cards still cost fill rate/overdraw and require integration checks, especially at distance and under temporal AA. Do not blindly duplicate six times.
- Visual change: remove opaque spherical cores and thick radial spikes; introduce tapered branches, layered foliage pads and fine needle sprays. Botanical species is not asserted.
- All trunk/root/backside structure, branch count, crown dimensions and exact trimming style are inferred. Photo shows only part of a plant behind the statue. This is a plausible photo-informed module, not an exact scan of that individual plant.

## Regeneration
Run Blender 4.2.3 in background with --python source/build_low_shrub.py -- /absolute/output/path . Output has GLB, editable blend, original texture PNG and stats JSON. No external assets or packages required.
Run source/render_views.py for three model views. The renderer uses this package's output/low_shrub.blend. Cycles transparency depth is 64 to avoid artificial black card silhouettes in the studio images. Runtime renderer acceptance is separate.

## Comparison baseline and placement
source/baseline_build_surround.py is the saved current surround generator, not claimed to be an exact download of main's GLB. source/build_baseline_cluster.py extracts its left-middle shrub algorithm (seed 794) and recentres it for same-camera studio comparison. This is a source-derived baseline, not evidence of runtime placement.
The old local stem anchor is x=-1.925, y=-1.45, z=segment minimum sampled pavement +0.49 in the original surround's statue-local frame (left segment middle i=1). Original ground and statue transform must be consulted before any future placement. New mesh original stem offset is recorded in output/stats.json; preserving stem alignment requires accounting for that offset. Do not automatically swap this scene file into the world.

## Status
Source-only review module. No new runtime registration or deployment. Independent review and in-engine texture/overdraw checks are required before integration.
