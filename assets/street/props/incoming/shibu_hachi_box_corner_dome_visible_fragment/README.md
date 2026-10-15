# SHIBU HACHI BOX roof-corner device: observed visible fragment

This is a new, unplaced accessory, not a replacement for the smaller soffit fixture in PR #66. The reference contains both objects simultaneously. This model represents only the visible white cylindrical housing, dark separator ring, white lower collar and dark hanging dome. It is not a complete device, a manufacturer identification, or a functioning camera.

## Evidence and uncertainty

- Source: SHIBUYA X WATCH, “渋谷、ハレとケ / Vol.16 Aug,2026 「ハチ、ハチ、ハチ 令和8年8月8日の渋谷」”, published 2026-08-11: https://biz.shibuyabunka.com/watch/107/
- Photograph represented as August 8, 2026 by that article; examined locally in the daytime pavilion image. Device occupies approximately x=164–196, y=0–43 in the 1080×608 reference.
- The top of the housing/attachment is clipped by the photograph. The model's flat upper face is a technical cutoff/interface, not an observed top or an actual mounting plate. Hidden bracket, cable routing, fasteners, rear markings and internal optics are intentionally omitted.
- Broad silhouette and white/dark layering: medium confidence. Small raised markings are too blurred to reconstruct and are omitted. Exact proportions, lower-dome finish and all dimensions: estimates.
- Diameter 0.160 m and visible height 0.230 m are low-confidence estimates based on device/fascia visual ratio and the existing pavilion's estimated 0.160 m fascia depth. This is **not independent measurement**; perspective and photograph clipping prevent precise calibration. The visible image ratio is roughly 30 px wide × 42 px high.
- This is 2026 evidence only. It does not establish installation in 2025 or the completed state of the entire Hachiko square.
- No reference photographs, crops or photo-derived textures are redistributed. The three PNGs are own procedural-model renders, not photos or proof of the assembled city.

## Integration contract

- Blender Z-up, metres, scale 1.0, bottom-centre origin. GLB uses standard glTF Y-up export.
- Bounds: x/y ±0.080 m; Blender z=0.000–0.230 m.
- Upper cutoff/interface z=0.230 m is provisional and **must not be treated as a verified mounting datum**.
- No runtime registration, placement, collision, scripts in src/, camera logic or other building edits. Placement remains the user's separate integration work.
- Roof-corner context is only a source location description. No unverified world transform is supplied.
- 896 triangles, four meshes, two opaque core-PBR materials. Dome appearance is glossy opaque dark material, not transparent optical simulation. No textures, emissions, external resources or required glTF extensions.

## Reproduction

Use Blender 4.2.3 LTS:

    blender -b -t 2 -P source/generate.py -- --output output --render
    blender -b -t 2 -P source/validate.py -- output

The editable .blend is saved before cameras/lights are created, so it contains just the model. Render views are generated from the same geometry. The source photo is not needed for regeneration.

## Tests and limits

Validation checks finite geometry, metres/bounds/origin, positive-volume closed manifold pieces, two materials, absence of external images/cameras/lights, GLB 2.0 self-containment/core triangle primitives, exact editable re-export and triangle totals. A separate-directory regeneration is byte-identical for the GLB. These are asset checks, not full-scene or browser/FPS acceptance. Three.js runtime testing was not run; only standard glTF format compatibility was checked.
