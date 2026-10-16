# Front terrace provenance and rights

## Source observations and dates

- **CASIO article:** https://note-pr.casio.co.jp/n/n848d1c101d53 . Published 2024-12-10; photograph capture date unknown. The near-frontal image supports five level spans, the descending visible run, the tapered fascia and five graphic zones. The article dates the campaign to 2024. This package treats the graphics as a **dated-2024 layer**, not proof of their persistence in 2026.
- **Operator notice:** https://shibuyaplusfun.com/news/detail/?cd=000153 . Associated operator PDF: https://shibuyaplusfun.pictona.jp/scc-admin/asset/shibuyaplusfun/000002/000002/d58a90d1.pdf . The prior research inspected pages 1–2. The H800 × W7600 mm front advertising specification informs approximate scale but does not establish outer-frame dimensions. Plan annotations do not establish the candidate's elevation, deck depth or whole-building fit.
- **Official TKTS location:** https://tkts.tokyo/location-list/shibuya . Photo: https://tkts.tokyo/img/shop/shibuhachi-t.jpeg . Publication and capture dates unknown. It corroborates foreground framing, while people obscure the descending continuation. It does not verify the right terminal or a current-2026 state.

The source URLs identify evidence; no source photographs, PDF pages, crops or source-pixel textures are redistributed. Acquisition/review dates must not be substituted for capture dates.

## Input lineage

The assembly derives from these existing, independently authored project assets:

- `shibu_hachi_five_span_level_rail_v001`: five-span level rail at original scale; only candidate knee ownership and joining geometry are derived.
- `shibu_hachi_three_span_sloped_rail_v001`: three-span sloped rail; candidate-only 28.5-to-28 px fall refit and shared-knee treatment are disclosed in `ASSUMPTIONS.md`.
- `shibu_hachi_visible_ramp_shell_v001`: ramp shell retained at original scale and shape.
- `pavilion_assembly_review_v003/modules/rail_01_ABSOLUTE_TOUGHNESS_white.glb` through the corresponding `rail_05_SHOCK_RESIST_shield_white.glb`: five original graphic inputs. Four candidate graphics retain their geometry. The shield's border/lower-triangle overlap is exact-unioned in the candidate only, preserving its outline, text, scale and depth while changing topology. No graphic is rescaled, trimmed or redrawn.

The graphics originate in `shibu_hachi_front_rail_graphics_2024_v001`. They are authored mesh approximations of visible lettering, a watch-case silhouette and a shield, not supplied brand-master artwork. The upstream lettering used DejaVu Sans Bold; its notice is retained in `references/DejaVu_LICENSE.txt`. This assembly reuses the mesh artwork and repairs only the shield's overlapping border/triangle topology; it does not regenerate type or require external font files. Preserve applicable upstream notices if redistributing source/font assets.

The independently authored new contribution is the visible level deck/fascia shell and reversible local assembly, including the shared knee, documented slope refit, shield topology repair, transforms, original model renders and verification material. The original pavilion shell, existing floor and all original input GLBs, including the shield, remain unchanged. Baseline GLBs and separately hidden baseline objects preserve the inputs; only the candidate belongs in the main export.

## Numerical evidence and preservation

The production basis is retained in `references/LOCAL_ASSEMBLY_PROPOSAL.md`, `references/NUMERIC_ALIGNMENT_AND_WATCH.json` and `references/INPUT_SNAPSHOT_AND_RAW_TRANSFORMS.json`, originally prepared in `pavilion_local_alignment_research`. These distinguish proposed transforms from surveyed placement, record exact contour/occlusion calculations and list 14 protected source paths with sizes and SHA-256 hashes, including the original pavilion and shell. They retain the initial transform-only graphic proposal as historical source material; the subsequently diagnosed shield repair is the declared final-candidate exception. A source snapshot is a preservation baseline, not by itself proof that a later build left every input unchanged.

The original watch GLB SHA-256 is `b2f91b963eec187601249ddaa1cf0b64407affcbeab9839b6ac8c034b2f631cf`. Its full geometry is preserved despite the explicitly modeled frame occlusion. `evidence/source_protection.json` verifies the nine packaged input GLBs against their source hashes, and `evidence/protected_originals_verified.json` separately verifies all 14 original paths against the research snapshot after the repair. `evidence/validation.json` reports actual export/reimport, preservation of the four unchanged graphics, shield repair and intersection checks. `evidence/shield_actual_export_check.json` records the original coplanar defect and its removal from the delivered shield.

Both corrected PNGs were reviewed after a defect-driven rerender. `evidence/reproducibility.json` records one final corrected no-render regeneration with a byte-identical geometry BIN chunk and matching placement/statistics. The shield's transform-only metadata flag was corrected, so complete GLB byte identity to the rendered export is not claimed. The earlier pre-repair regeneration remains separately labeled in `evidence/pre_shield_repair_reproducibility.json`. These results verify the stated candidate scope, not physical construction or world placement.

## Rights and distribution boundary

The package includes authored geometry, mesh approximations, code, numerical observations, documentation and model-render evidence. No redistribution license has been established for the external source imagery or PDF, so those pixels are excluded. Referencing a URL does not grant rights to copy its contents.

Source copyrights, product designs, names, logos and trademarks remain with their respective owners. Authored mesh redraws are not licensed official logos, brand-master files or an endorsement. This package grants no new rights in third-party photographs, marks or designs and makes no blanket public-domain or unrestricted-redistribution claim for them. Keep existing project and dependency notices with the corresponding materials.

The package makes no structural, accessibility, physical-installation or current-condition certification. Publication of this review candidate does not authorize scene integration, merge or deployment, and it includes no changes to QFRONT, Seibu Shibuya, walking display or FPS.
