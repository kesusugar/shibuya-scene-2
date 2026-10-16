# ハチ公スキャン候補の実シーン配置レビュー（2026-10-16）

## 結果と段階
- 受け渡し：完了。Google Drive MCP fetch（download_raw_file=true, include_base64=false）の取得応答と、CLI環境への実ファイル保存を別々に確認。
- 配置・検証：完了。main e1124dd1b5412d1cd4140d4272ebaf86ea7ca79eから専用worktree/ブランチで候補1体のみを通常表示。像・台座一体のスキャンで旧像/旧台座はロードしない。
- PR：レビュー提出対象。マージ・デプロイは実施しない。忠実度・実測精度・FPS合格の認定ではない。

## 受け渡しの実測検証
ZIP 28,660,411 bytes。
SHA-256: 7982eff7ba6346c03d12d27d062305e321add19245c1a65a4d3fbd35b328328e
全30ファイルのCRC合格。展開先外パス、Windowsドライブ指定、symlinkなし。manifest記載29ファイルのサイズとSHA-256が全一致。GLB/BLEND実収録も照合済み。
取得参照はMCPのtop-level file_uriを使い、認証情報・署名付きURLを公開資料へ含めていない。Drive共有変更なし。
公開に必要な正本GLB・出典・変換資料だけsource/scan-candidateに保存。完全ZIPとBLENDはCLIの一時フォルダに残し、公開しない。

## 配置の根拠と可逆性
既存 source/data/layout.json のOSM由来位置を維持：東11.5681755213m、北-48.6857322001m。既存推定yaw35度をglTF +Y軸回転として一度だけ適用。候補は+Y上/-Z正面で全体の推定縮尺が焼き込み済み。runtime scaleは(1,1,1)、非均等スケール・傾き変更なし。
実際の既存 sidewalk GLBへ下端371頂点をraycast。最も浅い点が1mm埋まる剛体高さにし、底原点はブラウザY=0.3795121889m（T.P.15.3795121889m）。最大埋まり0.0862435m。元の下端が約5.8cm不整形で傾斜地面でもあるため、地面への完全な面一致ではない。下面を閉じたり形状を平坦化していない。
source/data/scan-placement.json に順逆行列と全点を記録。元スキャン→候補の順逆行列はsource/scan-candidate/model/transform.json。旧GLB・README・manifestはsource/legacyに保全し、通常配信しない。実装/資産コミットのrevertで以前の読み込みへ復帰できる。

## 実シーン確認
既存 capture-street-fix.mjs と固定ビルドで、statue_front / statue_side / paving_close / surround_back / entryの同一5カメラを前後撮影。全10撮影でfailed空、HTTP/JS/consoleエラー0、地面/街路/周辺ロード成功。
旧像は15メッシュ・50,502三角形、新候補は1メッシュ・85,934三角形。二重表示なし。
比較画像：evidence/hachiko-scan-placement/*_comparison.png。
周辺の実GLB（石囲い・植栽・レール・点字・3小物・通常/投影street・広場施設）を候補ローカル外接範囲へ変換し、範囲外のことを確認。支持地面/敷石は意図した接地のため除外。一般の衝突判定機構を追加・認定したわけではない。
QFRONT・西武・歩行処理・FPS関連コード/予算の変更なし。初期表示の広い視点も前後記録。

## 表示用派生物と権利
Hachikō by Maurice Svay。
Source: https://sketchfab.com/3d-models/hachiko-fffee43c3cbc4b7ea20d6556a360b25f
CC BY 4.0: https://creativecommons.org/licenses/by/4.0/
納品加工の通知をsource/scan-candidate/PROVENANCE.mdへそのまま保全し、配信web/PROVENANCE.mdにも出典と追加加工通知を同梱。画面にも作者・ライセンス・推定を表示。
納品正本GLB SHA-256: cd20601d57308a1b50892c05d509a6295ca24ca2045cfd37421995a840bf039e。
表示用だけJPEGを4096角→1536角へLanczos縮小し、quality80/4:2:0へ再圧縮。材質名を既存furniture分類用に変更。幾何・索引・UV・法線・材質値は保全をテスト済み。
表示用GLBは2,911,696 bytes（既存B予算3MB内）、1描画プリミティブ、85,934三角形。予算上限は変更なし。元の4096角JPEGは正本GLB内へ保持。縮小により見た目の細部解像度は低下する。

## 制約
全高2.40559m・幅1.07063m・奥行1.66449mは旧設計全高へ合わせた推定で実測ではない。yawと位置も現地測量ではない。公開2016年・撮影日未確定で、2025年10月/2026年現況を認定しない。
元スキャンの写真陰影、葉、ハイライト、細部の軟らかさ、小さい像の開口、1非多様体辺、開いた下面を保持。metallic0.25/roughness0.2は石も含む一材質の継承で物理校正ではない。調査写真・秘密情報は追加していない。FPS測定・マージ・デプロイは未実施。

## 検証
- npm test -- --maxWorkers=2（CIと同条件）：50 files / 227 tests 全合格、48.36秒。逐次実行でも全合格。既存の資産別・全体予算を含む。
- npm run build：型検査・Vite build合格。
- Windowsでは初回全体テストがpython3未設定・CRLFによる既存ソースハッシュ差・並列資源競合によるタイムアウトで失敗した。未変更ファイルをGit保存時のLFバイトに復元し、Python3.14.4/Pillow12.3.0/NumPy2.5.4/Shapely2.2.0とpython3別名を用意し逐次実行で解決。テスト条件や性能予算は緩めていない。
- 詳細：evidence/hachiko-scan-placement/handoff-validation.json、surround-clearance.json、before/after/capture_log.json、validation-results.json。

CIで最初のバイト保全テストだけが5秒に達したため、大配列の再帰比較をBuffer.equalsによる全バイト比較へ変更。判定内容も時間上限も維持し、CIと同じ2ワーカーで全227件を確認。表示用バンドル・資産・撮影結果は不変。
