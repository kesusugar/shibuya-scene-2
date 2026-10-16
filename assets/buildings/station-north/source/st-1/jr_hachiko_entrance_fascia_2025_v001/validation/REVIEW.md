# Validation and visual review

Actual J01/J02 reference pixels were viewed locally; hashes matched the handoff. No photo bytes are delivered. All three final model-only PNGs were inspected for legibility, frame/face scope and unintended neighbouring text.

The final source was frozen after a visual correction reducing technical graphic separation to at most 1 mm above the pale face. These offsets exist solely to avoid coplanar rendering; the lettering remains zero-thickness geometry and must not be interpreted as raised metal. One earlier freeze/clean rebuild was superseded after final visual review exposed excessive shadowing. Exactly one clean regeneration of the final frozen source was performed, and its GLB was byte-identical to the final delivery. The package does not claim the entire development process used only one build.

Early working validation found zero-area triangles produced by converting the substitute font. The generator now removes only zero-area converted text triangles while retaining editable text sources. A coplanar overlap between the approximate J/R shapes was eliminated by using one unified independently authored outline. No other asset was changed.

Final checks: Blender 4.2.3; opening saved blend; five editable text sources; renamed OFL font packed; no external image assets; GLB with embedded buffer, four materials and no textures/images; root identity; bottom-centre envelope; expected estimated dimensions; zero degenerate triangles; deterministic clean regeneration; GLB reimport. Planar sign graphics intentionally have open boundary edges. Technical backing/rims are simple closed components, not a watertight boolean union of the entire object.

The validator initially included Blender's un-packable built-in font in its external-font check. The assertion was corrected to inspect only external fonts; the actual custom font was packed from the outset. This was a validator correction, not a missing-font repair.

No claims are made about a live running scene, all-runtime absence, legal rights to official trademarks, measured dimensions, exact logo/typeface, geographic placement or 2026 continuity.
