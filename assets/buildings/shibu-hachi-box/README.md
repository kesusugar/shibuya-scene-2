# SHIBU HACHI BOX — BOX-1本体とBOX-2外部表示

建物外形・前テラス1件と年代付き外部表示を通常表示するB建物。採用範囲・推定・地面・画像・検査結果は[BOX-1報告](../../../docs/core/BOX_1_REPORT.md)参照。地下・入室可能な内部は追加しない。第2段階の採用・推定・制約は[BOX-2報告](../../../docs/core/BOX_2_REPORT.md)。元のincomingは変更しない。

## リポジトリだけで配信用GLBを再生成

Blender **4.2.3 LTS**、リポジトリルートから：

```sh
blender -b --python-exit-code 1 -t 4 -P assets/buildings/shibu-hachi-box/source/build.py
node scripts/build-box-exterior.mjs
node scripts/check-box-1.mjs
npx vitest run tests/shibu-hachi-box.test.ts tests/box-exterior.test.ts tests/box-sign-look.test.ts tests/buildings.test.ts tests/budget.test.ts --maxWorkers=2
npm run build
```

入力は既存 `assets/street/props/incoming/shibu_hachi_box_architecture_reference/output/shibu_hachi_box.blend`、同梱済み `source/terrace-v001/shibu_hachi_front_terrace_candidate_v001.glb`、Core地面、`evidence/box-1/box-position-source.json`。ネットワーク・調査写真・比較一式・追加内装は不要。元シェルとテラスのハッシュを固定し、名前付き部位だけを選択加工する。上書き先はこの派生物の `web/` と `source/placement-and-build.json`。ビルド前後に撮影を完了させ、撮影中に生成・syncしない。

世界変換をGLBへ一度だけ適用済み。viewerはT.P.15m基準で追加オフセットなし。非均等拡縮なし。元の主床版・背面壁は保全し、外周の見える地面接続だけ推定スカートを追加した。スカートは基礎の実測形状ではなく、歩行面でもない。

## テラス候補自体の再生成は完全版が必要

`source/terrace-v001/` は**選択した入力・出典のスナップショット**。元のREADME、ASSUMPTIONS、PROVENANCE、manifest、placement_reference、DejaVu通知と最終GLBだけを収録。元manifestの44ファイルを全てここに収録したという意味ではない。元READMEの `source/generate.py` 手順をこの部分スナップショットだけでは実行できない。

候補そのものを再生成・編集する場合は[Drive完全版](https://drive.google.com/file/d/14ihhOgW-ANqAwyeNkX9XDUCEb0W8UloU/view)のZIP（5,299,103 bytes、SHA-256 `6e5c096b78341a855142a253be6363ec196e1605b94cdbe352c5cb42e9e25ea4`）を検証して用いる。そこにはBLEND・入力9GLB・生成コード・検証記録がある。今回の配信用再生成に完全版は不要。

## 出典・権利・制約

- 建築寸法・外形：既存incomingの[SOURCES](../../street/props/incoming/shibu_hachi_box_architecture_reference/SOURCES.md)。運営者の2024図面、2024/2026外観観察。元の出典・推定寸法を引き継ぐ。背面の閉鎖形状・屋根高・材質等は推定。
- 位置・向き：OpenStreetMap way1315939856 version5、© OpenStreetMap contributors / ODbL-1.0。測量値ではなく、2025年10月の確定現況でもない。
- テラス：`source/terrace-v001/PROVENANCE.md` と `ASSUMPTIONS.md` を保持。2024年公開CASIO記事由来のメッシュ図柄で、公式ブランド原稿ではない。写真・PDF・ロゴ等に新たな権利を付与しない。DejaVu通知は同ディレクトリの `references/DejaVu_LICENSE.txt`。
- 今回の加工：対応旧床5成分の局所切断、対応旧柵・化粧帯等の選択除去、単独テラスの剛体変換、地面合わせと外周スカート、材質別バッチ化。候補の図柄・構造の形と寸法は変更していない。元の盾修復・時計図形の意図した枠内隠れは上流の記録を保持。
- 18mmの水平接合差、226mmの残存帯、傾斜背後の最大約312mm差、可視R3以降の未確定端部を隠れた完成形としない。地形と候補傾斜の相違により水平部は最大約476mm地面より高い。バリアフリーや入室動線の認証ではない。

公開物は作成した形状・コード・数値・モデル画像のみ。調査写真・秘密情報を含まない。比較用 `pavilion_building_terrace_fit_v001` の統合GLBや内装は採用していない。

## BOX-2の表示レイヤーだけを再生成

```sh
node scripts/build-box-exterior.mjs
```

通常の外部表示再生成にBlenderやDriveの再取得は不要。承認済み本体GLB・配置記録を読み、`source/exterior-signs/placement.json` の局所変換を一度だけ合成する。本体GLBを固定ハッシュで検査し、屋根・床・接地・スカートを生成し直さない。`viewer.json` に6つの年代付きレイヤーを登録し、manifestを更新する。本体の旧Blender手順を別途実行した場合も、その後に上記コマンドを実行してレイヤー登録を復元する。本体ハッシュが変わった場合は自動で許容せず、別の変更として確認する。

`source/exterior-signs/` は対象4完全ZIPから選択したGLB・README・PROVENANCE・元manifest・配置資料・フォント通知と、既存名の抽出GLB。元manifestが列挙する全ファイルを収録したものではない。単体候補を再生成する場合は `evidence/box-2/intake.json` のDrive完全版とハッシュを用いる。配信レイヤーの再生成はリポジトリの選択入力だけで可能。

既存名称の正規化GLB自体を再抽出する場合だけ、Blender4.2.3で `scripts/export-box-name.py` を実行する。元incomingの文字だけを抽出し、旧高キャリアを戻さない。名前の等方1.201倍と淡色発光は今回の配信上の推定。時計は元の静止文字盤・全形状・法線を維持し、テクスチャ未使用の4プリミティブのUVだけを除去する。

丸i・犬・名称・FUN・スポンサーは2024年公開資料由来、時計のLCDは2026-08-08 08:08:08。2025年10月の確定風景ではない。既存窓枠が時計文字盤の一部を遮る。全文字の常時視認や取付金物の実物形状は保証しない。時計のフォント通知は `source/exterior-signs/shibu_hachi_gshock_display_clock_v001/fonts/LICENSE.txt`、スポンサーは同名パッケージの `fonts/LICENSE.txt`。調査写真・PDF・認証情報を含めない。

## BOX-2の表示レイヤー名

`source/exterior-signs/placement.json` の6つの `layer` は `signs_` で始める。
共通loaderは親名を `shibu-hachi-box:<layer>` にし、通常の `applyLook` と分類表示は
既存の `/:signs/` 規則で看板を識別する。生成済みviewer.jsonだけを書き換えない。
`node scripts/build-box-exterior.mjs` でviewer設定とmanifestを更新する。
この名前修正では本体・6表示GLBの内容、材質、形状、配置、予算を変更していない。
