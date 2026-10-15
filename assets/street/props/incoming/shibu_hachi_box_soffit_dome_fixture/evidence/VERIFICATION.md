# Verification

Blender 4.2.3 LTS generated GLB, editable blend and original front/side/oblique renders. A separate second process reproduced the GLB byte for byte, SHA256 f726d657ba9d5544d6fde4fa976a6492ff47315294462fbca9206c9e143099d6. Opening the editable blend and exporting also reproduced identical GLB bytes.

The editable-mesh validator confirms 3 meshes, 2 materials, 948 triangles, 0.120 × 0.120 × 0.090 m bounds, all origins at bottom centre, no FILE images, no camera/light objects. GLB size 24,512 bytes. Attachment top-to-soffit gap is approximately 3.6e-9 m (floating-point error) in the provisional parent-local translation, not a measured construction clearance.

Original oblique and attachment-closeup renders were viewed. Pale short tapered housing, shallow top flange and dark hemispherical lower section match the source's visible category, but exact product section and reflectance cannot be recovered at this resolution. An existing PR #64 pavilion GLB is used only for original-render context; its architecture is not bundled or modified. Existing runtime, source files, protected buildings and FPS logic untouched.

No scene build, runtime registration, geographic placement, integrated game screenshot, full-scene performance test or real-camera calibration claimed. Reference photographs/crops/PDF are not redistributed. References and pixel coordinates are recorded in SOURCES.md.
