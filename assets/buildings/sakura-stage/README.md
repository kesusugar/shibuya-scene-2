# Sakura Stage SHIBUYA Tower

PLATEAU 2025の元の壁・屋根を保持したB外装。窓割り・色・桟・屋上の空の看板筐体は写真の種類を参考にした推定。広告画像・古い工事状態はコピーしない。109の立体数字は2019年の形の補助を見た自作近似で、現在の字形・色・寸法・点灯までの一致は未確認。

source/data/plateau.jsonの高さはT.P.、ringのZはT.P.-15 m。屋根を移動しない。足元はCore/国土地理院DEM地形へ照会、仕上げ歩道の測量とは区別。元データファイルの出典・ハッシュはdocs/core/NEARBY_SOURCE_FILES.json、写真はsource/refs/SOURCES.md。形の照合に用いた旧OSM平面形は2026-09-08取得で、2025年の写真同定として認定しない。

```sh
blender -b --python-exit-code 1 -t 4 -P assets/buildings/sakura-stage/source/blender/build.py -- assets/buildings/sakura-stage/source/data/plateau.json assets/buildings/sakura-stage/source/data/layout.json assets/ground/core/web/ground_core.glb assets/buildings/sakura-stage/web assets/ground/extension/web/extension.glb
```

外側道路追加後の足元を再生成する場合は、最後の引数へextension.glbとexterior-west/middle/eastの各GLBを順に渡す。追加道路使用時は旧Coreの仮fillを照会から除き、測ったCore面・追加交通面・DEMへ照会する。屋根・上面は保持。
