# 渋谷フクラス

PLATEAU 2025の元の壁・屋根を保持し、個別の窓と桟・腰壁・空の看板筐体を追加したB試作。窓割り・色・階の分割は推定。参照写真の撮影年はsource/refs/reference.jpg.jsonに記録し、2025年の現況とは扱わない。写真をテクスチャに使用せず、広告を複製しない。平和クワトロの外観はセンター街写真の補助に留まり、建物個別の写真対応は未確定。

地面は元のC2aへ照会するが、範囲外はstatsのmissing_pavement_samplesに記録。建物全体を移動して屋根高さを合わせることはしない。

```sh
blender -b --python-exit-code 1 -t 4 -P assets/buildings/fukuras/source/blender/build.py -- assets/buildings/fukuras/source/data/plateau.json assets/buildings/fukuras/source/data/layout.json assets/ground/core/web/ground_core.glb assets/buildings/fukuras/web
```

## 地形補填後の追記

Core外側をDEMで補填した後の照会結果はstats.jsonとC1_STATION_FINISH_REPORT.md参照。補填は地形の推定であり、実際の仕上げ歩道を測った高さではない。屋根・上面は保持。生成時に最後の引数へ `assets/ground/extension/web/extension.glb` を追加する。旧い未取得の記録は当時の結果として保持。

外側道路追加後の足元を再生成する場合は、最後の引数へextension.glbとexterior-west/middle/eastの各GLBを順に渡す。追加道路使用時は旧Coreの仮fillを照会から除き、測ったCore面・追加交通面・DEMへ照会する。屋根・上面は保持。
