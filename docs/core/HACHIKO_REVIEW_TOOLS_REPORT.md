# PR #76レビュー指摘の追補修正

基準：PR #76マージ済みの最新main `75903c8`。専用worktree、別ブランチ `codex/hachiko-review-tools-20261016`。マージ・デプロイ・追加素材配置は行わない。

## 1. 旧部位ノードに依存する2本の検証

`check-hachiko-shape.mjs` は旧自作台座の投影縦横比、`check-surround-shape.mjs` は周辺植栽・レールと旧自作犬の高さ比を測る履歴検証である。現在の一体型スキャン全体を台座／犬と見なす名前置換は行わず、両方のハチ公入力を `assets/street/hachiko/source/legacy/hachiko.glb` へ明示した。

- legacy SHA-256を実行時検査し、対象部位のmeshがなければ用途が分かるエラーを返す。
- legacyは配置を焼き込んだワールド座標なのでnodeのworld matrixだけを使い、現行スキャンの配置行列・縮尺を再適用しない。
- 出力に旧モデル専用のscope、実入力パス・SHA、座標系、`current_scan_evaluated:false` を記録。周辺GLBのパスとSHAも残す。
- 出力先を第1引数で指定でき、親フォルダを作成する。引数なしの既存出力先は維持する。
- 現行スキャンの接地／周辺チェックには既存の `measure-hachiko-scan.mjs` と `check-hachiko-scan-surround.mjs` がある。この2本の旧比率を現行スキャンの精度判定と呼ばない。

実行済み：

```sh
node scripts/check-hachiko-shape.mjs evidence/hachiko-review-tools/legacy-statue-shape.json
node scripts/check-surround-shape.mjs evidence/hachiko-review-tools/legacy-surround-shape.json
```

台座の投影比0.7189116580は従来の台座検証値と一致。旧犬のワールドY範囲は1.8622074574〜2.8499508500m（犬だけの高さ約0.987743m）。現在の周辺GLBに対する比率0.9269134301を記録した。古い周辺shape-checkの保存値は別の過去モデル／植栽版の結果であり、一致を強制したり履歴ファイルを上書きしたりしていない。いずれも未校正写真との粗い指標で、物理精度・現行スキャン・現況の合格スコアではない。

2件の回帰テストは実際に両スクリプトを子プロセスで実行し、legacy部位の数値・scopeと配信GLBの不変を確認する。

## 2. 部分コピーに合わせた再生成README

`scan-candidate/README.md` を、実在する正本GLB・変換・検証JSON・出典・納品目録だけの部分コピーとして書き直した。配信用GLBと候補正本の再生成を分離した。

- **リポジトリ単体**：Python＋Pillow12.3.0、`source/tools/build_scan_runtime.py`（リポジトリルートからの完全パスを記載）。実行し、配信GLB 2,911,696 bytes、SHA-256 `0d68077edad1fc24858cdb9c42001439488728fc2e4779676ee3f0e3e821077e` が変更前と一致した。
- **Drive完全版**：ZIPのURL・サイズ・ハッシュ・別フォルダ展開・入力原本／trim face IDsの照合を記載。完全版パッケージ内のbuild、任意のBlender4.2.3再取込／BLEND生成を説明。この工程は今回は再実行していない。
- 任意の比較は別のローカル統合v001 GLBが必要。リポジトリの旧world配置legacyとは別物で、無条件に代用しない。比較PNGには両レンダー・Pillow・指定フォントが必要。旧比較入力なしで比較画像まで生成できるとは書かない。
- 元の `scan-candidate/manifest.json` は完全納品の履歴目録として保持。改訂READMEの現在のSHAは資産ルートmanifestへ別途記録し、古い納品READMEハッシュとの一致を偽らない。

## 3. 取り込み計画

`HACHIKO_ASSET_INTAKE_PLAN.md` に、実取得した2026-10-16 12:20 JSTの現行39件を全件分類した。BOX19／駅前外観7／小物・舗装5／採用済みスキャンと代替群8。件数は物体数ではない。BOX組立に内包する元部品7件を重複除外し、TKTS看板・縦画面だけを部分選択する。旧版6件・不採用HOLD・比較レビュー・受渡し資料・原本を配置対象から外す。BOX外形→表示→任意内装、駅前は一施設ずつ、小物・舗装は局所の順に別PRで進める計画。今回は計画のみ。

## 検証と変更範囲

- 上記2本を実行し、結果JSONを収録。
- 配信用GLBをREADMEの手順で実際に再生成し、バイト一致を確認。
- 新規2件＋既存ハチ公4件のテストは全6件合格。
- ローカル全体では51ファイル／229件中228件合格。変更外のHikarie day/night/day保持テスト1件が5秒制限で時間切れ（1・2ワーカーとも）。対象外コードや時間上限は変更せず、従来worktreeでも同テストを単独実行して全4件合格を確認。新規PRのLinux CIでも全体テストを確認する。
- `npm run build` 合格。ランタイムの出力JSは変更前と同じ `index-Bl1Es5-n.js`。
- `src/`、GLB、地面、QFRONT、西武、歩行表示、FPS、予算は変更なし。表示が同一なので新しい実シーン撮影はせず、PR #76の既存画像を表示変更なしの参照とする。
