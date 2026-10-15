# SHIBU HACHI BOX soffit dome fixture

Visible housing reconstruction, not a manufacturer identification or functioning surveillance device. This small pale circular base and dark lower dome is present beneath the front-left canopy in the 2024 CASIO photograph and the August 8, 2026 photograph. It was missing from the pavilion architectural model.

## Deliverables and reproduction
Use Blender **4.2.3**:

    blender -b -P source/generate.py -- --output output --render

Optional `--context-glb PATH_TO_PAVILION_GLB` creates two additional original-render attachment previews. The pavilion GLB is the separately authored PR #64 architecture; it is not copied into this package. Context imagery is NOT an integrated game screenshot, exact photo-camera match, or measured placement.

The editable blend contains only three named fixture meshes, two materials, and no camera/light. The GLB contains the same visible parts: tapered pale housing, shallow mounting flange and dark dome. No image textures, manufacturer marks, unobserved bolts, wiring or interior optics are invented. Shape is rotationally symmetric because image resolution cannot justify finer deviations.

## Dimensions and origin
Diameter **0.120 m**, total height **0.090 m**, lower dome diameter **0.090 m**: all estimated. In the 840×472 source the fixture spans roughly 10–12 pixels, compared with approximately 250–270 pixels of nearby floor-to-head frame. In the 1080×608 source it spans approximately 16–20 pixels, compared with roughly 390–420 pixels of frame. Using the pavilion plan's 2.354 m clear height only as a rough local scale gives order-of-magnitude diameters around 0.09–0.12 m; depth/perspective and low resolution preclude direct measurement. We use 0.12 m, not a claimed standard/model-specific dimension. Height and profile are visual estimates.

Metres; Blender Z-up, GLB Y-up. All mesh origins coincide with the **bottom centre (0,0,0)**. The top mounting plane is Blender Z=0.090 m, normal +Z. No negative local height.

## Attachment and integration
`placement.json` gives a provisional translation relative to the PR #64 pavilion, not a geographic/world coordinate. The fixture top meets the authored soffit underside at Z=2.660 m. X/Y are estimated from the front-left corner photographs. The fixture is a separate accessory, not a replacement of the pavilion or any existing security equipment. Do not duplicate if future integrated geometry already includes it.

No existing GLB, runtime loader, source placement, collision, walking, FPS, QFRONT or Seibu file is changed. Codex owns scene integration. A second larger device visible above the left roof corner in 2026 is a different object and is NOT included.

## Remaining differences
The small photograph cannot reveal exact flange section, dome transparency, internal optics, fixing screws, cable route or brand. Dark opaque glossy material approximates the visible shell only. Exact dimensions, local mounting coordinate, appearance at October 2025 and continuity between the two observed dates are not independently measured. Model views are neutral-lit, not matched source lighting. The context preview inherits estimated pavilion soffit/height and an intentionally empty interior/advertising layer.
