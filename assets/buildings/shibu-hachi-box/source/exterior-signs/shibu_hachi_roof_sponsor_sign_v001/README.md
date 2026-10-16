# SHIBU HACHI BOX roof sponsor lettering

Independent A15 / H-SG-004 asset. Blender 4.2.3 LTS only.

## Included
- Separate editable SUPPORTED BY mesh, using bundled licensed DejaVu Sans Bold as a neutral approximation.
- Seven independently authored angular G-SHOCK glyph solids, with pale amber lit faces and darker red-orange returns.
- One deliberately plain estimated low dark backing bar. No conjectural posts, bolts, wiring or tall support panel.
- Standalone GLB, self-contained packed Blender file, regeneration and validation Python, three GLB-derived PNG views, provenance, semantic placement guide, validation and timing records.

## Date and scope
The lettering is directly visible in Casio's December 10, 2024 front photograph, whose exact capture date is not stated. The accompanying article says the G-SHOCK installation began November15, 2024. The supplied August8, 2026 side photograph shows the exhibition but NOT this roof sponsor. Consequently this is a 2024-observed dated advertising candidate, not proof of unchanged lettering through2026 or a permanent architectural layer.

Existing SHIBU HACHI BOX lettering, information symbol, dog silhouette and parent pavilion are neither duplicated nor modified. The H-SG-004 G-SHOCK wordmark is included; the separate identity/dog graphic is outside this scope. No fence advertising or gallery artwork is included.

## Scale and integration
- Real metre units; estimated width4.08m, depth0.088m, total height0.44m.
- Origin is the exact bottom center of the entire asset. Blender front -Y/up+Z; GLB uses standard Y-up conversion.
- Roof width12.76m is itself estimated. A367px sponsor span versus roughly1157px full roof gives about4.05m; rounded production width4.08m is an approximate photo-based scale, not a measurement.
- Semantic anchor: right-hand front roof, following the existing facility name/dog graphic. All world coordinates, rotation and installation height remain null.
- Important: the existing estimated identity carrier spans x=-6.40…+3.40m; the photo-inferred sponsor span is approximately x=+0.71…+4.76m. These overlap. Do not blindly apply the suggested span or resize/move the parent automatically. A later integration step must reconcile the carrier against the photographic layout while preserving the approved name.

## Reproduction
Run with the provided exact Blender4.2.3 executable or another installation of the same version:

    blender -b --python source/generate.py
    blender -b --python source/validate.py -- /absolute/path/to/package

For a no-render rebuild in another directory:

    blender -b --python source/generate.py -- --no-render --output /absolute/path/to/rebuild

To export the editable packed blend without regenerating:

    blender -b --python source/export_editable.py -- /absolute/path/to/package /absolute/path/to/result.glb

The generator reads only its bundled open font. It does not load photographs or depend on absolute workspace paths. The blend has no external library links or photo texture, and the font is packed as well as separately bundled. Preview cameras/lights are not included in the model.

## Validation meaning
Source and reimported GLB are tested for finite coordinates, triangle count/area/bounds equivalence, exact bottom-center origin, zero-area triangles, self-contained data and <=4 material batches. Source font geometry is cleaned before export. Topological boundary counts are reported honestly: material-separated face and return batches are individually open, and glTF normal splits add apparent seams. This is not a watertight-all, collision, survey, exact brand-master or runtime/FPS certification.

## Rights and files
All delivered geometry and guide artwork are independently authored. No copyrighted source photographs, crops or photographic textures are included. Source URLs and reference hashes are recorded for reproducibility. DejaVu font license is included. G-SHOCK is a third-party brand; reconstruction does not grant trademark rights or imply endorsement.

Parent-managed private Drive upload only. No repository, runtime, QFRONT, Seibu, walking display, FPS, merge or deployment changes were made.

## Final checked values
4,018 triangles; 4 exported mesh/material batches; 9 editable mesh objects; 162,484-byte GLB. Zero-area triangles:0 in source and reimport. SUPPORTED BY source-font nonmanifold edges:194; manual G-SHOCK solids and backing:0. Boundary edges remain disclosed rather than claiming every mesh is watertight. Source regeneration and direct packed-blend export each produce the exact same GLB SHA-256.
