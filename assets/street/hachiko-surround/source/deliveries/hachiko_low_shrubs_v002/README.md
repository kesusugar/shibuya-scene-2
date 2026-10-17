# ハチ公周辺：低木のみ品質改善 v002

6株の低木だけを制作し直したコンポーネント候補。大木・既存汎用樹木6本・石・レール・土・照明筐体・配置・歩行表示・FPSコードは変更していません。GitHub登録、マージ、デプロイもこの制作では行っていません。

## 採用ファイル

- `models/hachiko_low_shrubs_only_v002.glb`：統合用の低木のみ。6株、枝1プリミティブ＋葉1プリミティブ。並行制作中の石縁・レールを戻さずに差し替える場合はこちら。
- `models/hachiko_surround_v002.glb`：既存の石縁・レールなどを保持した丸ごと比較用。並行した座面・レールの更新に上書きしないこと。
- `models/hachiko_surround_v002.blend`：同じ形状・マテリアル・パック済みアトラスを含む Blender 4.2.3 制作ファイル。
- `textures/needle_spray_atlas.png`：自作の針葉束4種、1024×1024 RGBA。写真ピクセルを利用していません。
- `source/build_after.py`：再現可能な生成スクリプト。
- `models/shrub_roots.json`：変更していない6株の根元位置。

## 変更内容

放射状の幅広い三角針と表面に露出した球状コアを除去。細く先細りの葉を方向性のある小束として構成し、3区間で曲げた葉束面に自作アルファマスクを使用しました。各株6つの非対称な重なる枝葉群、各群28束。葉先は横向き・下向き・穏やかな上向きを混在させ、球を芯として見せない構造です。樹種の同定ではありません。

実寸に見える細葉と密度を維持するため、最初の全ジオメトリ案（全体48,648三角形）は不採用。最終候補は7,224三角形の低木のみ、全体13,488三角形まで軽量化しました。

## 座標系と並行座面部品との統合

低木GLBはワールド配置済みです。メッシュ頂点だけでなく、各ノードの35度回転と移動にも配置が含まれます。ローカル座標の座面・レール部品の変換済み親へ、そのまま低木を入れないでください。既存surroundと同じワールド資産の親に別の子として置きます。詳細は `MOUNTING.md`。

## 必ず「置換」、追加しない

1. 既存 `hachiko-surround` の `street_surround_branch` と `street_surround_needle` を取り除く。後者には旧球状コアと旧針がまとめて含まれる。ノード名とマテリアルを確認してから実施する。
2. 低木のみGLBを、元のsurroundと同じ読み込み・座標変換経路で取り込む。ワールド配置はすでに含まれる。35度のyawや位置オフセットを再適用しない。
3. 元の石・土・レール・照明筐体を保持する。並行制作の座面・レールを使う場合も、低木のみGLBをその既存座標へ組み合わせる。
4. 既存の大木と汎用樹木は対象ノードではない。変更・複製しない。
5. 丸ごと版と低木のみ版を同時にロードしない。置換後に6株であること、旧トゲ・球が残らないこと、石・レールが重複しないことを確認する。

## コストとマテリアル

- 旧低木：9,264三角形、3プリミティブ（枝・コア/針2色）。
- 新低木：7,224三角形、2プリミティブ。22.02%削減。
- 旧surround全体：15,528三角形、8プリミティブ。
- 新surround全体：13,488三角形、7プリミティブ。13.14%削減。
- 新葉：6,048三角形、1,008の曲面葉束。1プリミティブ。
- アトラス：1024×1024、1枚、GLB内埋め込み。非乗算RGB＋独立アルファ。
- glTF葉材質：`alphaMode: MASK`、規定のcutoff 0.5、`doubleSided: true`。BLENDの深度ソートは用いない。
- 葉束は根元側を狭めて透明領域を抑制。ただし面の重なりによるアルファテスト負荷は残る。実アプリのFPSは未測定。三角形削減だけでFPS改善と断言しない。
- ミップマップ・遠距離・斜め視点で細葉のちらつき/消失がないか、Three.js実装側で確認する。比較画像は静止画であり、時間的ちらつきの検査ではない。

## 再生成

Blender 4.2.3 LTS（検証済みhash 0e22e4fcea03）を使用。

```sh
blender -b -t 4 --python-exit-code 1 -P source/build_before.py
blender -b -t 4 --python-exit-code 1 -P source/build_after.py
python source/validate_assets.py
blender -b -t 4 --python-exit-code 1 -P source/inspect_roundtrip.py
python source/check_glb_winding.py models/hachiko_low_shrubs_only_v002.glb
blender -b -t 6 --python-exit-code 1 -P source/render_comparisons.py
```

アトラス自体を再生成する場合のみ、Python＋Pillowで `python source/create_needle_atlas.py`。通常のBlender再生成は同梱PNGを使うため追加Python依存なし。

出力先を変える場合：`blender -b -P source/build_after.py -- /absolute/output/path`。同じ入力による2つのGLBのバイト一致を確認済み。`.blend`の保存メタデータのバイト一致は保証対象外。

## 検証の範囲

ベースラインはpinned sourceと記録済み接地点から再生成したもので、元のGLBバイナリを取得したものではありません。元のGLBのGitHubバイナリ取得は非対応だったため、地面GLBを近似する代わりに、元生成時の接地標高27点をそのまま使用しました。地面そのものは再制作・変更していません。

`validation/asset_validation.json`で非植生5グループの位置・形状・材質データがbefore/afterで一致、6つの根元位置が一致することを確認。`validation/roundtrip.json`はGLBを新規シーンへ再読み込みして三角形・境界・埋め込み画像を確認した結果です。`validation/regeneration.json`は別出力先へのクリーン再生成のハッシュ一致です。

`evidence/*_close.png` / `*_context.png`は同一カメラ・同一照明で比較するコンポーネント画像です。contextは左右のsurround全体であり、アプリ全景ではありません。中立の床はプレビュー専用でモデルへ含まれていません。像・大木・汎用樹木は制作ファイルに含めていません。実ゲームの表示、歩行、影、LOD、FPSは別途統合確認が必要です。
