# SHIBU HACHI BOX: missing roof identity icons

Two standalone subtasks within existing H-SG-001. The master ledger remains 108 rows. Existing roof name, carrier and sponsor were not duplicated or modified.

## Deliverables
- roof_information_circle.glb: pale circular disk and authored dark lowercase i. 0.46 × 0.039 × 0.46m (width/depth/height), 580 triangles, 2 material batches.
- roof_seated_dog.glb: approximate right-facing seated silhouette and low plinth. 0.50 × 0.032 × 0.52m, 220 triangles, 1 material batch.
- Two self-contained editable .blend files, one per asset. Circle disk, stem and dot remain separate editable objects. Dog is one closed mesh.
- Self-contained Python generator, direct editable exporter and validator. No font, photo, texture or downloaded brand master needed.
- Three PNGs rendered from the final exported GLBs, source/provenance/estimates, photo-normalized observations, validation, reproduction and timing records.

## Placement is not solved
Both assets have independent bottom-center local origins, Blender front -Y/up +Z, metres. GLB uses standard Y-up conversion. All world translation/rotation/scale/installation height values are null.

The circle belongs before SHIBU HACHI BOX; the dog belongs between BOX and SUPPORTED BY. Neither replaces the existing doorway i or counter placard. The pair preview is an inspection staging, not the actual sign order or spacing.

Existing imported name spans x=-5.9052…-2.59037m. The existing estimated carrier spans x=-6.4…+3.4m and conflicts with photo-inferred sponsor placement. Do not automatically force, resize or overlap the new icons against those ranges. Photo-normalized anchors document observations only; reconciliation belongs to later assembly. No installed fit is claimed.

## Fidelity and rights limits
The official CASIO front photo, published 2024-12-10, is the visual source. Capture date is unknown; 2026 persistence is not confirmed. Metric dimensions, depths, backs, physical i construction and materials are estimates. The dog is deliberately a coarse source-supported silhouette, not an exact trademark master. No detailed face, fur or unsupported fittings are invented.

Night-photo bloom and cool cast do not calibrate real color or emitted light. Preview illumination is illustrative. Source photos and crops are not redistributed, embedded or used as textures. Geometry is independently authored; reproducing a third-party identity mark does not grant trademark rights or imply endorsement.

## Rebuild and verify
Use exact Blender 4.2.3 LTS:

    blender -b --python source/generate.py
    blender -b --python source/generate.py -- --no-render --output /absolute/path/to/rebuild
    blender -b --python source/validate.py -- /absolute/path/to/package
    blender -b --python source/export_editable.py -- /absolute/path/to/package /absolute/path/to/reexport

Both clean-room regeneration and direct packed-blend re-export match the delivered GLB SHA-256 exactly. Source and reimport: zero degenerate triangles, finite coordinates and equivalent bounds/triangle count/surface area. Source meshes and reimported meshes after welding normal-split vertices have zero nonmanifold edges. These are asset checks, not collision/self-intersection/runtime/FPS certification.

Parent-managed Drive upload only. No runtime, QFRONT, Seibu, walking/FPS, Codex, GitHub, merge or deploy operation. No source photograph is included. The original 108-row inventory and PROGRESS files were read, not edited by this worker.
