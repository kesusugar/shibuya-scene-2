# SHIBU HACHI BOX front terrace candidate v001

水平5スパンと傾斜3スパンの手すり、5枚の広告、前面のデッキ・幕板を一つのローカル座標系にまとめた、独立した確認用候補です。建物本体への配置、旧床の置換、地面との接続は行いません。広告の大きさ・輪郭は維持し、盾図形だけは重複面による表示不良を候補側で修正しています。時計図形は変更せず、上下端が枠に隠れる仮説を明記しています。

## Candidate scope

- Five-span level rail and three-span descending rail, joined through **one shared knee upright**. Original duplicate knee posts remain in the hidden baseline, not the main export.
- The original ramp shell, unchanged in size and shape, plus a new visible level deck/fascia shell. Both meet at the same local high datum and lower contour.
- Five source-derived mesh graphics at scale `[1, 1, 1]`: ABSOLUTE TOUGHNESS, black G-SHOCK, watch-case silhouette, red G-SHOCK and SHOCK RESIST shield. Four retain their original geometry. The shield receives a candidate-only exact union of its border and lower triangle to remove coplanar overlap, preserving its silhouette, 11 text components and 0.6 mm depth. No artwork is cropped, stretched or redrawn; the shield topology is explicitly changed.
- A derived sloped-rail refit from a 28.5 px fall to the ramp's 28 px fall. The maximum change over the post-centre run is 5.890 mm; the original source asset is untouched.

The main GLB contains the candidate only. The editable BLEND preserves separately labeled, hidden baseline inputs, with original GLBs retained for reversibility. The older pavilion shell and its floor remain unchanged. This package does not replace the complete building.

## Files and review order

1. `shibu_hachi_front_terrace_candidate_v001.glb`: candidate-only export.
2. `shibu_hachi_front_terrace_candidate_v001.blend`: editable assembly and hidden baseline.
3. `evidence/01_overall_front_terrace.png` and `evidence/02_watch_and_shared_knee_detail.png`: the overall terrace and a near-frontal detail spanning the watch, shared knee and first slope span. These are model views, not source photographs.
4. `source/generate.py`, `source/glb_geometry.py`, `source/repair_shield.py` and `source/check_shield.py`: regeneration, geometry validation, the declared shield repair and overlap verification. `inputs/`: immutable baseline GLBs, including the original shell and unmodified shield.
5. `references/`: the assembly proposal, numeric calculations, protected-input snapshot and applicable font notice. No reference-image pixels are included.
6. `ASSUMPTIONS.md`: construction hypotheses, coordinate conversion and unresolved interfaces.
7. `PROVENANCE.md`: input lineage, reference URLs, date limits and rights. `placement_reference.json`: machine-readable local placement and normalization record, not a world-placement instruction.

## Coordinates

Authoring units are metres: +X runs right/descending, -Y faces the public/front, and +Z is up. Before export normalization, the shared knee is X=0 and its high shell/support datum is F=0.248 m. This inherits an existing model floor elevation only.

The final asset is normalized to the **actual candidate AABB bottom-centre**, not a surveyed ground point. Recorded raw bounds are approximately X `[-7.981335640, 3.752020597]`, Y `[-0.020, 0.880]`, Z `[-0.164328769, 1.108000040]` m. The recorded normalization adds `[2.114657402, -0.430000007, 0.164328769]` m in authoring XYZ. Reimported normalized size is **11.733356476 × 0.900000006 × 1.272328854 m**, within float32 precision of the design values. Full-precision transforms are in `placement_reference.json`.

Undoing that translation recovers the local shell-floor datum. It does **not** recover site ground, a whole-building XY fit, a parent transform or a world placement. See `ASSUMPTIONS.md` before integrating. glTF uses +Y up and +Z public/front; the vectors above are authoring coordinates, not glTF translation vectors.

## Read these limits before reuse

- The rail underside and fascia top use a local butt-support hypothesis. Source-image edges y414 and y418 are distinct observations; no physical joint has been proven.
- The watch graphic touches the clear pane's front but sits behind the opaque frame. Its upper and lower extremes intentionally overlap the frame volume. About 6.77% of its front ink area is expected to be masked. There is no hidden backing glass and no claim of a physically certified decal installation.
- The shell is an estimated 0.900 m deep, with technical 20 mm skins. It is not a solid foundation, measured cladding or verified structural assembly.
- The descending shell stops at observed R3, with positive fascia height. The continuation, right terminal and ground connection remain unknown.
- The graphic layer is based on an article published in 2024; persistence in 2026 is unverified.

No QFRONT, Seibu Shibuya, walking display, FPS, runtime registration, terrain, collision-system integration, merge or deployment changes are included.

## Build and verification status

Use **Blender 4.2.3 LTS**. From the package directory, regenerate the asset and evidence with:

    blender -b --threads 4 --python source/generate.py

For one separate-output no-render regeneration:

    blender -b --threads 4 --python source/generate.py -- --no-render --output /tmp/front_terrace_regeneration

Preserve the supplied inputs; no source photographs, network access or external fonts are needed for this assembly.

**Corrected geometry verification, visual review and one final separate-output regeneration passed.** `evidence/validation.json` records:

- Actual GLB reimport: 30 meshes, 8,440 triangles, finite vertices and no degenerate triangles. The asset contains eight clear spans, nine posts including one knee, four upper/lower bars, four visible skins and five graphics.
- Four graphic triangle counts preserved, with at most 0.267 micrometres inverse-translation vertex error from float32 export. The repaired shield has 3,156 triangles instead of the original 3,100. Its outline, text, scale and depth are retained, but its topology is not unchanged.
- `evidence/shield_actual_export_check.json` records zero positive coplanar front-triangle overlaps in the actual delivered shield. The original lower triangle overlapped four border triangles by a total 0.0009778013535 m². The candidate-only union removes that defect without editing the source GLB.
- No accidental positive-volume overlaps under the exact-prism and projected-ink tests. Only the declared watch/upper-and-lower-frame overlap is present, masking 6.772163% of its reimported front ink area; the other graphics have no masked ink in this test.
- Saved BLEND reopened with hidden baseline retained, including all five original shell material batches. The self-contained main GLB excludes the baseline, cameras, lights and source-image textures.
- Nine packaged input GLBs match their source hashes; see `evidence/source_protection.json`. All 14 original source paths also match the research snapshot; see `evidence/protected_originals_verified.json`.

Both PNGs were rendered again once to verify the shield-defect correction, then inspected. The overall view shows eight spans and deck/ramp continuity; the detail shows the unchanged watch naturally masked by the frame and the single shared knee. The corrected shield no longer shows the detected overlap artifact. This is a bounded local visual candidate, not a site-fit approval. The additional render pass was a defect correction, not an unrelated cosmetic variant.

The delivered GLB and BLEND come from one final corrected no-render regeneration. Its geometry BIN chunk is byte-identical to the corrected rendered export, and statistics and placement data match. Export JSON differs only in the shield's explicit `transform_only_no_scale` metadata flag, corrected from `true` to `false`. **Full-GLB byte identity to the rendered export is not claimed.** `evidence/reproducibility.json` records final GLB SHA-256 `6198b2ee3c7d9ce114c9d738f80d72d42aac32610437c715cedd4b7bcfd554df`.

One earlier regeneration predates the shield repair and is retained separately as `evidence/pre_shield_repair_reproducibility.json`; it does not validate the final corrected asset. The final no-render regeneration did not trigger another render pass.

These checks validate the bounded review candidate, not surveyed dimensions, real support construction, accessibility compliance, current-2026 appearance or complete scene integration.
