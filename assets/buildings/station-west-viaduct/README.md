# 駅西側の高架部 — B試作（写真との対応は推定）

対象 `plateau/bldg_9b0ce3b9-6e8c-4bf9-a86b-4f48e326b324` は元の台帳で駅舎中央部と推定されていた。10月18日の銀座線高架付近の写真を参考に、閉じた箱の下部を桁・柱・補強材へ置換。元のRoofSurfaceの全頂点・T.P.32.3 mを上面として保持し、通常表示のB試作へ追加した。施設IDと写真の対応、各寸法・位置は推定。正式名称・10月全外観の確定ではない。

原点T.P.15 m、上下移動0。C2aへの8支柱位置の照会は範囲外のため0件。足元は元のPLATEAU地面T.P.15.14 mを使い、支柱ごとの地面合わせは未達。中間桁T.P.25.3 mと8支柱は推定。養生網は上面より1.1 m高い推定の軽量表現で、最高値はT.P.33.4 m。

初版の青い板の見え方を、不透明度（alpha）だけ補正。写真の網は透明な面と金属枠で近似し、網目の実寸や光学特性は再現していない。初版はlayout.jsonのbarrier_alpha=1.0、最終版は0.22で再生成できる。広告・発光・写真テクスチャは追加していない。

## 再生成

リポジトリルートからBlender 4.2.3 LTSで実行：

```sh
blender -b --python-exit-code 1 -t 4 -P assets/buildings/station-west-viaduct/source/blender/build_station_viaduct.py -- assets/buildings/station-west-viaduct/source/data/parts.json assets/buildings/station-west-viaduct/source/data/layout.json assets/ground/core/web/ground_core.glb assets/buildings/station-west-viaduct/web
```

1,332三角形・5描画単位・78,096 bytes。Cから同じIDを一度だけ除外。`context=nostation`で駅側4資産を消し、既存5資産を残す。推定を台帳・HUDへ記載。

出典はsource/refs、報告は `docs/core/C1_STATION_VIADUCT_REPORT.md`、画像は `evidence/c1-station-viaduct/boards/`。
