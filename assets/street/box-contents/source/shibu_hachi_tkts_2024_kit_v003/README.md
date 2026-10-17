# SHIBU HACHI BOX: TKTS visible left return v003

Focused successor of the existing 2024 optional TKTS kit, not a new physical desk. Adds the photographed left-hand red worktop return and inward-facing upper fascia. H-IN-018 remains partial because the lower cabinet, cropped front display and final placement are not reconstructed.

## What changed

Exactly two editable red parts were added to the counter upper shell:

- `Left_return_top_visible_estimated_plan`: estimated 0.280 × 0.760 × 0.045 m slab, with its top at local Z = 0.350 m.
- `Left_inner_red_fascia_evidence_cutoff`: estimated 0.052 × 0.760 × 0.305 m upper apron at the inward-facing edge, stopped at the existing lower evidence cutoff.

The reference supports the visible red top/edge and inward fascia. Absolute scale, thickness, rectangular hidden plan, rear endpoint and 1.5 mm bevel are inferred. A co-level top is a bounded modelling choice because no step is visible, not a measured relationship. The device kit's illustrative laptop offset is not used. No new desktop bridges the central opening.

## Preserved

- All 10 v002 meshes, evaluated geometry, materials and transforms remain exactly unchanged, including the revised wordmark.
- `red_sign_display.glb` and `portrait_monitor.glb` are byte-identical to v002.
- Counter bounds remain 1.400 × 0.960 × 0.350 m. The bottom-centre origin is unchanged; compensation is (0, 0, 0).
- The original illustrative kit arrangement is unchanged. There is no world/site placement transform.
- v002 is unmodified. No devices, lower cabinet, full interior, runtime, QFRONT, Seibu, walking/FPS, merge or deployment changes.

## Deliverables

- `models/counter_upper_shell.glb`: revised six-part shell, one red material batch, 648 triangles.
- `models/red_sign_display.glb`, `models/portrait_monitor.glb`: unchanged modules.
- `shibu_hachi_tkts_2024_kit_v003.blend`: separated editable parts, no cameras/lights/reference images.
- `source/generate.py`: deterministic Blender 4.2.3 construction; frozen v002 modules are bundled in `source/unchanged_modules/`.
- `source/export_editable.py`: re-export an edited blend without regeneration.
- `source/validate.py`, `validation_common.py`, `v002_baseline.json`: predecessor source signatures and focused integrity checks.
- `source/render_comparison.py`, `make_comparison_sheets.py`: matched actual final-GLB renders and labelled model-only comparison sheets.
- `evidence/comparison_oblique.png`: same-camera whole-kit before/after.
- `evidence/comparison_inside.png`: same-camera counter-only inside inspection, with no devices obscuring the new fascia.
- `PHOTO_REFERENCE_ANALYSIS.md`, `PROVENANCE.md`, `source_reference.json`, `component_estimates.json`: observations, inferred dimensions and source-only provenance.

## Reproduce

Use Blender 4.2.3 LTS. No downloaded image, font or external Blender add-on is needed. Retain the bundled `source/unchanged_modules/` and `source/v002_baseline.json` beside the generator/validator.

```sh
blender -b -t 2 --python source/generate.py -- --output /path/to/new-output --no-render
blender -b -t 2 --python source/validate.py -- /path/to/new-output
blender -b -t 2 --python source/render_comparison.py -- /path/to/new-output /path/to/shibu_hachi_tkts_2024_kit_v002
python source/make_comparison_sheets.py /path/to/new-output
```

Generation and validation work without the predecessor package. The optional second validation argument enables the original v002 file-preservation audit if `evidence/v002_preservation.json` is present. Matched comparison rendering and re-capturing the historical baseline require v002. Ordinary generation optionally produces standalone inspection views if `--no-render` is omitted.

## Coordinate and topology contract

Metres; Blender Z-up, front -Y; standard glTF Y-up conversion. Export nodes have identity transforms. Local counter bounds are X [-0.70, 0.70], Y [-0.48, 0.48], Z [0, 0.35] m. The bottom plane is a deliberate upper-shell evidence cutoff, not floor contact. The blend's installation estimates are illustrative only.

Every editable component is closed. The counter is a visual assembly of closed parts, not a Boolean-unioned fabrication solid. The new top meets the old front top at Y = -0.28 m and the new fascia meets its underside at Z = 0.305 m. These are intentional component contacts, not exposed overlapping skins. After global seam welding, the combined counter has three nonmanifold contact edges (v002 had one), zero open boundary edges and zero degenerate triangles. New components individually have zero nonmanifold edges. Existing contact geometry is retained.

## Scope and evidence limits

Source article publication: 2024-09-19. Photo capture date is unknown; 2026 continuity is unverified. No real dimension is surveyed. No complete cabinet, storage, supports, extra cables, paper/advertising textures, screens UI, laptop, tablet or raised laptop shelf was added. The authored v002 wordmark is not official licensed vector artwork. Source photos/crops remain local-only and are absent from this package. No runtime/collision/FPS testing was applicable because runtime was not changed.
