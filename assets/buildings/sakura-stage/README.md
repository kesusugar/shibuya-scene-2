# Sakura Stage SHIBUYA Tower: 北143・東113の納品済み修正版

既存B段階モデルの限定外装修正。新規建物ではありません。北143の旧格子・合成X表示を、40ベイ、41本の連続フィン、階間帯、細い分節暗色帯、2本の強い水平帯に置換。東113は上部4個の合成X表示（16三角形）だけを除去し、下部4個は未解決のまま保持。南側屋根の斜材は対象外。

PLATEAU bldg_9442d303-7a48-4f81-aa67-b6ef05dbd43b / OSM way/1200029947。全体を原点へ移さず、1単位=1m、Blender Z=T.P.−15m、GLB Y=T.P.−15mを維持。原屋根・外殻・足元・元306舗装サンプル・対象外の頂点属性と三角形順序を保持。8個の元のゼロ面積外壁三角形は残り、新規縮退はありません。

## 写真と推定

北面: 2025-02-08 ウィ貴公子 CC BY-SA 4.0、2025-09-30 かなえゆうじん CC0。review/north143/SOURCES.md と画像を参照。2月写真の切抜き・比較ボードも CC BY-SA 4.0。フィン幅0.13m、突出0.34m、帯高1.05m、水平帯高さ118.5/127.9m等は写真の比率による推定で、測量値ではありません。

東面: 2025-12-01 Syced CC0 のパノラマ。review/north143-east113/SOURCES.md と coverage.json を参照。12月は目標2025年10月より後で、恒久外装を推定する限定的根拠です。10月状態の証明や写真の厳密なカメラ校正はありません。画像を建物テクスチャには使っていません。

元PLATEAU/OSMデータの権利条件は維持し、写真のCC0をモデル全体へ適用しません。既存 source/refs の歴史的2023年資料とそのmanifest記録はリポジトリ上で保持します。無許諾写真、Street View、広告テクスチャは追加しません。

## 再生成・編集

リポジトリルートで Python 3（標準ライブラリのみ）:

    python assets/buildings/sakura-stage/source/blender/build_north143.py /tmp/sakura-north.glb
    python assets/buildings/sakura-stage/source/blender/build.py /tmp/sakura-final.glb
    python tests/sakura-stage-revision.test.py

前者は固定 baseline.glb から北面依存モデルを生成。後者は同梱 accepted-north143.glb から最終モデルを生成。両方とも同梱GLBにバイト一致します。外部地形・他ZIP・ネットワークは不要です。

編集用 source/blender/sakura-stage.blend は Blender 4.2.3 LTS (0e22e4fcea03)。外部画像・ライブラリ依存なし。verify_editable.py は読み取り専用で最終GLBの全ワールド空間三角形と材質割当を比較します。

    blender -b --python-exit-code 1 -P assets/buildings/sakura-stage/source/blender/verify_editable.py
    blender -b --python-exit-code 1 -P assets/buildings/sakura-stage/source/blender/render_main_comparison.py -- /tmp/sakura-renders

render_east_upper.py は旧北面依存→最終モデルの比較と編集シーン再生成用です。after指定ではblendを上書きするため、編集内容を保存したコピーで実行してください。

## 現在値と検証範囲

最終31,834三角形 / 12プリミティブ / 2,783,244 bytes。元36,336 / 8 / 2,234,272からの累積差分。B予算120,000 / 40 / 3,000,000は変更なし。source/data/stats.json は元外殻・地面の由来として保持し、現在値はmanifest.statsとeast113-upper.jsonを使います。

review/main-vs-final は実mainの正確なGLBと最終モデルの同一カメラ・同一照明のnative JPEG。限定geometry回帰、2段階完全再生成、編集ソース一致、現行Sakura屋根/C親重複検証とloader 9件、限定予算2件を実行。無関係テスト11件はスキップ。全街並みbuild/browser、昼夜、実FPSは未検証です。QFRONT・西武・歩行表示・FPS設定の変更なし。マージ・デプロイなし。
