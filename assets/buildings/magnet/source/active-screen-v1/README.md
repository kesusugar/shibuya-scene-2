# MAGNET active-screen revision, single-target publication

Only the accepted delivered screen quad changes. The permanent MAGNET and Eiraku models are unchanged. Inputs are pinned copies necessary for portable binary patching and editable-scene reconstruction, not new building revisions. ORIGINAL_DELIVERY.md is historical source-package documentation; current evidence is at evidence/magnet-active-screen in the repository root.

## Regeneration

From any working directory run Blender 4.2.3 with:

    blender -b -t 2 --python-exit-code 1 -P /absolute/path/to/active-screen-v1/tools/regenerate.py

This writes output/magnet_signs_2025.glb, output/signage_2025.json, validation.json and an editable blend. The generated GLB/source must equal assets/buildings/magnet/web/magnet_signs_2025.glb and source/data/signage_2025.json. No network, external fonts, reference photos or former ZIPs required. For GLB only use Python source/correct_screen.py --output /absolute/output. The delivered editable blend is preserved byte-for-byte; regeneration is verified structurally, not claimed byte-identical for the blend. It has five packed original placeholder images and imported editable meshes. Editing it does not update the canonical patch script.

The renderer used for current evidence imports the accepted final GLB and takes before positions from the actual current-main byte-identical baseline. All other glTF data is equal, as separately asserted. Both views use the same inherited south camera, 1100×1400, Cycles CPU 24 samples, AgX, direct JPEG quality94. This is asset-only evidence, not a browser/full-scene test. The historical render script remains unchanged; current_render.py is rendering-only and records actual baseline positions.

## Date, geometry and rights

8.64×4.80m follows the operator specification. Height center18.86m is inferred from the photograph in a 2025-10-24 publication; capture date unknown. The inherited cassette conflicts by about0.69m at each photo-mapped edge. Manual-pick center18.72–19.00m is sensitivity only. No surrounding shape was distorted to conceal this.

The existing nominal2025 layer remains enabled exactly as before; artwork is original placeholders, not real campaign art. Mixed 2025/2026 signs are inherited and not certified for October2025. No newly dated advertisement is introduced. No optional layer or shared runtime source is changed. Viewer vertical offset−0.093m applies once; no datum rebasing.

No HUIS or other reference-photo pixels are redistributed. See sources/SOURCE_AND_INFERENCE.md for URLs, dates and restrictions. Existing MAGNET manifest preserves upstream PLATEAU and photo attributions; models are not declared CC0. Unchanged fixed-input GLBs and packed original placeholders retain their original licensing. Full-scene/build/browser/walking/FPS/collision and surveyed accuracy are not claimed.
