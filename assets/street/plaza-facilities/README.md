# 広場の小施設（B試作）

2025-10-31のOSM形状に、喫煙設備候補の金属収納箱2基と名称不明の小構造物を制作。全頂点の基礎は既存Core歩道へ照会し、最低点へ1.5 cm埋める。喫煙設備の形状は約1.7×0.45 mで、区画全体を表す足跡とは判断しない。標準的な収納箱・灰皿の種類として高さ1.05 mを推定。高さ9 mの既定の箱を使用しない。

名称不明の小構造物はOSMの平面形を保ち、高さ3.03 mの金属パネル・平屋根・扉・換気口を推定。元台帳の高さと実測値を区別する。喫煙所・案内所などの用途を断定しない。

参照写真は2026年3月の喫煙囲い。フレームと収納箱の種類の補助であり、2025年10月の状態・施設ID・位置の一致として認定しない。写真をテクスチャにせず、囲い全体を小さなOSM形状に縮めて置かない。写真との対応と小施設の外装は未達。

OSM出典: © OpenStreetMap contributors / ODbL-1.0。2025-10-31T23:59:59Zの履歴、Overpass API。元応答をsource/data/osm_2025.jsonへ保存。写真の出典・ライセンスはsource/refs/SOURCES.md。

```sh
blender -b --python-exit-code 1 -t 4 -P assets/street/plaza-facilities/source/blender/build.py -- assets/street/plaza-facilities/source/data/layout.json assets/ground/core/web/ground_core.glb assets/street/plaza-facilities/web/plaza-facilities.glb assets/street/plaza-facilities/source/data/stats.json
```
