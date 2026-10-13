# Core ground (C2a)

This asset is the ground of the Shibuya Scramble Core, within 150 m of the crossing centre (OSM node/291758776).
It fixes positions and heights. Northern sidewalk and selected Hachiko plaza walking faces use estimated procedural paver atlases; other materials remain the existing flat colours.

## What it contains
| Object | Source |
|---|---|
| `ground_road`, `ground_intersection` | PLATEAU 2025 road surfaces, LOD3 (車道部 and 車道交差部), at PLATEAU heights |
| `ground_sidewalk` | PLATEAU 2025 歩道部 and 島, see "Sidewalks" below |
| `ground_kerb` | Kerb faces, plus 0.3 m skirts, see "Kerbs and skirts" below |
| `ground_marking` | Zebra bars of the OSM-marked crosswalks, see "Crosswalks" below |
| `ground_fill` | **Provisional** ground (purple-grey), see "Fill" below |

### Sidewalks
- Densified so that no edge is longer than 1.5 m.
- Lifted 0.15 m above the road.
- Drop to 0.02 m within 1 m of a crosswalk band, then ramp back up over the next 1.5 m.

### Kerbs and skirts
- A kerb face is built wherever a sidewalk edge meets the road.
- Every other open edge gets a 0.3 m skirt that hides the seam.

### Crosswalks
- Zebra bars are 0.45 m wide with 0.45 m gaps, and run parallel to the walking direction.
- They are clipped to the road and draped 12 mm above it.
- Widths and centre lines were measured on the GSI orthophoto.

### Fill
- `ground_fill` covers ground that PLATEAU's road data leaves out, such as forecourts and plazas.
- It sits at sidewalk level and excludes building footprints.
- Within 50 m of the centre it is 1.7 % of the area.

## Datum
- The GLB is already in the common datum, world Y = T.P. − 15.000 m, so it is placed at the origin.
- Each building is placed by its `viewer.json` `groundElevationTP`: Y = elevationTP − 15.000.
- The elevation is the lowest finished ground just outside the building's PLATEAU footprint, so no base floats. It is measured by `source/blender/ground_anchor.py` and written to `source/data/ground_anchors.json`.

| Building | Offset | Roof vs PLATEAU |
|---|---|---|
| QFRONT | +0.202 m | +0.10 m |
| MAGNET and Eiraku | −0.093 m | +0.35 m |

## Rebuild
Run these from `assets/ground/core`:

```
python3 source/tools/measure_crosswalks.py <old shibuya-scene-data.json> <GSI z18 tiles dir> source/data/crosswalks_measured.json
python3 source/tools/prepare_ground.py <plateau_core.json> source/data/crosswalks_measured.json source/data/ground_input.json 150
blender -b -P source/blender/build_ground.py -- source/data/ground_input.json web/ground_core.glb source/data/ground_stats.json
blender -b -P source/blender/ground_anchor.py -- web/ground_core.glb <plateau_core.json> source/data/ground_anchors.json
python3 source/tools/write_manifest.py <53393596_tran.gml> <plateau_core.json> <old data json>
```

- `plateau_core.json` comes from `tools/core/plateau_core.py` (PLATEAU 2025 Shibuya-ku).

## Not measured yet (checked against photos in C3)
- The kerb height (0.15 m) and the low kerb (0.02 m).
- The zebra bar and gap.
- The default width of crosswalks the orthophoto could not measure.
- Whether the PLATEAU road heights match the pavement seen in photos, to within 5 cm.
- The ground floor of the station corridor block, which may be open.

## Licences
- PLATEAU: 国土交通省 Project PLATEAU, CC BY 4.0 compatible.
- OSM: ODbL, © OpenStreetMap contributors.
- GSI: 出典：国土地理院（シームレス空中写真）. Used as a measurement reference only.

## 北側歩道の舗装仕上げ（2026-10-13、試作）

北側領域の歩道・島の面へ、写真を貼らずに自作した平板模様を追加。道路・縁石・横断歩道・補填面の材質は保持。面の頂点・標高を動かさず、平面座標のUVで坂でも平板の尺度をそろえる。既存WebGLの露出・歩道色・粗さは変更しない。

平板0.6×0.3 m、目地6 mm、敷設角6.4度は写真の種類を参考にした推定。実測値ではない。X=-80〜50 m、Y=0〜65 m内に重心がある歩道面を試作対象にし、実際の舗装切替位置を確認した境界とは扱わない。模様は2.4×1.2 m周期、1024×512ピクセル、16枚の平板で微小な色差を付けた。法線・凹凸の追加や舗装の高さ変更はない。

```bash
source /workspace/setup-tools/core-env.sh
python3 assets/ground/core/source/tools/make_paving.py assets/ground/core/source/data/paving_layout.json
blender -b --python-exit-code 1 -t 4 -P assets/ground/core/source/blender/build_ground.py -- assets/ground/core/source/data/ground_input.json assets/ground/core/web/ground_core.glb assets/ground/core/source/data/ground_stats.json
python3 assets/ground/core/source/tools/write_manifest.py
```

既存の生成コマンドは、同じフォルダのpaving_layout.jsonがあれば舗装を含めて生成する。設定や目地色を変えたら、先にmake_paving.pyでアトラスを再生成する。BlenderのMultiplyノードがglTFの色係数として出ない場合もあるため、書き出したGLBの舗装材質の係数だけを0.30/0.28/0.25へ明示し、Blender側のTintとそろえる。バッファ内の形状は変更しない。

2025年1月・2月のCC0写真を模様の種類の参考にし、出典・日付・ハッシュはsource/refs/PAVING_REFERENCE_REGISTER.csv。M027は混雑と細い歩道領域のため舗装色の合否には使わない。写真をテクスチャとして加工していない。

初版の目地色は0.60、補正後は0.82。ほかの設定・露出・光は固定。初版/最終版の設定とアトラスをevidence/c2-north-paving/{first,after}/へ保存。別フォルダへ設定をコピーする際はdata/とtextures/の相対関係を維持し、Blenderの4番目の引数でコピーした設定を渡す。

寸法・目地幅・方向・対象境界、実際の舗装色・摩耗・汚れ・凹凸・夜の反射は未達。ハチ公広場の異なる舗装、点字誘導、排水溝、マンホールは今回の対象外で、舗装全体の完成を認定しない。

## ハチ公広場の舗装試作（PR #22後）

`source/data/plaza_paving_layout.json`は赤茶色のブロック・淡い区画線と
推定の対象ポリゴンを記録する。2月の高所写真と10月10日の南西側歩道写真を
種類の参考にした。ブロック0.2×0.1 m、区画6 m、角度・境界・色は未実測。
写真の人物や影は使わず、自作アトラスをGLBへ埋め込む。

```bash
python3 assets/ground/core/source/tools/make_paving.py assets/ground/core/source/data/paving_layout.json
python3 assets/ground/core/source/tools/make_paving.py assets/ground/core/source/data/plaza_paving_layout.json
blender -b --python-exit-code 1 -t 4 -P assets/ground/core/source/blender/build_ground.py -- assets/ground/core/source/data/ground_input.json assets/ground/core/web/ground_core.glb assets/ground/core/source/data/ground_stats.json
python3 assets/ground/core/source/tools/write_manifest.py
```

生成器の第4引数は北側の設定、第5引数は広場の設定。省略時は既定ファイルを使う。
存在しない設定パスを指定するとその材質追加を省略する。北側は歩道・島の面の重心で選択。広場は推定ポリゴンの辺で面を分割し、
道路・縁石・白線・仮補填面を変更しない。元の面の形・高さを維持し、
材質の境界自体は未実測。表面の凹凸、点字・排水、10月の全区画の照合は未達。


## 広場の舗装境界（PR #23後）

`source/blender/paving_boundary.py`で境界辺の延長線に沿って歩道面を分割し、
凹型の領域も扱う。新しい頂点の高さは元の三角形から補間する。
縁石と補填面は分割前に生成し、その形を保持する。三角形重心による
材質の段状境界を解消する処理で、ポリゴンの位置を測量したものではない。
色アトラス、ブロック寸法、区画線、北側歩道の設定は保持する。

詳細・比較・元GLBとの面照合の再実行方法は
`docs/core/C2_PAVING_BOUNDARY_REPORT.md`を参照。
