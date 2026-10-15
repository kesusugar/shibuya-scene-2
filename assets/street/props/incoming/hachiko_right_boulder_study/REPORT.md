# Production log and validation scope

2026-10-15: Independently inspected full-resolution photo crop and verified Commons attribution/date/licence. Isolated work: hachiko_reference_rock_revision. No Codex environment or API used.

Built one 32×18 two-sided grid shell with photo-informed asymmetric outline and front cleft, merged closed perimeter, removed coplanar corner remnants, recalculated normals. Synthetic seeded multiscale mineral texture softened after first visual review. Added explicit estimate/date caveats. Original algorithm comparison is representative, not exact current main.

Blender 4.2.3 LTS export: 2300 triangles, 1152 mesh vertices, 1 mesh/material, one embedded 512² texture. Saved editable .blend contains only asset mesh, packed texture and no render cameras/lights. Texture filepath relative; regeneration uses only Blender's bundled Python, numpy and standard library. Comparison assembly additionally uses Pillow.

Checks: finite coordinates; identity mesh transforms; closed manifold with 0 nonmanifold edges; 0 zero-area faces; positive volume 0.0895996 m³; one packed image. Dimensions .850 × .413792 × .578313 m, all estimated. Bottom AABB center origin. The seam removal fixes degenerate boundary behavior without adding separate disconnected shells.

Three views rendered with same lighting. Comparison uses own baseline algorithm and photograph crop, whose perspective is not metrically calibrated. Shape and recess are meaningful improvements over the generic rounded source algorithm, but color/mineral distribution remain approximations. Current 2026 persistence, placement, whole-scene performance and Three.js browser behavior are NOT established.

Independent regeneration/export QA pending at package freeze. No PR or runtime integration success claimed by this report.
