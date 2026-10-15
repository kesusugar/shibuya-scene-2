# Validation report

PASS: Blender 4.2.3 canonical regeneration and editable-blend export produce byte-identical GLB. Strict GLB validation verifies 936 nondegenerate triangles, finite positions/normals, two OPAQUE double-sided materials, no images/external resources/animations/skins, and metre-scale bottom-centre bounds.

Visual inspection: original July photo, front/oblique render, and context render inspected. Photo evidence supports the leaf type and low patch only; species, count and dimensions remain estimated. Material palette was reduced from the first overly pale trial. No calibrated sunlight/colour match is claimed.

Scale-context stone and rock are neutral witnesses only, neither existing main assets nor proposed placement. GLB/blend contain only the tuft. No runtime files changed; no integrated-game or FPS test performed.

Candidate package is ready for independent review, not yet submitted to GitHub.

## Reference-crop correction before publication
The first comparison mistakenly applied preview coordinates directly to the larger source and showed a wall area, not foliage. Independent review caught this blocker. Actual source dimensions are 3072 × 4096. Crop bounds were correctly scaled to (2032,1800,2324,1971), and the resulting leaf/rock-base crop was opened and visually confirmed before rebuilding the comparison. Geometry, materials, GLB, blend and tests are unchanged.
