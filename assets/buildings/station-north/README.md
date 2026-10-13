# JR北側ホーム上屋（部分B試作）

2025-10-11のCC BY 4.0写真を参考に、北側上屋を開放し、柱・梁・天井・照明・点字帯を追加。屋根の元の頂点と絶対高さを保持した。南側施設とJR高架全体は元のC形状を保持し、完成Bとして扱わない。

柱・梁・帯の位置と寸法は推定。写真GPS、屋根までの距離、元の高架床T.P.21.29 mは候補同定の補助であり、写真カメラの校正・画素誤差計測は未達。写真をテクスチャには使っていない。

## 再生成

リポジトリルートから、Blender 4.2.3 LTSを使用：

```sh
blender -b --python-exit-code 1 -t 4 -P assets/buildings/station-north/source/blender/build_station_north.py
```

`source/data/parts.json`は元の施設と高架の入力、`layout.json`は推定の配置と補正の根拠、`stats.json`は生成結果。共通原点のT.P.15 mを使い、地面へ一括移動しない。C2aの地面と既存入力を必要とする。

通常表示に追加し、`context=nostation`で駅側二資産を除外。推定箇所の注記は通常のHUDで表示する。

検証・前後画像・残る差は[報告](../../../docs/core/C1_STATION_NORTH_REPORT.md)。996三角形、9描画単位、68,400 bytes。
