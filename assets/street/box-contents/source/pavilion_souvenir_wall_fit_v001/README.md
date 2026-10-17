# SHIBU HACHI BOX souvenir-wall partial review v001

日本語要約: 既存の陳列網・6箱棚・木壁を部分断面としてまとめました。既存パネル1枚の同一形状インスタンスだけで上部の木壁を続け、ルーバーは右側に保持しています。床・窓・実際の支持は未確定です。壁の下端1.10 mは切り取り位置で、床ではありません。追加商品・全館内装・取付金具は作っていません。

**A bounded, translation-only assembly of existing assets, not a full room or verified installation.** This advances queue item 4 only to the extent supported by the two 2024-published interior photographs. Physical floor support, a window relationship and the final pavilion placement remain unresolved.

## What is assembled

- H-IN-014: the existing wire fixture, two wire shelves and 13 provisional hooks, unchanged.
- H-IN-015: the existing six independent box carcasses, still two columns × three tiers, unchanged.
- H-IN-001 / H-IN-002: the existing ten-part counter-derived wood-wall/louver sample, unchanged and translated to the right/up.
- One linked instance of the sample's existing broad vertical wood panel extends its upper wood surface behind the souvenir fixtures. This reuses the exact mesh and material, not new unique geometry or another inventory object. It does not extend down to a floor.

The wire fixture is left of the boxes. The counter-derived louver remains to their right. The counter photo's large dark rectangle is a monitor; no window is inferred or modeled. Merchandise, signs, hidden anchors, extra storage, counters, paper, full room, floor and skirting are excluded. Empty shelves are furniture-only scope, not a claim that the photographed display was empty.

## Critical cut-edge distinction

**Review Z=0 is only the inherited fixture-model base datum, not an established floor elevation.** The lower ends in the souvenir photograph are cropped. No floor plane, technical render floor, or floor contact assertion is included.

**The wood section begins at review Z=1.10 m, a sample cut, NOT a floor/contact edge or real wall termination.** Both the main sample and the one extra linked panel keep this cut. The upper-left panel ends at its source's 1.208 m height; its exposed top is another sample boundary. No missing lower continuation is filled.

The full review envelope is approximately 5.30 m wide × 0.457 m deep × 2.50 m high. That is the composition envelope of estimated, unscaled source assets, not a recovered room width or measured space. All numerical translations, depth clearances, the common fixture datum and the implied adjacency remain modeling estimates. The published promotion-space bay dimensions are not used to calibrate this section.

## Files

- `pavilion_souvenir_wall_fit_v001.blend`: editable original mesh parts, original materials and packed original textures, four reversible assembly roots; no render helpers.
- `models/pavilion_souvenir_wall_PARTIAL_REVIEW.glb`: one combined local partial-section review, suitable for inspection only. Do not import it alongside its standalone source assets or regard it as an approved runtime installation.
- `images/01_front_partial_section.png`: actual combined-GLB reimport front render showing all six openings and the lower cut.
- `images/02_oblique_depth_and_cut.png`: actual combined-GLB reimport oblique render showing fixture depth, wall separation and the incomplete section. Both images have render-only captions and no ground mesh.
- `transforms.json`: group, all editable-part, and six-carcass transforms and bounds, with source matrices for reversal.
- `REPORT.md`, `PROVENANCE.md`, `validation/`: arrangement rationale, limits and focused inter-asset checks.
- `inputs/`: exact copies of the two original editable blends for reproducibility; original folders are unchanged.
- `source/assemble_review.py`: appends those inputs and applies only documented root translations plus the one linked panel instance; does not invoke source generators.
- `source/export_editable.py`: exports the current edited blend's assembly collections without recreating the assets or replacing edits.

## Use and export

Exact authoring binary: `tools/blender-4.2.3-linux-x64/blender`, Blender 4.2.3 LTS, build `0e22e4fcea03`.

Rebuild this composition from preserved inputs, including its two inspection renders:

    tools/blender-4.2.3-linux-x64/blender -b -t 2 --python pavilion_souvenir_wall_fit_v001/source/assemble_review.py -- pavilion_souvenir_wall_fit_v001

Export an edited copy without regenerating it:

    tools/blender-4.2.3-linux-x64/blender -b -t 2 --python pavilion_souvenir_wall_fit_v001/source/export_editable.py -- edited.blend edited_PARTIAL_REVIEW.glb

Metres. Blender Z-up / front -Y; glTF Y-up / front +Z. All assembly roots have unit scale and zero rotation. No world position is assigned. Preserve the distinction between the fixture base datum and the wall cut. Original individual assets remain authoritative for their detailed source limitations.

## Stopping point

The bounded partial-section result is complete. Floor-supported placement and window interference cannot be established from these photographs and are explicitly not complete. A contextual view containing the souvenir fixture bottoms, the actual floor and the wall/adjacent opening would be needed for that next step. No full-room extension, source-asset regeneration, existing counter/paper-fit review, runtime import, QFRONT/Seibu change, walking/FPS change, GitHub write, merge or deployment was performed.
