# Hachiko right boulder: unplaced photo-informed study

One natural rock beside the stone inscription panel, informed by July 2025 reference. This is a replacement candidate, not a new garden layout. No runtime assets, trees, wall, placement, collision or FPS code are changed. Do not place duplicate rocks over existing geometry.

## What improves
Original source uses randomly distorted subdivision-2 icospheres with a uniform brown material. This study adds the visible asymmetric rising-right silhouette, broad diagonal cleft, rounded shoulders and synthetic gray-brown mineral mottling. The reference image is never used as a texture. Back, depth and underside are invented because not visible.

The comparison's baseline is a representative reconstruction of the existing source algorithm, not an exact extracted main object. Its RNG stream differs because the full existing scene consumes random values earlier. No exact current-main visual comparison is claimed.

## Scale and orientation
Meters, bottom bounding-box center origin; front is Blender -Y (glTF +Z). Width 0.85 m, height approximately 0.58 m and depth approximately 0.42 m are provisional estimates, not measurements. Absolute scale is anchored to the previous source's 0.60–0.84 m rock width and 0.56–0.76 m height range. The photograph constrains projected width-to-height and cleft direction, not hidden extent. The existing wall's 0.52 m height is itself estimated and the rock is behind it at another depth, so it cannot support an accurate metric measurement. Do not infer exact dimensions from the comparison panel.

## Integration handoff
Codex should establish whether this individual rock still exists in the intended 2026 scene, identify the corresponding old rock component, and replace only that component. Do not remove the joined street_surround_rock mesh wholesale, or other rocks, groundcover, plaque, rails or stone wall. Placement and orientation remain to be calibrated against current full-scene photographs. July reference alone does not establish October 2026 condition.

## Files
hachiko_right_boulder.glb: one mesh/material with embedded self-authored PNG.
hachiko_right_boulder.blend: editable geometry with packed texture.
source/generate.py: Blender 4.2.3 generator, export and three renders; invoke Blender -b --python source/generate.py -- /absolute/output/directory.
source/check.py: mesh integrity checks on saved blend.
source/baseline_preview.py: representative old algorithm render.
evidence/: front/side/oblique, source-algorithm baseline and attributed photo comparison.

A browser/Three.js runtime and full-scene performance validation are not claimed. Blender regeneration/import and file structure checks are separate from deployment.
