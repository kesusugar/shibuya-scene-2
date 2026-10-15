# SHIBU HACHI BOX doorway information lettering

Unplaced architectural add-on. This contains ONLY the readable `Tourist Information & Souvenir Store` lettering and a simple circular information symbol. It does not contain the carrier board, architecture, advertising, or a runtime registration. Codex owns placement.

- Blender 4.2.3, metres, bottom footprint centre origin, front is Blender -Y.
- 3.650 × 0.004 × 0.180 m, 832 triangles, 3 opaque materials. All dimensions and colours are estimated, not surveyed.
- Proposed parent-local Blender offset: [0, -0.686, 2.315] m for the existing SHIBU HACHI BOX model. Existing carrier front is y=-0.676. The add-on's nearest surface is y=-0.684: 8 mm clear of the carrier. No duplicate carrier or coplanar overlay.
- Export uses glTF Y-up: Blender offset maps to [0, 2.315, 0.686]. Apply only within the matching parent asset coordinates; do not treat this as world placement.
- Bfont lettering is an approximate substitute, not an exact font match. Letter spacing/height, icon geometry and red pigment are approximate. The smaller dark trailing text is confirmed by the clearer frontal photograph; no other labels are invented.

## Reproduce

`blender -b --python source/generate.py -- --output output`

For optional assembly comparison, add `--context /path/to/shibu_hachi_box.blend`. The referenced parent model must be the architectural module from PR #64. Context geometry is imported only AFTER standalone export/save and is never included in this GLB/blend. Front and oblique renders are model-only. Context before/after use identical camera and light settings. No repository runtime files are changed.

The editable blend retains separate text/symbol meshes. The generated GLB batches them into one mesh, three material primitives. No textures or external file dependencies are required.

Letters are flat painted-sign meshes rather than unnecessarily extruded lettering; the symbol disk is 2 mm thick. The white i sits forward of the disk without coplanar overlap.
