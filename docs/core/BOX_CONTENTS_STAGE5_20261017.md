# BOX可視内容物とハチ公周辺ステップ5

## 基準・採用状態

基準は最新main `96d301a0a0342d7175dd27b7609693f51652172b`（PR87マージ）。開始時の作業ツリーはクリーン。専用ブランチ `codex/box-contents-stage5-20261017`、既存の別作業ツリーを保全。マージ・デプロイしない。

実装 `94fd005`、必須3素材 `8bb6a4d`、TKTS・棚壁取付 `d4ca12d`、接地等の回帰 `4465223`。必須3素材の通常描画と比較を先に通し、その状態から残りを組み込み、全体を確認した。

| 対象 | 現在の採用 | 内容 |
|---|---|---|
| 案内カウンター＋左2段ラック | 今回通常採用 | incomingの既存GLBそのまま |
| 横長壁面モニター | 今回通常採用 | 木壁に埋まらないよう前方へ100mm調整 |
| 開いたノートPC | 今回通常採用 | 案内右側天板へ接地、訪問者側に蓋の背 |
| TKTS上部＋端末の調整済み一式 | 今回通常採用 | 別区画。上部殻の切断端から床まで局所幕板を推定補完 |
| TKTS独立縦モニター・赤い縦サイン | 今回通常採用 | 統合版の部品一覧を照合して別途登録 |
| 物販陳列網・6箱棚・木壁の部分組立 | 今回通常採用 | 完成済み組立を92%一様縮小。下端切断を持つ木壁は部分モデルのまま |
| 元TKTS単体カウンター・元端末・元棚の重複部品 | 未採用（代替済み） | 統合版と二重ロードしないため。場所不明による保留ではない |
| PR87の8部品 | 通常採用を維持 | 宝くじ、A8、屋根接合、駅ルーバー、全周石囲い、白柵、舗装・縁石・誘導線。確認用へ戻さない |
| 像・台座・石碑・植栽、BOX建築・時計・看板・テラス、JR入口、交番 | 既存採用を維持 | 再制作・重複追加なし |

今回は指定された可視内容物をすべて通常表示へ配置した。**ZIP全体の全モデル採用やBOX全室制作とは異なる。** 商品、画面UI、広告原稿、隠れた配線、下部収納内部、入室機能は追加していない。

## 出典・配置と時点

座標・高さ・縮尺の完全な一覧は [内容物README](../../assets/street/box-contents/README.md) と [layout.json](../../assets/street/box-contents/web/layout.json)。建築の既存親原点 `(25.108505, -46.695255, .489115)`、角度−81.083977度を共通使用。ローカルBlender座標からGLB Y-upへの位置変換は一度だけ。床 .248、カウンター天板1.228、TKTS天板1.298、天井2.584mを区別した。

[and trip.公式紹介](https://www.andtrip.jp/article/006193.html)（2024-09-19公開、撮影日不明）の案内・TKTS・物販写真3枚を実際に開いて照合。案内の左に物販、PCは天板右、TKTSは別区画で縦モニターを赤いサインの左へ配置した。施設内の絶対位置・寸法・取付高さは実測でなく、既存窓割・床・天井との整合による推定。

**ハチ公周辺だけ**、2025年10月固定に加えて許可された工事後景観・異なる時期を併用する。今回の2024年内容物、既存BOXの2024年外観、PR87で採用済みの2025年2月案内図・7月/8月/11月写真、樹木の2026年8月参考は同時点の実景再現ではない。各原出典は既存台帳を継続し、他地区へ例外を広げない。画面にも内容物の時期・推定を注記。

3ZIPをDrive取得応答のダウンロード参照からローカルへ実保存。全CRC・manifest91ファイルのサイズ/SHA-256成功。必須3素材と既存検証済み素材は再取得せず。[取得記録](../../assets/street/box-contents/source/intake-verification.json)。写真・署名URL・認証情報はコミットしていない。

## 実描画で行った調整・ステップ5

1. 既存ガラスのまま必須3素材を描画。カウンター、左ラック、横長モニター、開いたPCの識別を正面/斜めで確認。[最初の3素材](../../evidence/box-stage5-20261017/first-three/contents_oblique.png)。
2. 棚壁追加時に天井を越えない一様縮尺を選び、モニター背面と木壁前面に約19mm離隔。木壁の切断端を床と誤認して落とす処理はしない。
3. TKTS上部殻の床置きを避け、前・左右の簡素な幕板を床から殻下端へ接合。元端末と単体カウンターを追加しない。縦サイン上端は天井より24mm低い。
4. 外部テラス、時計、柱、窓割と内容物を確認。ガラスの全透明化・非表示・材質変更は実施していない。画面は配布物の無地・非発光状態を維持。夜間も既存照明で見え方を確認。
5. PR87の採用物、像・石碑、BOX外観、駅周辺を全景・近景で再確認。今回の内容物以外は既存配置を保持し、必要のない地形・道路網・建築の再生成を行わない。通常8部品の読み込み状態も各ログで照合。

## 比較画像

前後12組は同じ位置・四元数・FOV・解像度・時間帯・品質low。[機械照合記録](../../evidence/box-stage5-20261017/comparison-check.json)。beforeはmainに撮影用cameraState取得だけを加えたbuild、afterは通常配置済みbuild。最終buildの追加差はHUD内の推定注記だけで、比較画像の描画対象は同一。標準品質mediumは別フォルダで確認し、lowとの画質差を配置差と扱わない。

| 確認 | 前 | 後 |
|---|---|---|
| 交差点側全景 | [前](../../evidence/box-stage5-20261017/before/fit_whole.png) | [後](../../evidence/box-stage5-20261017/after/fit_whole.png) |
| 駅側全景 | [前](../../evidence/box-stage5-20261017/before/stage5_station.png) | [後](../../evidence/box-stage5-20261017/after/stage5_station.png) |
| BOX正面 | [前](../../evidence/box-stage5-20261017/before/contents_front.png) | [後](../../evidence/box-stage5-20261017/after/contents_front.png) |
| BOX斜め・外観 | [前](../../evidence/box-stage5-20261017/before/box_oblique.png) | [後](../../evidence/box-stage5-20261017/after/box_oblique.png) |
| 案内斜め | [前](../../evidence/box-stage5-20261017/before/contents_oblique.png) | [後](../../evidence/box-stage5-20261017/after/contents_oblique.png) |
| 案内夜景 | [前](../../evidence/box-stage5-20261017/before/contents_night.png) | [後](../../evidence/box-stage5-20261017/after/contents_night.png) |
| TKTS | [前](../../evidence/box-stage5-20261017/before/contents_tkts.png) | [後](../../evidence/box-stage5-20261017/after/contents_tkts.png) |
| 物販・時計の関係 | [前](../../evidence/box-stage5-20261017/before/contents_shelves.png) | [後](../../evidence/box-stage5-20261017/after/contents_shelves.png) |
| 石囲い・白柵・接地 | [前](../../evidence/box-stage5-20261017/before/fit_enclosure.png) | [後](../../evidence/box-stage5-20261017/after/fit_enclosure.png) |
| A8・通行部 | [前](../../evidence/box-stage5-20261017/before/fit_a8_oblique.png) | [後](../../evidence/box-stage5-20261017/after/fit_a8_oblique.png) |
| 誘導線と既存端の接続 | [前](../../evidence/box-stage5-20261017/before/fit_route_join.png) | [後](../../evidence/box-stage5-20261017/after/fit_route_join.png) |

12組目の初期カメラは撮影回帰用。駅側全景の最初の試写は屋根に遮られたため、上記の共通カメラへ変更し前後とも撮り直した。

## 検証と限界

- `REUSE_CAPTURE=1`：poseなしビューや異なるシーン条件へ移ると新規ページに切り替える。pose間も毎回明示的に移動。位置だけでなく四元数・FOV・aspect・時間帯を記録。回帰テスト追加。
- 実GLBに対する床・PC天板・モニター高さ・TKTS幕板接合・背面壁・天井・扉からの離隔、null/重複変換の拒否、既存BOXバイト同一性を検証。
- 内容物パックは **2,446,988 bytes / 33,900 triangles / 40 primitives**。既存の独立street furniture B予算内。BOX建築本体は別の既存B資産として維持。シーン全体も集計対象。予算の上限は変更していない。描画プリミティブに追加の余裕はなく、将来の追加では統合等が必要。
- 全体の実測寸法・現在の営業状態・画面内容を再現し切ったとは扱わない。既存テラスの傾斜・段差、部分木壁の切断、写真で見えない支持形状は推定の制約として残る。通路への新しい張り出しは作っていないが、入室やバリアフリー認証は今回の対象ではない。
- FPS、歩行表示、衝突、QFRONT、西武、全域地形は変更していない。

最終実装 `de4fdf7` に対して標準テスト **62ファイル・272件成功**、`npm run build` 成功、diffチェック成功。[テストログ](../../evidence/box-stage5-20261017/final-tests.log)、[buildログ](../../evidence/box-stage5-20261017/build.log)、[画像・状態確認](../../evidence/box-stage5-20261017/review.json)。通常22状態で内容物8ロード単位とPR87の8部品が成功し、JS/HTTP/GLBエラーなし。12組の実カメラ一致に加え、poseあり→なしの結果が再利用しない新規ページの位置・四元数・FOVと一致した。

実際に開いた最終画像：上記afterの全景・昼夜近景・接地11枚、standardの8枚、freshの像近景。特に[標準品質の全景](../../evidence/box-stage5-20261017/standard/fit_overview.png)、[案内斜め](../../evidence/box-stage5-20261017/standard/contents_oblique.png)、[案内夜景](../../evidence/box-stage5-20261017/standard/contents_night.png)、[BOX全体夜景](../../evidence/box-stage5-20261017/standard/box_stage5_night.png)、[像・台座・石囲い](../../evidence/box-stage5-20261017/fresh/surround.png)、[石碑と宝くじ](../../evidence/box-stage5-20261017/standard/memorial_oblique.png)、[ルーバー](../../evidence/box-stage5-20261017/standard/fit_louvre_front.png)、[A8前の足元](../../evidence/box-stage5-20261017/standard/fit_tactile.png)で対象を確認した。

この範囲のステップ5の描画・局所取付調整・レビュー資料を完了。既存木壁は切断端のある部分資産で、モニターは無地、幕板・絶対配置は推定という表現上の制約を残す。写真との完全一致や全室完成をテスト成功から推定しない。
