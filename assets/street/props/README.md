# 街路の小物（外部で生成したモデルの取り込み口）

自動販売機・車止め・ごみ箱・交番などの小物を、外部のツール（ChatGPT の dots など）で生成したモデルから取り込むための場所です。2026-10-14 時点で置いた小物は **0 件**（仕組みだけ）。

## 流れ
1. **モデルを置く。** 受け取ったファイル（GLB・FBX・OBJ。テクスチャがあれば同じフォルダ）を `incoming/<id>/` に置く。
2. **仕様を書く。** `source/data/specs/<id>.json` に、実物の寸法・三角形の上限・材質の区分・出典を書く（例は `_selftest_vending.json`）。
   - 寸法は日本の標準値、または写真から読んだ値。根拠も書く。
   - `source` には生成ツール・作成者・日付・利用条件を必ず書く。利用条件がわからないものは取り込まない。
3. **取り込む。**
   ```bash
   $BLENDER -b --python-exit-code 1 -P tools/props/import_prop.py -- \
     assets/street/props/source/data/specs/<id>.json assets/street/props/incoming/<id>/<file> \
     assets/street/props/web/<id>.glb assets/street/props/source/data/reports/<id>.json
   ```
   - 足元を原点にし、高さ（なければ一番大きい寸法）に合わせて**縦横同じ倍率で**縮尺を直す。
   - 他の寸法が目標と 15 % 以上違うと警告を出す。その場合は引き伸ばさずに、生成し直す。
   - 三角形が上限を超えたら減らし、遠景用の簡易版（`<id>_lod1`）も作る。
   - 材質名を `prop_<区分>_<n>` に変え、場面の共通の見た目（`look.ts`）が効くようにする。
4. **配置する。** `web/layout.json` の `props` にファイルを登録し、`placements` に平面の座標・向き・根拠を書く。
   - 高さは読み込み時に歩ける面から取る。地面がない場所の小物は置かない。
   - 同じ種類の小物は 1 回の描画でまとめて描く（`src/world/props.ts`）。
5. **確認する。** 同じカメラの前後の画像、`npm test`、予算を確認する。台帳（`ASSET_REGISTER_V2.csv`）にも記録する。

## 生成を頼むときの書き方（例）
- 「日本の歩道にある飲料の自動販売機。高さ 1.83 m・幅 1.0 m・奥行 0.75 m。企業ロゴなし。GLB、テクスチャ付き、三角形 5,000 以下」
- 実在の企業ロゴ・商標は入れない（架空のものか無地）。
- 1 ファイルに小物 1 つ。

## 自己テスト
`tools/props/make_fixture.py` で、わざと崩した試験用モデルを作る（センチ単位、原点から離れている、部品 3 つ、重い球）。それを取り込み、寸法・三角形・材質名が直ることを確かめた（`evidence/look-foundation/prop_selftest.json`）。試験用モデルは配置しない。
