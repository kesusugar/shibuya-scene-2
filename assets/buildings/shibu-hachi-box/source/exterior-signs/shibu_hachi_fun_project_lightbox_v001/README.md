# SHIBUYA FUN PROJECT lightbox v001

台帳 H-SG-003 / A14 BOX案内表示の小型ライトボックスを、2024年公開のCASIO正面写真に基づいて独立部品として制作しました。既存の屋上「SHIBU HACHI BOX」と中央の「Tourist Information & Souvenir Store」は別の表示で、この部品は既存生成元に含まれていません。

## 内容と制約
- GLB: 3マテリアル / 3メッシュ / 3プリミティブ。静的部品で、写真テクスチャは使っていません。
- Blender 4.2.3 LTS: ケース・発光面・3語・FUN外枠の6個の編集可能なメッシュ。文字はメッシュ、文言と寸法は同梱のPythonで変更できます。
- 推定外寸: 幅1.150 m × 奥行0.1056 m × 高さ0.205 m。実測値ではありません。
- 原点: 全部品を含む底面中心。BlenderはZ-up、正面-Y。glTFはY-up、正面+Z。
- 読める文言は「SHIBUYA FUN PROJECT」。FUN直前の小さなマークと外枠の微細な形は解読できないため省略しました。字体・線幅は独自の近似で、ロゴの完全再現ではありません。
- ケース奥行・背面・取付方法・色・発光の強さは推定。背面は未観察のため無地で、架空のボルトや配線を追加していません。
- 参考記事の公開日は2024-12-10。写真撮影日は不明、現在も同じ表示があるかは未確認です。

## 収録
- shibu_hachi_fun_project_lightbox_v001.glb
- shibu_hachi_fun_project_lightbox_v001.blend
- source/generate.py: 外部フォント・画像・ネット接続不要の生成元
- source/validate.py: 凍結したblend/GLBの再読込・構造検証
- evidence/01_front.png, 02_oblique.png, 03_estimated_back.png
- source_reference.json, PROVENANCE.md, placement_hint.json
- evidence/validation.json, timings.json, 生成・検証ログ
- manifest.json: 各ファイルのSHA-256

## 再生成
Blender 4.2.3 LTSで実行します。ここで利用した実行ファイルは tools/blender-4.2.3-linux-x64/blender です。

    blender -b --python source/generate.py -- --output /path/to/output

画像が不要なら --no-render を付けます。クリーンな別出力先に同じ生成元を実行し、GLBのバイト一致を検証しています。

## 統合担当への注意
未配置です。既存シーンは変更していません。placement_hint.json に右側正面ベイ上という観察位置と親ローカルXの大まかな目安だけを記載しました。親モデルの開口上端・軒天高さとの整合は未検証のため、取付Y/Z・完全な親変換・ワールド変換はnullです。位置の自動適用や旧表示の自動置換はしないでください。

QFRONT・西武渋谷・歩行表示・FPSの変更、GitHub登録、PR、マージ、デプロイは行っていません。このZIPは非公開Drive保存のための単体納品物です。表示の現存確認と配置・接地・干渉確認は別作業です。
