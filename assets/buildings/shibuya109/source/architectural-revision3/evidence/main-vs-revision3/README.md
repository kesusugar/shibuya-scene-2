# Actual main versus accepted revision3

Fresh same-camera comparisons, not the historical a31 input comparison. Left: main8633c1b7, introduced through PR35/36/37. Right: accepted revision3, including the full cumulative roof/cap/logo/cylinder/wing and entrance/stair/opening changes. Both preserve scene coordinates and viewer datum15m. Render plane is neutral staging only and is not shipped geometry.

The exact actual-main model is inputs/current-main.glb. To reproduce in a writable copy of this folder, copy that file to inputs/prior.glb (a renderer slot name ONLY; it is not the source generator predecessor). Copy the canonical asset web/shibuya109.glb to output/combined/shibuya109.glb. Then run:

    SAMPLES=16 VIEWS=overall,entry-front RENDER_SET=current-main blender -b --python-exit-code 1 -P scripts/render_evidence_framed.py -- before
    SAMPLES=16 VIEWS=overall,entry-front RENDER_SET=accepted-revision3 blender -b --python-exit-code 1 -P scripts/render_evidence_framed.py -- combined

Both scripts are the exact rendering code used, kept separate from generation. PNG hashes in the receipt record original renders; boards are JPEG95 labeled side-by-side copies without image generation, geometry edits, or camera changes. Full-scene execution and FPS are not represented.
