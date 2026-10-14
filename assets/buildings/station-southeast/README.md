# JR南東側施設（B試作）

PLATEAUのbldg_d7fb4726の壁・屋根を保持し、白い壁の縦長窓・桟・階の帯を追加。2024年1月の駅正面写真は種類の補助。2025年10月の工事状態・施設IDとの対応・窓割り・寸法は未確認。広告・JR文字・工事用囲いをその写真からコピーしない。

地面はCoreとDEM補填へ照会。522点中498点有効・24点未取得。補填の地形は測った仕上げ歩道ではない。元の屋根とT.P.15 m基準を保持する。

```sh
blender -b --python-exit-code 1 -t 4 -P assets/buildings/station-southeast/source/blender/build.py -- assets/buildings/station-southeast/source/data/plateau.json assets/buildings/station-southeast/source/data/layout.json assets/ground/core/web/ground_core.glb assets/buildings/station-southeast/web assets/ground/extension/web/extension.glb
```

外側道路追加後の足元を再生成する場合は、最後の引数へextension.glbとexterior-west/middle/eastの各GLBを順に渡す。追加道路使用時は旧Coreの仮fillを照会から除き、測ったCore面・追加交通面・DEMへ照会する。屋根・上面は保持。
