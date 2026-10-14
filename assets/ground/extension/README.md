# Core外側の地形補填

国土地理院の標高タイルDEM5Aを使い、元のCore地面の外側だけを6 m格子で補填。元の地面を再書き出しせず保持。元の境界から20 mは既存面の最寄り点の補間高さへ滑らかにつなぐ。これは推定の継ぎ目で、DEMそのものの値や実測の仕上げ舗装とは区別する。道路・歩道・工事状態・床高・縁石は未収録。通常表示・歩行の地形として使うが、正確なバリアフリー経路として認定しない。

出典: 国土地理院「標高タイル」、DEM5A zoom 15（出典URLはsource/data/source.jsonとタイル番号）。2026-10-13取得。撮影・測量年はこの取得日から推定しない。国土地理院コンテンツ利用規約: https://www.gsi.go.jp/kikakuchousei/kikakuchousei40182.html 。加工して利用。

原点35.6595,139.7005、東X/北Y、T.P.15 m。元の面を2 mm外側へクリップする保護マージンがある。既存交差点の歩行面は保持し、補填は独立読み込み。取得失敗でもCoreは続く。

```sh
node assets/ground/extension/source/tools/extract-ground.mjs assets/ground/core/web/ground_core.glb /tmp/original-ground-triangles.json
python assets/ground/extension/source/tools/prepare.py assets/ground/extension/source/data /tmp/original-ground-triangles.json
blender -b --python-exit-code 1 -t 4 -P assets/ground/extension/source/blender/build.py -- assets/ground/extension/source/data/extension.json assets/ground/extension/web/extension.glb
```

`dem.txt` は29099/12905、ほかの3ファイルはファイル名にタイル座標を保持する。

## 周辺建物追加時の範囲拡張

外側を東西-330〜380 m、南北-450〜350 mへ拡張し、6 m格子へ。補填の高さはsource/data/stats.json、元のCore地面は保持。遠方の建物の足元の地形を収録するが、道路・歩道仕上げの再現ではない。

外側道路の追加後はCore+3道路タイルの三角形を保護マスクへ渡し、仕上げ面の下にDEMを重ねない。継ぎ目20mの補間は道路モデルの高さへ接続する推定。Core原本は保持。
