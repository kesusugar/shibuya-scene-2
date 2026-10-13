# 駅西側の小施設 — B試作（名称・写真対応は推定）

対象は `plateau/bldg_5369333e-5975-493a-b05d-b341800715c2`。台帳ではハチ公口側の駅舎と推定されていたが、正式な施設名は未確認。2025-10-18写真の白い設備棟候補を参考に、住宅風の共通窓を白い金属パネル、目地、推定の換気口へ置換した。元のPLATEAUの全外形・屋根頂点を保持。正面同定・10月の全外観を完了したとは扱わない。

目地・換気口の種類・配置・寸法は推定。初版の目地幅0.07 mを、比較後に0.025 mへ一項目だけ補正。初版はlayout.jsonのjoint_width_mを0.07へ戻して再生成できる。広告と照明は追加していない。

共通T.P.15 m基準、上下移動0。地面52点T.P.15.300〜15.501 mを測り、元の床下端15.439 mより低いところを裾で塞ぐ。屋根の差0 m。施設の裾は測った地面に合わせた推定で、実際の基礎構造の測量ではない。

## 再生成

リポジトリルートから、Blender 4.2.3 LTSで実行：

```sh
blender -b --python-exit-code 1 -t 4 -P assets/buildings/station-service/source/blender/build_station_service.py -- assets/buildings/station-service/source/data/parts.json assets/buildings/station-service/source/data/layout.json assets/ground/core/web/ground_core.glb assets/buildings/station-service/web
```

342三角形・6描画単位・24,288 bytes。通常表示の一覧に追加し、同じIDのCを除外。`context=nostation`では駅側3資産を消す。推定は通常HUDと台帳へ記録した。

出典はsource/refs。view.tokyoの画像はURL参照だけで、モデルテクスチャ・比較板・リポジトリへ転用していない。報告は `docs/core/C1_STATION_SERVICE_REPORT.md`、画像は `evidence/c1-station-service/boards/`。
