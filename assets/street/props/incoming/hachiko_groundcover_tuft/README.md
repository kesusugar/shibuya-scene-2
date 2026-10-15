# Hachiko narrow-leaf groundcover: unplaced photo-informed module

One modest 36-blade tuft, distinct from the completed pine-like shrub. Intended as a candidate for the small patch between the statue pedestal and right boulder. No automatic placement, soil, rock replacement, high tree, protected building or runtime/FPS change.

- Blender 4.2.3 LTS, metres, identity transforms, AABB bottom-centre origin.
- Dimensions approximately 0.331 × 0.306 × 0.167 m. All dimensions are estimates, NOT surveyed. The photo patch is only partly visible and cannot establish the full planting footprint or individual clump size.
- 936 triangles, one mesh, two opaque double-sided leaf materials; no textures, alpha cards, lights, animation or external resources in GLB. Thin seven-segment curved blades have a slight central keel. These are surface blades, not thick watertight solids; double-sided rendering is required.
- Muted dark green/olive palette approximates photographed foliage. Studio lighting is not matched to the original photo's sunlight, exposure or white balance, so comparison is for shape and layering, not measured colour reproduction.
- Species is unidentified. Crown grouping, leaf count/width, hidden roots and backside are inferred. July 2025 visibility does NOT certify that this exact patch survives in October 2026. Integration should wait for placement/current-state confirmation.

## Reproduce
Blender 4.2.3: `blender -b --python source/generate.py -- /absolute/output/directory`.
Without arguments the output is `output/` adjacent to `source/`. `source/render.py` regenerates four isolated views and a scale-context view from the editable blend. `python source/validate.py` validates the delivered GLB. No external add-ons or dependencies for generation; comparison sheet assembly uses Pillow separately.

`evidence/context_labelled.jpg` contains a generic stone block and low-poly rock ONLY as size witnesses. They are neither existing main meshes nor a proposed placement. The asset GLB/blend excludes these witnesses.

## Integration boundary
Do not scatter a lawn or replace the existing pine shrub. A local integrator must locate a supported low patch, preserve existing stone/rocks, and evaluate screen-size benefit before placing one or more tufts. No runtime integration/performance acceptance is claimed.

## Licences
Self-authored geometry, source and renders: CC BY-SA 4.0, following this project's asset convention. Source photo/crop: RuinDig/Yuki Uchida, CC BY 4.0; see SOURCES.md. No unlicensed 2026 image is distributed. Source photograph is not a material texture.
