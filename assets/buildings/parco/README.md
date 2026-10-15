# 渋谷PARCO：既存モデルの累積外装・テラス更新

main dc760eb6 の既存PARCO（340,788 bytes）から、完成済みの低層外装、source108/152の三角形接続、roof22、奥行きのあるテラスを一建物だけで反映するレビュー用パッケージです。新しい建物の追加ではありません。新規造形は行わず、配送済み最終GLBをそのまま使用します。

実行用は web/parco.glb、現行編集用は source/terrace-v1/parco_terrace_candidate.blend。Blender 4.2.3、Python 3、NumPy、Pillowが必要です。資産フォルダの作業コピーで python source/blender/build.py --blender /path/to/blender を実行すると、低層→屋根→テラスの全段階を再生成し、各中間GLBの完全一致を確認して現行GLBへ同期します。

source/roof-repair-v1/prior.blend は屋根修正器が使う編集可能な先行シーンです。source/terrace-v1/inputs の不変中間入力は再生成結果とバイト一致を検証します。旧マニフェストは履歴であり、そこに記載された古い配送画像などを現行パッケージの依存にしません。

元のPLATEAU座標・足元・T.P.15m基準を保持。現在のポリゴン数12,085、プリミティブ19、719,392 bytes、非縮退三角形10,036。既存B予算を変更しません。元の8材質・ノード、修正対象外属性と接続、上部タワー、source84/141の実在ノッチ、roof47を検証します。対象屋根22と低層source108/152/171のみ修正。床は4F/5F等の高さを分けています。

絶対1F標高、階段接続・室内・ガラス光学特性・一部不透明仕上げは未確定。東側3F–4Fエスカレーター下部開口は未再現。測量・構造・衝突・歩行可否・全景ブラウザ・FPSは未認定です。QFRONT、西武、他建物、歩行表示、FPS設定の変更はありません。マージ・デプロイはしません。

写真はSyced撮影2024-03-04、CC0の恒久外装参考です。2025年10月の店舗・広告の証明ではありません。図面はURLと数値解釈のみ、無許諾の図面・写真画素を同梱しません。詳しい出典、寸法、不確実性は source/terrace-v1/README_JA.md、docs/SOURCES.md、references/PHOTO_SOURCE.json。PLATEAU/OSMの原プロジェクトの条件を継承し、全体の一律再ライセンスは行いません。

現行の対応検証は tests/parco-podium.test.ts、tests/parco-terrace.test.ts。前者は不変の中間ステージに対する幾何・寸法検査であり、後者は現行GLBの切欠き・床・庇裏・側壁・対象外保持・材質・故障注入を検査します。過去配送時の170件やビルド成功は今回の実行結果と混同しません。
