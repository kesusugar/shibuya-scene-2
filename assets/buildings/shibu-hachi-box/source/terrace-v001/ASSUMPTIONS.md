# Front terrace assumptions and integration limits

This document separates inherited model values, photo-derived estimates and deliberate assembly conventions. All values below use metre-based authoring XYZ unless specified otherwise.

## Scale and protected architecture

The architectural front components inherit the projected scale `0.86 / 73 = 0.0117808219178 m/source-pixel`. The source perspective has not been rectified and the scale is not surveyed. The original graphics retain their independently estimated `0.80 / 68 m/source-pixel` scale, differing by approximately 0.137%; they are not silently rescaled to match the rail.

The operator PDF's H800 × W7600 mm front advertising label supports an approximate glass/print scale. It does not identify outer-frame height or post-centre width. The candidate's 0.790 m clear aperture therefore must not be represented as a verified 0.800 m opening.

No original building dimensions are changed. The inherited shell dimensions remain overall plan width 12.559 m, column-centre span 12.259 m, wall-centre span 12.206 m, 3.853 m bays, 0.350 m divisions, depth 3.572 m, wall-centre depth 2.244 m and promotional clear-height specification 2.354 m. They are not used to force a fit to the estimated terrace.

## Raw local assembly

- Axes: +X right/descending, -Y public/front, +Z up. Knee post centre: X=0; rail centre plane: Y=0.
- Chosen high shell/support datum: F=0.248 m, inherited from the existing modeled finished floor. It establishes neither attachment to that floor nor site elevation.
- Level post-centre extent: X=-7.963835616 to 0 m. Rail outer vertical height: 0.860 m; nominal frame face: 0.035 m. These are inherited modeling estimates.
- Ramp post-centre run: 3.734520548 m. High fascia height: 0.412328767 m; R3 fascia height: 0.082465753 m; fall: 0.329863014 m. Ramp geometry remains unchanged.
- Shared fascia bottom: Z=-0.164328767 m. Level shell top: Z=0.248 m. Ramp top at R3: Z=-0.081863014 m. Negative values do not mean below a certified ground plane.
- Visible shell depth: Y=-0.020 to +0.880 m, an estimated 0.900 m. Aligning the fascia front and rail front at Y=-0.020 m is a local convention, not a measured building attachment.
- New level shell: X=-7.963835616 to 0 m, with thin top and front skins matching the ramp's visible shell treatment. The 20 mm gauges, backs, undersides and closure faces are technical mesh construction, not observed cladding, support, real end caps or a solid foundation.

## Shared knee and slope refit

The derived candidate uses one knee upright. Level and descending members terminate at the shared knee plane, with a common section and corresponding flat/sloping cuts. No mounting bracket, foot, concealed support or cap is inferred. Both original knee posts remain in the baseline.

Only the derived sloped rail receives `Z += (0.5 / 317) × X`, using raw terrace X with the knee at zero. This changes the 28.5 px source fall to 28 px while preserving constant vertical frame height, nominal sections, pitches and material. The maximum post-centre correction is 5.890410959 mm. It is a documented fit within source uncertainty, not a new measured grade.

The revised top residuals are `[0, 1.333, 1.667, 2]` source pixels and the lower residuals `[0, -0.667, -2.333, -3]` pixels. These residuals describe agreement with sampled image contours, not physical accuracy.

## Rail and deck seam

The default support clearance is zero: rail underside and shell top meet under a **local butt hypothesis**. The source lower rail at y414 and the opaque fascia upper contour at y418 remain distinct observations. The clean candidate joint resolves assembly bookkeeping only; it does not prove those two photo edges coincide.

Preserving the original independently sampled elevations instead would leave approximately 47.123 mm at the knee and 41.233 mm at R3 between rail underside and fascia top. No filler, fabricated legs or hidden overlap is added to disguise this ambiguity. A closer oblique/side photograph or section drawing is required to establish the actual support seam.

## Unchanged watch artwork and intentional overlap

The original watch-case mesh is approximately 0.811764717 m wide, 0.835294127 m high and 0.600 mm thick. Its placement relative to the unchanged level-rail root is `[0.005890411, -0.006300, 0.011780822]` m, with unit scale.

Its vertical bounds relative to the level rail are Z=0.011780822 to 0.847074949 m. It stays inside the outer frame's Z=0 to 0.860 m while extending 23.219 mm below and 22.075 mm above the clear aperture, Z=0.035 to 0.825 m. It remains horizontally inside the central bay.

The graphic occupies Y=-0.0066 to -0.0060 m. Its rear face touches the clear pane front at Y=-0.0060 m; its front face is 13.4 mm behind the opaque frame front at Y=-0.020 m. The full original silhouette is retained. The frame intentionally masks the extreme upper and lower ink regions.

Clipping the original 40 front-facing triangles to the clear aperture predicts 0.279836309 m² total front ink, 0.260885335 m² visible ink and 0.018950974 m² masked ink, approximately **6.772%**. This is projected ink area, not a percentage of the bounding rectangle or a guarantee about every camera view.

The actual GLB reimport check reports 6.7721628% masked front ink, agreeing with that prediction within export precision. Only the watch overlaps the level upper/lower bars; the other four graphics report no masked ink in the same projected test. This does not remove the physical-construction caveat below.

The clear pane ends at the aperture. Ink hidden inside the opaque frame has **no modeled backing glass**. The overlap is a disclosed rendering hypothesis, not collision-free physical decal construction. Do not shrink, trim or pull the graphic in front of the frame to conceal this condition. Validation must distinguish intentional print/frame intersections from accidental solid intersections.

## Candidate-only shield topology repair

The original SHOCK RESIST shield contains a lower white triangle coplanarly overlapping four border front triangles. The measured total overlap is 0.0009778013535164578 m². It produced an actual render artifact and is distinct from the watch's intentional frame occlusion.

`source/repair_shield.py` exact-unions the border and lower triangle in the candidate only, retaining the original union silhouette, scale, 0.600 mm depth and 11 text components. It does not redraw letters, crop the artwork, move it forward or alter the source GLB. Retriangulation changes the shield from 3,100 to 3,156 triangles without increasing the candidate mesh count. The other four graphics, including the watch, retain their original geometry apart from assembly transforms and export precision.

`evidence/shield_actual_export_check.json` finds zero positive coplanar front-triangle overlap in the actual delivered shield. This is an explicit topology repair, so the final candidate must not be described as five unchanged graphic meshes or a transform-only assembly of every graphic. Original source/baseline preservation remains a separate, verified property.

## Normalization and inverse

Expected raw candidate bounds are X `[-7.981335616, 3.752020548]`, Y `[-0.020, 0.880]`, Z `[-0.164328767, 1.108]` m. Export normalization adds:

`p_normalized = p_raw + [2.114657534, -0.430, 0.164328767]`

Thus the expected normalized bounds are X approximately ±5.866678082 m, Y ±0.450 m and Z 0 to 1.272328767 m. The raw knee/support point `[0, 0, 0.248]` becomes approximately `[2.114657534, -0.430, 0.412328767]`.

The inverse subtracts that vector. It restores the **shared local shell-floor datum only**. Export Z=0 is the candidate's visible lower-profile plane, not site ground. Neither direction supplies a world transform, a surveyed anchor, whole-building XY alignment or ground contact. Use measured export bounds for floating-point tolerances; the quoted values describe the intended geometry.

For the delivered asset, `placement_reference.json` records the actual float32 normalization as `[2.114657402038574, -0.4300000071525574, 0.16432876884937286]` m. Use that machine-readable transform for exact asset reversal. The difference from the design vector above is sub-micrometre numerical precision, not an additional alignment adjustment.

## Old platform and right terminal remain unresolved

The old level fascia bottom is Z=0, 164.329 mm above the new raw lower contour. The old slab top is 0.230 m, 18 mm below the chosen finished floor. The new level and ramp shells are continuous with one another, not proven continuous with the old platform.

The old central front slab occupies X `[-5.1295, 5.1295]`, Y `[-1.786, -0.660]`, Z `[0, 0.230]` m. Its right approach and threshold steps occupy X `[5.1295, 6.2795]`, with 0.115/0.230 m tops. Any future replacement must isolate those exact connected components and relevant joints/trim. Do not suppress the whole mineral-material batch: it also contains `Rear_closure_INFERRED`. The main slab behind the facade and rear closure remain protected.

The observed R3 plane is a modeling boundary, **not a confirmed right terminal**. The shell retains positive height there. No toe, return, apron, footing, ground extension, terrain collision or continuation beyond R3 is supplied. Whole-building integration requires a separately reviewed old-platform replacement map and plan/photo-based XY fit.
