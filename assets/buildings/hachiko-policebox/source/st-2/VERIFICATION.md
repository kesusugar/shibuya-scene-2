# Bounded verification

## Visual review

Reviewed the original P1 and P2 photo pixels before modeling and inspected all five generated model-only PNGs. Camera views are illustrative orthographic studies, not calibrated matches to either photograph.

| Feature | Result | Evidence / limit |
|---|---|---|
| Silver outer-frame silhouette | PARTIAL | Broad top, projecting underside, short left upper return and longer right return reproduced. Width/depth and left overhang remain adjustable estimates because P1 perspective and P2 cropping do not establish plan dimensions. |
| Open upper recess | PASS for scoped structure | No upper-storey volume, side/rear room shell or deck has been inserted. A separate shallow rear aperture remains behind the open frontage. Exact window subdivisions are simplified. |
| Bowed pale-green frontage | PASS for scoped structure | Both oblique views and top silhouette show a shared 24-segment outward elliptical bow. Radius/bulge is not measured. |
| Green/silver band continuity | PASS | Shared curve coordinates and exact common z interface. Independent materials and heights. No overlap between top/bottom interface caps; one small rear thickness transition closes the difference. |
| Visible support locations | PARTIAL | Source-observed upper-left, lower-left and lower-right locations included; both lower red strips retained. Lower-left upper segment is explicitly visible in P1 x240–266, y492–545. No mirrored completion. Crowd-hidden lower continuations and exact placement are explicitly estimated. |
| Lower façade | PARTIAL, intentionally | Shallow neutral removable backing/frame and threshold only; no exact door mechanism, notices, interior or unseen perimeter invented. |
| Rights-safe output | PASS | Five model-only PNGs; no source photographs/crops/overlays or photo-derived textures in package or GLB. |

The ground-level front render uses a studio ground plane; it is not site pavement or a measured ground contact.

## Technical checks

Final results are recorded in `mesh_audit.json` and `glb_validation.json`:

- Pinned Blender 4.2.3 LTS used.
- GLB contains only source-visible and estimated-closure model objects. No review cameras, lights, ground, labels or curve guide exported.
- No external buffers, images, texture files, nonfinite positions or zero-area exported triangles.
- Evaluated mesh check finds no negative-volume closed objects; broad curved fronts are checked against analytic outward normals.
- Closed shell components are used where needed. The overall façade intentionally is not a watertight building.
- Band front vertices share the same curve and interface height. A narrow front rail is a real geometric overlay, not coplanar duplicate faces.

## Build and correction record

One initial build generated the editable Blend, GLB and five PNGs. Essential exported-triangle validation caught **16 degenerate triangles on the optional sign's thin inset bevel**. The generator was corrected to limit bevel width to 22% of each box's smallest dimension, avoiding a clamped, collapsed bevel. This changes only that tiny sign inset for this parameter set.

The single requested no-render regeneration then completed successfully with zero exported degenerate triangles. During parent review, the source-visible lower-left support/red strip in P1 (x240–266, y492–545) was correctly identified as an additional support. That observed upper segment was added at an independently estimated position; its crowd-hidden lower continuation is a separate estimated object. This was an evidence correction, not a cosmetic pass.

The source-backed correction rebuilt the final Blend/GLB and refreshed only the four images affected by lower-support visibility: front, both obliques and confidence. The existing top silhouette was retained because the lower support is entirely hidden by unchanged upper geometry in that view. The final representative and confidence images were visually inspected after this correction. No whole-scene test, new photo research or additional no-render regeneration was performed.

The final GLB read-only validation again reports zero degenerate triangles. The source generator has no random geometry or external texture dependency. A second identical-output run/hash comparison was not performed; only one no-render regeneration was requested. The final GLB hash is in the validation JSON and release manifest.
