# 渋谷フクラス / Tokyu Plaza: bounded facade revision

way/55588118. The complete PLATEAU shell and roofs, original mesh attributes/index buffers, source datum T.P.15, source top T.P.120.899, and all135 recorded foot samples are retained. No whole-building translation or equal-floor division.

Only source wall76 (north),81 (east), and confirmed joining facet135 receive the new treatment below source z83.9. Fine panes, explicitly grouped silver infill, tall lower corner glazing, three broad east-side returns and a localized cap replace the old uniform18-row/checker/sign-strip overlays. The tiny joining facet is not a new rounded podium. The full source shell remains opaque; diagonal circulation relief is a restrained depth cue, not a surveyed staircase or open interior.

## Regenerate exactly

Blender4.2.3 LTS, no add-ons:

    blender -b --python-exit-code 1 -t 4 -P assets/buildings/fukuras/source/blender/build.py

The asset-local script reads unchanged plateau.json plus source/data/baseline.glb (exact main275f832 export, SHA256 e25a48ed0f4792088de9e5dfed71db2249e5a7b95f71b9d7cf866bde6a8069bb) and baseline_stats.json. It writes web/fukuras.glb, source/data/stats.json, facade_map.json, and packed source/blender/fukuras.blend. No shared builder changes; no ground GLB needed because original footing geometry and sampling evidence are preserved, not remeasured. layout.json documents dimensions; the explicit pane patches and level arrays are in build.py.

## Source and limitations

See source/refs/FIDELITY_SOURCES.md and docs/core/FUKURAS_FIDELITY_REPORT.md. All dimensions except source shell anchors are estimated. No photo texture, signage extraction, invented luminous outlines, or new lettering. Non-target walls, lower north wing104, higher stepped/service portions, roof equipment, interiors and unseen base remain the inherited approximation. The permanent TOKYU PLAZA lettering remains missing.

Actual isolated Blender before/after renders share cameras and lighting. Photo-angle labels indicate comparable viewing direction only, not calibrated photo alignment. No new full-scene asset-completeness or owner-PC FPS claim. Strict asset-local tests and existing Fukuras roof/C-exclusion test pass; complete repository suite needs unavailable large scene assets.
