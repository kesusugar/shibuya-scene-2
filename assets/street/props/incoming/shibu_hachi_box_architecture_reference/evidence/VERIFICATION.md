# Verification scope

Blender 4.2.3, build 0e22e4fcea03, background generation.

- Final architecture: 9,312 triangles, five meshes / five material primitives, no external images or buffers.
- GLB SHA256: 95f08e5d0aba2acd0043aff57ae2995fc15953792ef02f1ce20bde4dc1c3c923.
- Relocated source generation from the publication package produces byte-identical GLB.
- Mesh coordinates are finite; ground minimum is zero in glTF Y; architecture is under 13.1 m wide and 3.5 m total height, including the estimated identifier panel.
- Independent relocated generation and editable batch export are both byte-identical to the final GLB. Independent index, finite normal and degenerate-face checks passed: 9,312 triangles, zero zero-area triangles, all normals unit length.
- Front, side, oblique, rear and photo-near views use procedural original model geometry only. Studio ground/cameras/lights are not exported or stored in the editable architecture blend.
- All public asset images are model renders; none is a source photograph or a photograph-derived collage.

These are asset-level checks. No main-scene browser view, automatic placement, frame-rate test or runtime integration is claimed. The original scene is unchanged. Roof dimensions, sign carrier, rear closure, vertical sizes, steps and pane thicknesses remain visual estimates; plan measurements do not turn them into surveyed dimensions.
