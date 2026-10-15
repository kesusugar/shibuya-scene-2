# Production record

All times below are UTC on 15 October 2026. No rounded “10 minute” duration is substituted for the actual measurements.

- Actual start: 15:55:12. Supplied counter, CASIO exterior, August 2026 exterior and July 2025 statue photographs inspected; local inventory/readmes checked.
- Target selection reported at 15:56:28: the open counter laptop, explicitly separate from the completed wall monitor. Parent approved the bounded 2024 movable-equipment interpretation.
- First source/build completed at approximately 15:59:19; initial generation/export/save itself measured 0.978 s. Evidence selection and source authoring took about 4 min 7 s from start, including tool reads.
- Initial freeze at approximately 15:59:49; first GLB import/render pass completed by 16:01:20. Initial structural and visual review identified 69 zero-area bevel residues in very thin geometry and a cropped operator-view camera. The blend audit also incorrectly counted Blender's internal Render Result viewer as external data.
- Correction: collapse duplicate/degenerate submillimetre bevel geometry; widen only the operator camera framing; distinguish viewer data from external images. No new object, texture or brand detail was added.
- Final geometry/source freeze: 2026-10-15T16:02:34.031183+00:00. Final generation/export/save measured 1.039 s.
- Final structural checks: GLB and editable blend passed. No zero-area triangles remain. The regenerated asset affected the render stage, so final previews were regenerated from that asset. No unchanged already-passed production stage was otherwise repeatedly run.
- Final GLB import plus all three renders: 66.229 s total. Rear 23.146 s; side 11.955 s; operator oblique 30.995 s.
- Final visual inspection: 16:04:48. All three PNGs actually viewed; framing accepted. Pixel-alpha bounds also verify margins on every edge.
- Packaging/manifest preparation: 2026-10-15T16:05:45.950124+00:00. The user then prioritised a comprehensive inventory; work stops after this completed asset, with no next-object search.

## Final state

Blender 4.2.3 LTS; 8,904 triangles; 80 editable meshes; GLB 3 meshes / 3 primitives / 3 materials; metres; full-open-envelope bottom-centre origin; no texture or external URI. File packing invoked and no external content was required. Structural, authoring-file and GLB-round-trip checks passed. Final hashes match the freeze record.

No independent reviewer, Khronos command-line validator, full-scene/browser integration, FPS test, runtime placement, GitHub upload or PR was performed by this producer. Root publisher owns the separate publication gate. No QFRONT, Seibu, walking/FPS or pre-existing asset was changed.
