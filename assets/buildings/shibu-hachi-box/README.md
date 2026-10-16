# SHIBU HACHI BOX — BOX-1配信派生物

建物外形と前テラス1件を通常表示するB建物。採用範囲・推定・地面・画像・検査結果は[BOX-1報告](../../../docs/core/BOX_1_REPORT.md)参照。地下、入室可能な内部、看板・時計等の第2段階以降は追加していない。元のincomingは変更しない。

## リポジトリだけで配信用GLBを再生成

Blender **4.2.3 LTS**、リポジトリルートから：

```sh
blender -b --python-exit-code 1 -t 4 -P assets/buildings/shibu-hachi-box/source/build.py
node scripts/check-box-1.mjs
npx vitest run tests/shibu-hachi-box.test.ts tests/budget.test.ts --maxWorkers=2
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
