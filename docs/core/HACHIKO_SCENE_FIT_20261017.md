# ハチ公周辺の実配置・比較修正（PR #85 後）

基準は最新main `73a5fe1`（PR #85マージ済み）。新ブランチ `codex/hachiko-scene-fit-20261017` で作業した。検証済みローカルZIPを再利用し、Drive取得・全CRC/manifest検証を繰り返していない。QFRONT・西武の資産、歩行表示・FPSの処理、採用済み像・台座・石碑、BOX、JR入口、交番は保持。地面や道路網の高さは変更していない。

## 実装した表示と切替

| 対象 | 最終状態 | 推定調整と残る差 |
| --- | --- | --- |
| 宝くじ売場 v002 | **通常配置、正面の部分置換** | 既存OSM小施設 `way/858994297` の長辺と、同所に残るPLATEAU `bldg_a4e27670-5674-4902-bbd5-51c0f5084ee9` の正面を基準に3窓を配置。公式地図点とOSM外周の3.17m差は位置精度の不確実さとして残す。初回はC段階外壁に隠れたため北へ0.70m移し、2本脚の接地点で上下を調整した。施設割当て・前後寸法・正面線は推定。既存小施設の北側の浅い帯だけを差し替え、南側、喫煙設備、C段階の後方外壁は維持。v001は追加していない。 |
| 大木・石囲い | **大木を維持、見える側の囲いを通常配置** | 幹 `(7.4,-45.5)` を共通基準に、写真の直線石壁と傾いた笠石を4.6mの一辺＋0.72mの短い返しとして制作。幹から像側へ0.95m、回転35°、壁厚0.24m・高さ0.50m・笠石上端0.605mは推定。各部分を現行地面に接地。既存の像両脇の石縁・植栽、他の6樹木は置換しない。**背面の全周形・分岐・実寸は保留**で、閉じた全周囲いの完成とは扱わない。 |
| 像周辺の舗装 | **通常配置、既存局所面の材質置換** | 写真で見える小さな灰色の扇形敷石に合わせ、約0.10mの割付け・目地約4mmの連続した独自アトラスを作成。既存 `plaza-finish` の境界・全頂点位置・標高をそのまま使い、元の見える面と切り替える。非シームレスな90°試片を並べていない。扇中心・各石の形と寸法は推定。範囲外の赤褐色舗装や道路は維持。 |
| A8入口 | **確認用仮配置** | 公式図の像→BOX→A8→JRの関係と既存南辺を基準に、`plaza-kiosk` の南側の一部分だけを5.8m幅シェルへ差し替える案。丸柱・庇・開口を接地し、北側屋根・側面の残りを保持。画像上の支柱の浮きはないが、既存約167m²の屋根とシェルの幅・高さ、北側との接合には差が残る。施設の分割境界と南側開口の正確な位置は推定なので通常採用にはしない。地下・階段奥・室内機能は追加していない。 |
| 駅ルーバー | **確認用仮配置** | 14面のうち広場側を向く `stn_louvre_01` に限定し、2×4ベイを均等0.6倍、幅10.056m・高さ2.118m、面法線に沿って0.20m前へ配置。法線・幅は既存面から取得。画像では12.12m高の既存外壁に対して設備が中段に見え、写真のデッキ・白囲いとの上下関係を確定できない。設備の支持高さと施設対応が残る。原面と共用鋼材は背後に保持し、別の13面・西高架・station-serviceへ広げない。 |
| 白い柵 | **確認用仮配置、1区間** | 既存の道路側レールの支柱2本間、長さ約1.885mに合わせた広幅上梁の案。初回の0.57m切片では端・支持が成立しないことを画像で確認し、反復や一様な引き伸ばしをせず1区間の推定形状を作った。既存支柱位置・接地・下側の柵と当たり判定は維持。写真の白い部材とこの設置線が同一か、断面・端金具・全景の関係が未確認で、通常採用にはしない。 |
| A8前の誘導ブロック | **確認用仮配置、2.7mだけ** | 仮配置した開口の法線8.3°へ線を合わせ、入口側を0.6m角の警告面に修正。地面に沿う短い接近線で、広場の既存ネットワークへ接続済みとは扱わない。`NOT_LOCAL` 素材を現地形状と偽って追加していない。既存の誘導線・入口の当たり判定を維持。 |
| 縁石・誘導網の全経路 | **既存維持・追加保留** | 既存の測った島状区画と歩道を基準に接地を修正した。既存境界を越えて縁石を伸ばす案や、仮A8経路を推測で全網へつなぐ案は採用していない。必要な追加情報は、A8の接続先となる既存経路端点、縁石の実際の切れ目・段差の起終点。単に座標nullを理由に保留したものではない。 |

通常表示はURL指定不要。`?fit=off` が今回の追加前、`?fit=preview` が通常採用＋4対象の確認案。`?fit=preview&fitparts=a8` のように `a8,louvre,fence,tactile` を個別指定できる。確認案は画面注記と台帳で区別する。見える形状を切り替えても、元の入口・施設の当たり判定を取り除かない。新しい石壁だけを障害物へ加える。

## 座標・寸法の根拠

計画はX東/Y北、WebはX東/Y上/Z南。すべてm、Web上方向はT.P.−15m。数値は**実装した値**であり、測量の確定値とは区別する。既存GLBの座標・地面レイキャスト値は計算値、施設対応と寸法・向きは写真と既存構造からの推定。

| 対象 | 実装値 | 根拠・詳細記録 |
| --- | --- | --- |
| 宝くじ | 計画中心 `(10.900,-61.550)`、Z基準T.P.15.626216m、回転187°、均等倍率1。正面5.6m、全外形幅約5.75m | [接地点と置換帯](../../assets/street/hachiko-fit/web/lottery.json)。初回 `(10.900,-62.250)` ではC段階外壁の奥となった。[初回正面](../../evidence/hachiko-fit-20261017/lottery-trial1/fit_lottery_front.png)から修正。[公式売場](https://www.takarakuji-official.jp/map/spot/?uribaCode=9002211303)と[3窓写真](https://atarukana.com/tokyo/)を参照。 |
| A8 | 中心 `(35.250,-47.000)`、モデル原点T.P.15.144106m、回転8.3°、均等倍率1。柱底の局所0.08mを加えると地面T.P.15.224106m | [配置・部分置換範囲](../../assets/street/hachiko-fit/web/a8.json)。[2月公式図p2](https://shibuyaplusfun.pictona.jp/scc-admin/asset/shibuyaplusfun/000002/000002/38f57a3e.pdf)、[8月資料p3](https://shibuyaplusfun.pictona.jp/scc-admin/asset/shibuyaplusfun/000002/000002/9ca91390.pdf)。撮影日不明。 |
| ルーバー | 中心 `(51.173,-55.148)`、底T.P.18.000m、回転−84.073°、均等倍率0.6 | [配置](../../assets/street/hachiko-fit/web/louvre.json)と[既存14面](station_north_louvre_planes_20261017.json)。11月写真の形は参照したが、10月状態・支持高さ・対応面は未確定。 |
| 囲い | 幹基準 `(7.400,-45.500)`、回転35°、像側−0.95m、壁4.6×0.24×0.50m | [各地面試料と寸法](../../assets/street/hachiko-fit/web/enclosure.json)。11月写真の見える側だけ。笠石は一片ずつ9°傾け、地面の傾きで底が浮かないよう15mm埋めた。 |
| 舗装 | 像中心 `(11.568176,-48.685732)`、35°、既存局所範囲 `[-5.2,-4,5.2,3]`、高さ差0 | [材質置換](../../assets/street/hachiko-fit/web/finish.json)。2025-07-13/11-01の写真を形状参照。石の配置は新規の推定図柄。 |
| 柵 | 端点 `(2.071600,-46.222599)` → `(2.612800,-44.417133)`、73.31356°、梁中心は各地面＋0.78m | [1区間の記録](../../assets/street/hachiko-fit/web/fence.json)。既存レール生成処理の支柱3–4間を使用。白梁の実際の設置区間との一致は未確認。 |
| 誘導線 | 端点 `(36.420900,-55.028769)` → `(36.031138,-52.357049)`、8.3°、延長2.7m | [経路と地面試料](../../assets/street/hachiko-fit/web/tactile.json)。仮A8の直前だけで終わり、全網とのつながりは保留。 |

大木の枝・幹は2025-11-01、葉は2026-08-08、囲い・ルーバーは11月、舗装・白梁は7月、A8は2025年公開資料を組み合わせた推定。これを2025年10月の同時点の確定景観とはしない。[資産の出典・権利](../../assets/street/hachiko-fit/source/RIGHTS.md)、[大木のライセンス台帳](../../assets/street/hachiko-rear-tree/README.md)に著者・ライセンス・画像をコピーしていない範囲を記録した。囲いの笠石上端0.605mは埋め込み基準からの公称値で、9°傾斜の高い側は約0.630m（地面から約0.615m）となる。

## 同一視点の比較画像

`before` は `fit=off`、`normal` は通常採用、`preview` は確認案込み。同じpose・視野角・`q=low`で比較し、撮影時の実際の各rootの読込状態をログへ保存する。最終画像は下記。`lottery-trial1`、`a8-trial1`、`preview-trial1` は試して修正した案の履歴で、最終採用画像と混同しない。

| 視点 | 変更前 | 通常配置 | 確認用仮配置 |
| --- | --- | --- | --- |
| 像と売場を見渡す全景 | [前](../../evidence/hachiko-fit-20261017/before/fit_overview.png) | [通常](../../evidence/hachiko-fit-20261017/normal/fit_overview.png) | [確認案](../../evidence/hachiko-fit-20261017/preview/fit_overview.png) |
| 全景 | [前](../../evidence/hachiko-fit-20261017/before/fit_whole.png) | [通常](../../evidence/hachiko-fit-20261017/normal/fit_whole.png) | [確認案](../../evidence/hachiko-fit-20261017/preview/fit_whole.png) |
| 売場 正面・斜め・足元 | [正面](../../evidence/hachiko-fit-20261017/lottery-before/fit_lottery_front.png) / [斜め](../../evidence/hachiko-fit-20261017/lottery-before/fit_lottery_oblique.png) / [足元](../../evidence/hachiko-fit-20261017/lottery-before/fit_lottery_feet.png) | [正面](../../evidence/hachiko-fit-20261017/normal/fit_lottery_front.png) / [斜め](../../evidence/hachiko-fit-20261017/normal/fit_lottery_oblique.png) / [足元](../../evidence/hachiko-fit-20261017/normal/fit_lottery_feet.png) | — |
| 囲い 正面・足元 | [前](../../evidence/hachiko-fit-20261017/before/fit_enclosure.png) / [足元](../../evidence/hachiko-fit-20261017/before/fit_enclosure_feet.png) | [後](../../evidence/hachiko-fit-20261017/normal/fit_enclosure.png) / [足元](../../evidence/hachiko-fit-20261017/normal/fit_enclosure_feet.png) | — |
| 舗装 | [前](../../evidence/hachiko-fit-20261017/before/fit_paving.png) | [後](../../evidence/hachiko-fit-20261017/normal/fit_paving.png) | — |
| A8 正面・斜め・足元 | [正面](../../evidence/hachiko-fit-20261017/before/fit_a8_front.png) / [斜め](../../evidence/hachiko-fit-20261017/before/fit_a8_oblique.png) / [足元](../../evidence/hachiko-fit-20261017/before/fit_a8_feet.png) | 既存維持 | [正面](../../evidence/hachiko-fit-20261017/preview/fit_a8_front.png) / [斜め](../../evidence/hachiko-fit-20261017/preview/fit_a8_oblique.png) / [足元](../../evidence/hachiko-fit-20261017/preview/fit_a8_feet.png) |
| ルーバー | [正面](../../evidence/hachiko-fit-20261017/before/fit_louvre_front.png) / [斜め](../../evidence/hachiko-fit-20261017/before/fit_louvre_oblique.png) | 既存維持 | [正面](../../evidence/hachiko-fit-20261017/preview/fit_louvre_front.png) / [斜め](../../evidence/hachiko-fit-20261017/preview/fit_louvre_oblique.png) |
| 白柵 | [前](../../evidence/hachiko-fit-20261017/before/fit_fence.png) | 既存維持 | [1区間](../../evidence/hachiko-fit-20261017/preview/fit_fence.png) |
| 誘導線 | [前](../../evidence/hachiko-fit-20261017/before/fit_tactile.png) | 既存維持 | [局所案](../../evidence/hachiko-fit-20261017/preview/fit_tactile.png) |

## PR #85 の3指摘への対応

1. **出典台帳**: 大木のREADMEと元パッケージのPROVENANCEを保存。Commonsの著者・CC BY-SA 4.0、記事画像の権利留保、モデル／材質が独自の手続き生成であることを区別。記事画像・元写真の追加コミットなし。
2. **rearTree撮影状態**: 撮影スクリプトに `__viewer.rearTree` と `sceneFit` を記録し、off時と成功時をassert。新しい通常画像の4つのrearTree視点でも実際の成功状態を記録する。読込失敗時の画像を成功扱いにしない。
3. **フォント互換性**: 上面図生成でLinuxのDejaVu/Liberation、WindowsのArial、Pillow内蔵フォントの順に選ぶ。固定Windowsパスへの依存を除いた。すべての候補フォントがない条件を模擬し、内蔵フォントでリポジトリ外に再生成できることを確認した。

## 検証と残る差

地面頂点の維持、選択したrootだけの可視切替と失敗時の原物維持、A8北側屋根の保持を回帰テストへ追加。既存の性能予算上限は変えず、確認用資産も含めてB予算へ登録した。標準テストとbuildの最終結果はPR本文に記録する。新しいスクリーンショットは通常・仮配置の全景と各対象を見て判定し、テスト通過を現地景観の完成とは扱わない。

- 最終標準テスト `npm test -- --maxWorkers=2 --testTimeout=30000`: **60ファイル・265件通過**。
- `npm run build`: **成功**。最終画像はそのbuild成果物をpreview配信して撮影した。
- B資産の合計は確認案込みで **2,745,576 byte / 33,297 triangles / 35 primitives**。上限3,000,000 byte / 120,000 triangles / 40 primitivesを変更していない。
- 最終画像のログはbefore 12、lottery-before 3、normal 13、preview 9、class 2の**39状態**でHTTP/JSエラーなし、`rearTree.ok`を確認。変更前後17組はpose・実際のcameraPosが一致。
- [夜の全景](../../evidence/hachiko-fit-20261017/normal/fit_whole_night.png)、[分類の全景](../../evidence/hachiko-fit-20261017/class/fit_overview.png)、[売場の分類](../../evidence/hachiko-fit-20261017/class/fit_lottery_front.png)、[大木4視点を含む成功状態ログ](../../evidence/hachiko-fit-20261017/normal/capture_log.json)を保存。低負荷設定では細いルーバーに画素単位のエイリアシングが残る。接合部の近接二重面は避けたが、これを景観完成やすべての動的なちらつきの解消とは扱わない。

残る差は、A8の既存屋根との接合・分割範囲、ルーバー設備の実際の支持面と高さ、白梁の設置線との対応、誘導線の既存網への接続、囲いの背面全周。配置を試した画像と数値を残し、これらの確認案を通常採用済みとは報告しない。マージ・デプロイは行わない。
