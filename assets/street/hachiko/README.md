# ハチ公スキャン候補のレビュー配置

PR88後：GLBと平面アンカーを維持し、像rootだけyaw−65°へ推定調整、371点の接地を再測定。現行値は `source/data/scan-placement.json` と `src/world/hachiko.ts`。設備用 `source/data/layout.json` の35°は周辺設備・履歴生成用であり、像へ再適用しない。[実描画・推定根拠](../../../docs/core/HACHIKO_FINAL_FIT_20261017.md)。下記の旧配置記録より現行JSONを優先。
通常表示は Maurice Svay の Hachikō スキャン由来の候補1体です。像・青銅座・石台座・下段タイルが一体で、旧像・旧台座を追加表示しません。マージ・デプロイは未実施です。

## 出典と加工
Hachikō by Maurice Svay — https://sketchfab.com/mauricesvay
元モデル: https://sketchfab.com/3d-models/hachiko-fffee43c3cbc4b7ea20d6556a360b25f
CC BY 4.0: https://creativecommons.org/licenses/by/4.0/
加工の詳細と権利通知: source/scan-candidate/PROVENANCE.md。配布時も保持します。

納品側の加工は、余分な周囲舗装の除去、不要属性の整理、全体の一様な推定縮尺・向き・底中心原点への変換です。形状の彫り直し、穴埋め、UV変更は行っていません。本取り込みでは表示用JPEGを4096角から1536角へLanczos縮小、JPEG quality 80／4:2:0へ再圧縮しました。材質名を既存の街路設備分類に合わせました。形状・索引・UV・法線の値と材質パラメータは納品候補から不変です。

## 保全と再生成
- source/scan-candidate/model/hachiko_uploaded_scan_candidate_v001.glb: 納品正本をバイト一致で保全。
- source/scan-candidate/manifest.json: 完全な納品ZIPの目録です。このフォルダは公開に必要なモデル・資料のみの部分コピーで、全納品ファイルを含みません。全29ハッシュ照合は evidence/hachiko-scan-placement/handoff-validation.json。
- source/legacy/: main e1124dd の旧GLB・README・manifestをバイト一致で保全。通常配信しません。旧自作モデルの出典・ライセンスは旧資料のままです。
- web/hachiko.glb: 既存3MB予算内の表示用派生物。ブランチのコミットをrevertすれば元の配信資産と読み込みへ復元できます。
- source/data/scan-placement.json: 地面371点の測定、剛体配置と逆行列。
- source/scan-candidate/model/transform.json: 元スキャンと納品候補の順逆変換。縮尺はすでに焼き込み済みで再適用しません。

Python 3 / Pillow 12.3.0で表示用GLBを再生成:
    python assets/street/hachiko/source/tools/build_scan_runtime.py

地面を再測定:
    node scripts/measure-hachiko-scan.mjs assets/street/hachiko/source/scan-candidate/model/hachiko_uploaded_scan_candidate_v001.glb placement.json

配置は src/world/hachiko.ts の単一ルートで行います。東11.5681755m、北-48.6857322m、既存の推定yaw35度、底原点のT.P.15.3795122m。glTFは+Y上／-Z正面。追加の非均等スケール・傾き補正・形状加工はありません。既存地面と歩行面は変更しません。hachiko=off と hachikourl=missing の既存比較・障害経路も保持します。

## 制約
全高2.40559m、幅1.07063m、奥行1.66449mは推定縮尺の出力で実測ではありません。旧全高へ合わせた縮尺で、2025年10月の現況を保証しません。公開は2016年で撮影日は未確定。写真由来の陰影・葉・ハイライト、軟らかい細部、小さい像の穴、非多様体辺、開いた下面を保持しています。金属0.25／粗さ0.2は石も含めた元スキャンの一材質で、物理校正値ではありません。

下端は約5.8cm不整形で、地面371点に対して1mm〜約8.6cm埋めて浮きを避けています。実測接地や構造・衝突・FPSの合格認定ではありません。画像縮小で細部の解像度は低下します。調査写真、認証情報、署名付きURLは追加しません。
