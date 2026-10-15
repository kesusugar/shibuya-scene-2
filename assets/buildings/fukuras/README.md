# 渋谷フクラス: 完成済み上壁・テラスの限定反映

既存建物 way/55588118。main の写真由来ファサードはそのまま保持し、納品済み壁74/76/81・屋根35の三角形分割と外向き法線を反映する。新しい建物やファサード制作ではない。

## 実際の差分

比較元は main 2d1d416d5b4428db7a983e510eeaba08332f707f のGLB (Git blob 954439cc27edeaa65fe76a47c310b8e3bd5875bf)。source/tessellation-v4/main.glb に同一バイトを保存。元の source/data/baseline.glb はファサード制作前の入力であり、今回の比較元ではない。

最終GLBは納品ZIPと同一 (Git blob fa1010e80fdfa8bd854931c0edd24f4ee29cc09d、SHA256 4454c7c1e0c910688d68a879f8c94b1fa02d058641d23dddde6ad5c37e9d6f44)。壁74:10、76:12、81:6、屋根35:14三角形の局所分割を置換。その他12,189三角形の座標と法線、全材質、親子構造、既存ファサード境界を厳密に維持。全12,231三角形・13プリミティブは不変、1,046,328→1,137,516 bytes。B予算は変更なし。

T.P.15基準、source top T.P.120.899、135点の既存接地記録、配置を維持。地面を再計測したという意味ではない。

## 再生成・編集

Blender 4.2.3 LTS (0e22e4fcea03)。資産ディレクトリを作業用コピーにし、任意のカレントディレクトリから実行:

    blender -b -t 2 --python-exit-code 1 -P /absolute/path/assets/buildings/fukuras/source/blender/build.py

同梱 baseline.glb / baseline_stats.json / plateau.json から最終GLBと生成JSONがバイト一致。地面GLBや他棟は不要。生成器はwebと生成JSON・blendを上書きする。source/blender/fukuras.blend は納品済み編集シーンを保全し、最終GLBとの三角形・法線・材質の意味的一致を再検証した。blend保存のバイト決定性は保証しない。

## 検証・画像

npmの通常環境で `npx vitest run tests/fukuras-fidelity.test.ts`。6件成功。元の4件のうち完全な壁インデックス不変という1件だけを局所修復対応に更新し、他3件は本文を変更せず保持。厳密な非対象三角形・法線不変、修復面の境界・面積・辺接続・外向き法線・元頂点一致を追加。元テストもsource/tessellation-v4/に参考保存し、旧mainは4件成功、最終版は意図した1件のみ失敗することを確認した。既存 neighbourhood のFukuras1件も変更せず成功。他5棟は対象外として選択実行していない。

evidence/tessellation-v4/main-before-after.jpg は実mainと最終GLBを同じ平行投影・向き・倍率・照明で並べたBlenderネイティブJPEG。左右への比較用移動だけを描画シーンに適用し、資産座標は変えていない。比較元の屋根/上壁の黒い破綻の解消が対象。最終版にも対象外の上部小面に細い黒い三角が残るため、棟全体の完成を意味しない。画像後加工はない。

## 出典・限界

PLATEAU由来の既存形状とOSM識別子を継承。既存source/refs/SOURCES.mdとFIDELITY_SOURCES.mdの出典・写真ライセンスは変更しない。2025-10-10/11/18の写真、9月30日の補助写真を区別。2020年の写真は構造補助であり2025年広告の証拠にしない。今回新しい写真やテクスチャは追加せず、画像は模型の自作レンダーだけ。SOURCE_NOTES.md参照。

外装の寸法・窓割り・色は写真比率の推定。隠れた面、サービス部、屋上設備、内部、TOKYU PLAZA文字などは未達。全シーンのロード、ブラウザ、build、FPS、衝突・歩行の成功は主張しない。QFRONT・西武・他棟・歩行・FPS・実行時設定に変更なし。
