# SHIBU HACHI BOX display spotlight, August 2026 reference

Standalone estimated accessory; no runtime placement, real lights, shadows, or FPS changes. This is not the exterior soffit dome already produced. One reusable black display spotlight represents the two small heads visible inside the glazed display in the August 8, 2026 source.

## Reproduce
Blender **4.2.3**: `blender -b -t 4 --python source/generate.py -- /absolute/output/directory`

Outputs: GLB, editable blend, asset.json, and model-only front/side/oblique PNGs. Blender Z up, front toward negative Y; GLB exported Y up. The full fixture's bounding-box bottom centre is zero; mount datum is separately recorded in asset.json. The saved blend contains only the model, not render lamps/cameras or context building. Render lamps exist only transiently for verification images and are not exported.

## Scope and estimates
Estimated cylindrical housing diameter 0.110 m, axial depth 0.160 m, downward angle 60 degrees below horizontal. These are visual proportion estimates, not measured/product specification dimensions. The dark housing, short support and warm front aperture are observed; exact swivel geometry, rear cap, mount foot and fastening method are inferred minimal functional shapes. No manufacturer identification, hidden wiring, embossed markings, detailed electronics, advertising or branding are invented. The lens uses low emission solely to represent the warm aperture; no runtime light is exported and it does not light the game scene.

## Codex integration
Date gate this accessory separately from the older pavilion. Do not presume presence in 2025. Two observed image locations are recorded in SOURCES.md but cannot determine metric/world placement reliably. Reuse two instances only after aligning the current pavilion with the source. The mount datum is the top of the small foot; local position/orientation and collision remain Codex's responsibility. Do not duplicate the whole pavilion, replace existing geometry, or add real-time lighting automatically.

## Deliverable rights
Model, script and model-only renders are original project work; no third-party photograph, crop, advertisement artwork or image texture is included. Existing repository licensing applies; no source photograph licence is claimed.
