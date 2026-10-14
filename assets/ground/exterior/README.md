# Core外側の車道・歩道

2025 PLATEAU交通4タイルを使用。元Coreの測った道路・歩道+2cmを除外し、LOD3優先、未収録範囲だけLOD2を使用。Polygonの内周穴を保持。元の建物・道路・高度な街路資産は変更しない。

入力のT.P.0は高さ欠測として、GSI DEM5A・Core継ぎ目補間で推定（12,378入力頂点、重複を含む）。歩道を15cm、横断歩道の端では2cmとし、1m平坦/1.5mスロープの標準値を使用。元の地面モデルと同じ推定規則であり、仕上げ高の実測ではない。交通データの更新時点と写真の2025年10月一致は未確認。

西・中央・東の3資産へ分割して各ground予算内。島の分類はBVHで行い、Core生成器の全ポリゴン探索を避ける。歩道細分最大3m。白線8帯はCore横断歩道データを外側に切った部分のみで、外側の全横断歩道・全白線を網羅しない。敷石・店舗前区画・点字の全経路は未達。

再生成（リポジトリroot、Blender 4.2.3、Python/numpy/shapely/scipy）：

```sh
node assets/ground/extension/source/tools/extract-ground.mjs assets/ground/core/web/ground_core.glb /tmp/core-tri.json '^ground_(road|intersection|sidewalk)$'
# source/data/sources.jsonのGML4本とTrafficArea/AuxiliaryTrafficArea function.xmlを同じ入力ディレクトリへ取得
python assets/ground/exterior/source/tools/extract.py /tmp/tran assets/ground/exterior/source/data/traffic.json
python assets/ground/exterior/source/tools/prepare.py assets/ground/exterior/source/data /tmp/core-tri.json assets/ground/core/source/data/crosswalks_measured.json
python assets/ground/exterior/source/tools/split.py assets/ground/exterior/source/data /tmp/core-tri.json assets/ground/extension/source/data
for part in west middle east; do
  blender -b --python-exit-code 1 -t 4 -P assets/ground/exterior-$part/source/blender/build.py -- assets/ground/exterior-$part/source/data/input.json assets/ground/exterior-$part/web/exterior-$part.glb assets/ground/exterior-$part/source/data/stats.json /tmp/no-paving.json /tmp/no-plaza.json
done
```

最後の2引数は存在しないファイルを指定し、Core用敷石区画を外側へコピーしない。生成後の仕上げ面をextract-groundで抽出しCore三角形と合わせ、extensionのprepare.pyに渡す。DEM補填を道路の外側だけへ作り直す。

通常表示では追加道路とDEMの両方が正常にロードされた場合だけ、元Coreの仮のground_fillを表示から外し、道路・DEMへ置き換える。Core GLB自体はバイト一致を維持。いずれか失敗した場合は元fillを表示する。測った車道・歩道・白線・縁石は保持。足元生成でも追加道路使用時は旧Core fillを照会から除く。白線端のレイが2cm以内で外れた場合は最も近い書出し道路三角形へ補間し、z=0に落とさない。
