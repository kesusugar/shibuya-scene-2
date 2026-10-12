# Core の周辺建物（C 段階の一括）

- 交差点の中心から 250 m 以内で、**自分の資産フォルダを持たない建物すべて**（PLATEAU 2025 LOD2、303 棟＋駅側 5 棟）と橋・高架 7 件。
- C 段階の定義（`docs/core/DECISIONS.md`）：PLATEAU の形と共通の材質。**完成扱いにしない。** A・B 段階の建物を作ったら、その建物はここから外れる。
- 外壁は自作の手続き生成のタイル（1 区画 3.2 m × 1 階 3.6 m）2 種類と、色 4 種類。写真・Street View は使っていない。
- 夜は窓の部分だけ弱く光る（`facade_*_emit.png`、`src/world/context.ts`）。

## 除外
- 自分の資産がある建物：QFRONT（way/136691386）、MAGNET（way/116806281。同じ PLATEAU の立体に栄楽ビルの屋根も入っている）。
- 地下鉄出入口の上屋（街路資産 `assets/street/core` が描く）。
- 新しく A・B の建物を作ったら、`source/tools/select_context.py` の `OWN_ASSETS` に OSM の id を足して作り直す。

## 駅側のグループ
- JR の駅舎など 5 棟は `station` のグループ。**2025 年 10 月（東急東横店の撤去後）の写真で形を確かめるまで仮。**
- `?context=nostation` で隠せる。`?context=off` で全部隠す。

## 再生成
```bash
python3 assets/context/core/source/tools/select_context.py <plateau_core.json> <records_v2.json> \
  docs/core/ASSET_REGISTER_V2.csv assets/street/core/source/data/street_input.json assets/context/core/source/data/context_input.json
python3 assets/context/core/source/tools/make_facades.py assets/context/core/source/textures
cp assets/context/core/source/textures/*_emit.png assets/context/core/web/
$BLENDER -b --python-exit-code 1 -t 2 -P assets/context/core/source/blender/build_context.py -- \
  assets/context/core/source/data/context_input.json assets/context/core/source/textures \
  assets/context/core/web/context_core.glb assets/context/core/source/data/context_stats.json
```
- `plateau_core.json` は `tools/core/plateau_core.py`、`records_v2.json` は `tools/core/build_records_v2.py` の出力（`DEV_ENVIRONMENT.md` の外部データ）。抽出した入力 `context_input.json` はリポジトリに含めた。

## 出典
- 国土交通省 Project PLATEAU「渋谷区 2025 年度 3D 都市モデル」（CityGML、13113_shibuya-ku_pref_2025_citygml_1_op）を加工して作成。

## 未達の点
- 1 階の店舗・看板・屋上の設備がない。外壁のタイルは建物ごとの実際の窓割りではない。
- PLATEAU の建物の地面と C2a の地面は 0.2 m ほど食い違う所がある（U9）。C 段階では PLATEAU の高さのまま置いた。
