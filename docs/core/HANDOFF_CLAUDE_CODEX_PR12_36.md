# Claudeへの引き継ぎ：CodexのPR #12〜#36を精査・修正する

> **2026-10-14 追記（Claude）：第1回の精査と修正は [CLAUDE_REVIEW_PR12_36.md](CLAUDE_REVIEW_PR12_36.md)。** 大盛堂ビルの角、駅の連絡通路の北面、ハチ公像の色と植栽、109の材質を直した。直していない候補も同じ資料の§3にある。

2026-10-14（日本時間）。オーナーの最新指示は「一回Claudeに精査と実装させるので、PR12くらいから実装した内容をまとめてClaudeが読める形にする」。Codexの新しい実装はここで止め、Claudeの精査・修正を優先する。古い引き継ぎの「Codexが指示を待たず連続実装」は、この最新指示より優先しない。

## 1. まず読むもの・開始ブランチ

1. この資料：現在の実装・注意点・優先順位。
2. [DEV_ENVIRONMENT.md](DEV_ENVIRONMENT.md)：Claudeと同じBlender 4.2.3 CLI、Node 22、Python 3.11、Playwrightの構成。
3. [DECISIONS.md](DECISIONS.md)と[CODEX_C2B_REVIEW.md](CODEX_C2B_REVIEW.md)：年代、既存成果、写真比較、過去の失敗。古い実験の「通常表示へ出さない」方針は最新AGENTS.md/レビューより優先しない。
4. 対象の下記レポートとassetsのREADME・source/refs。最初から過去の全資料を読む必要はない。

**開始点はPR #36のブランチ `origin/codex/core-exterior-walk`。** mainだけを取ると最新の実装が欠ける。確認時点の状態は次のとおり。

| PR | 状態・注意 |
|---|---|
| #12〜#30 | mainへマージ済み。#19は設計資料のみ |
| #31〜#34 | マージ済みだが、マージ先はそれぞれ前段featureブランチ。mainへ反映済みとは言えない |
| #35 | OPEN、base main。#31〜#34の実装と周辺10資産をmainへ統合するPR |
| #36 | OPEN、base main。#35の変更も含む最新状態。道路・歩道・点字・接地の追加 |

GitHub確認スナップショットは[CODEX_PR_HISTORY_FOR_CLAUDE.json](CODEX_PR_HISTORY_FOR_CLAUDE.json)。状態は変わるので作業前に再確認する。元の実装/撮影を確認した基準コミットは`35c8d38`（その後のこの引き継ぎ追加は資料のみ）。確認したmainの先端は`3ed1144`（#30）。

既存の未コミット作業を保全し、必要なら別worktreeで開始する：

```sh
git fetch origin
git worktree add -b claude/review-codex-pr12-36 ../shibuya-scene-2-claude-review origin/codex/core-exterior-walk
```

同名ブランチ/ディレクトリが既にある場合は別名を選び、reset/clean/stash/force-pushしない。旧リポジトリ・西武A館WIPを上書きしない。

mainへ届ける順は#35→#36。両方main向けなのでbase変更は不要。Claudeの修正も最新依存変更を含むブランチから作り、main向けPRに依存順を記載する。自動マージはしない。

## 2. 全体像と、できていないこと

通常表示に主要建物の個別B外装、駅の部分B、ハチ公像/周辺、広場設備、舗装、点字、道路/地形を追加した。元の汎用Cを対応するsource_id/PLATEAU親で除外した。最新のC群は293件で、すべてを個別高品質へ作ったわけではない。

**全体は試作。写真品質の完成ではない。** 特に規則で作った窓割り、空の看板面、駅の形、像、素材の質感はClaudeに精査・改善してほしい。機械検査は「有限な座標・予算・接地・重複等」の検査であり、実際の寸法/施設同定/2025年10月/写真忠実度の正しさではない。

QFRONT・西武・既存の高度な信号/樹木/地下鉄出入口は再制作の対象から外してきた。これらと今回の追加物の接続・表示回帰は確認してほしい。既存デザインを調整する場合も元の成果を保全する。

## 3. PR別の実装履歴

開始点は#12（渋谷駅前ビル）で合っている。#10/#11は初期画面の西側広告・外装に関わる前提なので補足する。以下は当時の変更で、後続で更新された箇所は次節にまとめる。

| PR | 実装した内容 | 詳細レポート |
|---|---|---|
| [#10](https://github.com/kesusugar/shibuya-scene-2/pull/10)・[#11](https://github.com/kesusugar/shibuya-scene-2/pull/11) 前提 | センター街入口西側をB化。屋上看板・赤い角・窓・入口を補正。広告の切り貼り/割付けは未達 | [西側B](C1_WEST_BLOCK_B_REPORT.md)、[補正](C1_WEST_BLOCK_REFINE_REPORT.md) |
| [#12](https://github.com/kesusugar/shibuya-scene-2/pull/12) | 渋谷駅前ビルway/60739635をB化。丸い角・東側正面・店舗/窓・11月看板層、C親除外 | [駅前ビル](C1_EKIMAE_B_REPORT.md) |
| [#13](https://github.com/kesusugar/shibuya-scene-2/pull/13) | 駅/マークシティ連絡通路候補と重なる橋を部分B化。接続側の開口 | [連絡通路](C1_STATION_CONCOURSE_REPORT.md) |
| [#14](https://github.com/kesusugar/shibuya-scene-2/pull/14) | JR北側上屋を部分B化。南側とJR高架は元形状を保持、点字帯の継ぎ目を補正 | [北側上屋](C1_STATION_NORTH_REPORT.md) |
| [#15](https://github.com/kesusugar/shibuya-scene-2/pull/15) | 連絡通路の一様な発光面を透明ガラス・浅い内部・器具・横枠へ置換 | [ガラス/照明](C1_STATION_GLAZING_REPORT.md) |
| [#16](https://github.com/kesusugar/shibuya-scene-2/pull/16) | 駅西側の小施設候補を白い金属外装・目地・換気口のBへ置換 | [駅小施設](C1_STATION_SERVICE_REPORT.md) |
| [#17](https://github.com/kesusugar/shibuya-scene-2/pull/17) | 駅西側高架候補の閉じた箱を桁・8支柱・補強材・青い養生網へ置換 | [西側高架](C1_STATION_VIADUCT_REPORT.md) |
| [#18](https://github.com/kesusugar/shibuya-scene-2/pull/18) | 銀座線上部を部分B化。公式設計幅12mを参考にM形フレーム、ホーム/ドア/点字帯/線路/照明。下部保持 | [銀座線](C1_GINZA_CANOPY_REPORT.md) |
| [#19](https://github.com/kesusugar/shibuya-scene-2/pull/19) | 初期画面重視の設計・既存Claude資産の保全方針。モデル変更なし | [初期画面計画](ENTRY_VIEW_QUALITY_PLAN.md)、[候補](ENTRY_VIEW_REMAINING_CANDIDATES.md) |
| [#20](https://github.com/kesusugar/shibuya-scene-2/pull/20) | 初期画面左側の第一勧銀共同ビルway/114755219を個別B化 | [第一勧銀](C1_DAIICHI_KANGIN_REPORT.md) |
| [#21](https://github.com/kesusugar/shibuya-scene-2/pull/21) | センター街入口ゲートの支柱・アーチ・掲示面・照明器具を追加 | [ゲート](C2_CENTER_GAI_GATE_REPORT.md) |
| [#22](https://github.com/kesusugar/shibuya-scene-2/pull/22) | 北側歩道/島に自作の平板舗装アトラス。形・高さは保持 | [北側舗装](C2_NORTH_PAVING_REPORT.md) |
| [#23](https://github.com/kesusugar/shibuya-scene-2/pull/23) | 広場に赤茶色ブロック・淡い区画線。北側舗装と描き分け | [広場舗装](C2_PLAZA_PAVING_REPORT.md) |
| [#24](https://github.com/kesusugar/shibuya-scene-2/pull/24) | 三角形重心で段状になった材質境界を、辺に沿う分割へ修正 | [境界修正](C2_PAVING_BOUNDARY_REPORT.md) |
| [#25](https://github.com/kesusugar/shibuya-scene-2/pull/25) | 中央3横断歩道の6端に警告24/誘導36、計60枚を追加 | [初期点字](C2_TACTILE_REPORT.md) |
| [#26](https://github.com/kesusugar/shibuya-scene-2/pull/26) | 広場の2アプローチを分岐でつなぎ南へ9m延伸。点字60→164枚 | [点字延伸](C2_TACTILE_LINKS_REPORT.md) |
| [#27](https://github.com/kesusugar/shibuya-scene-2/pull/27) | M027から円形路面蓋1個を推定配置。径約0.38m、自作の枠/模様/補修跡 | [路面蓋](C2_ROAD_COVER_REPORT.md) |
| [#28](https://github.com/kesusugar/shibuya-scene-2/pull/28) | ハチ公像・台座・銘板を自作。2025年OSM位置と7月/11月写真の形を参考 | [像](C2_HACHIKO_REPORT.md) |
| [#29](https://github.com/kesusugar/shibuya-scene-2/pull/29) | 像周囲の石縁・傾斜銀色レール2区間・低木6株・自然石6個・石板 | [像周辺](C2_HACHIKO_SURROUND_REPORT.md) |
| [#30](https://github.com/kesusugar/shibuya-scene-2/pull/30) | 像周囲の灰色方形敷石区画と、像の頭/先細りの鼻先/目/耳を補正 | [敷石と顔](C2_PLAZA_FINISH_REPORT.md) |
| [#31](https://github.com/kesusugar/shibuya-scene-2/pull/31) | センター244・平和クワトロ・スクランブルスクエア・フクラスの4B外装 | [周辺4棟](C1_NEIGHBOURHOOD_REPORT.md) |
| [#32](https://github.com/kesusugar/shibuya-scene-2/pull/32) | Core外DEM地形、JR南東施設のB、高架/銀座線/大型建物の足元補填 | [地形/駅南東](C1_STATION_FINISH_REPORT.md) |
| [#33](https://github.com/kesusugar/shibuya-scene-2/pull/33) | 売店候補、喫煙設備候補2基、名称不明小構造物。入口/扉を推定制作 | [広場小施設](C2_PLAZA_FACILITIES_REPORT.md) |
| [#34](https://github.com/kesusugar/shibuya-scene-2/pull/34) | 14横断歩道の16端へ点字108枚、6入口へ接続166枚。像周辺の裏石壁2区間 | [歩道補足](C2_WALK_FINISH_REPORT.md) |
| [#35](https://github.com/kesusugar/shibuya-scene-2/pull/35) | 周辺10資産、複合建物の表裏判定、DEM範囲拡張。#31〜#34のmain統合を含む | [周辺10資産](C1_NEARBY_FINISH_REPORT.md) |
| [#36](https://github.com/kesusugar/shibuya-scene-2/pull/36) | 道路3資産・仮fill置換・白線8帯、未配置12端の点字80枚、15建物/駅資産の足元更新 | [最新道路/接地](C2_EXTERIOR_REPORT.md) |

## 4. 最新状態を読むときの上書き関係

古いレポートの「次に作る」「未配置」は当時の記録。最新のソース・通常ロード一覧と合わせて読む。

- 点字は現在4資産：`tactile`164枚、`tactile-extra`108枚、`tactile-links`166枚、`tactile-outer`80枚、計518枚。#25の60枚は164枚の中に含まれ、別に加算しない。#34で未配置だった12端は#36で配置済み。**現実の点字経路を確認済みとは言えない。**
- #31で未照会だった大型建物の足元、#32のDEM範囲/高架支柱の値は後続で更新。最新の各`source/data/stats.json`を見る。最新共通外装13資産の生成時照会では、マークシティに未取得1点、他12資産は未取得0点。これは照会サンプルの結果で、建物の全周・実地の仕上げ高を保証しない。センター244/クワトロ等の過去の値をこの13資産へ混ぜない。
- 最新DEMはX[-330,380]・Y[-450,350]、6m格子、20mの継ぎ目補間。標高から作った下地で、仕上げ高の実測ではない。
- #36はCore GLBを保持し、**実行時だけ仮の`ground_fill`を外す**。測った車道/交差部/歩道/白線/縁石は保持。追加道路とDEMの両方が成功した場合だけ置換し、失敗時は元fillを継続。実行時の構成変更を「元の全地面を何も変えていない」と解釈しない。
- 外側道路のマスクは元Coreの測った道路/歩道+2cm。仮fillまでマスクに入れると109前などの道路が消えるため、除外する。
- 追加道路を使う足元生成でも、旧Coreの仮fillをBVH照会から除く。元fillへ接地した裾を最新仕上げ面の結果と取り違えない。
- マークシティ東西は同じPLATEAU親。`mark-city`1資産＋OSM2件の別名で扱い、親全体を2回ロードしない。分割するなら部分形状と親/別名の除外を合わせて整理する。
- 窓/枠の表裏は共通重心だけで誤る複合建物があったため、元の殻の両側へ判定して修正した。追加形状/開口を変えると殻の閉じ方や判定結果も精査が必要。

## 5. 変更・再生成する場所

| 分野 | 主な編集先 | 読むべきもの |
|---|---|---|
| 西側街区/駅前ビル | `assets/buildings/west-block/`、`ekimae/`のsource/data・source/blender。広告はwebの年代レイヤーと元素材 | 各README、#10〜#12レポート。初期Bは接地/座標の実装が共通facadeと異なる |
| 駅 | `assets/buildings/station-concourse/`、`station-north/`、`station-service/`、`station-west-viaduct/`、`ginza-canopy/`、`station-southeast/` | 各README・parts/layout/stats、`docs/core/station_refs/` |
| 個別外装 | `tools/core/build_facade.py`と各buildingの`source/data/plateau.json`、`layout.json`、wrapper `source/blender/build.py` | 各refs/SOURCES、レポート、manifestのsource_id/source_aliases |
| 元Core舗装 | `assets/ground/core/source/blender/build_ground.py`、`paving_boundary.py`、source/dataの舗装設定・アトラス | #22〜#24。形/高さ保持の検査と実際の舗装境界の正しさは別 |
| 外側道路 | `assets/ground/exterior/source/tools/`、`source/blender/build.py`。`exterior-west/middle/east`が輸出単位 | [外側道路README](../../assets/ground/exterior/README.md)、raw GMLのURL/SHAはsource/data/sources.json |
| DEM | `assets/ground/extension/source/tools/prepare.py`、source/dataのDEM入力、source/blender/build.py | 道路三角形を合わせたマスクで再生成。Core仮fillを保護マスクへ戻さない |
| 像/周囲/局所敷石 | `assets/street/hachiko/`、`hachiko-surround/`、`plaza-finish/` | layout/statsとsource/refs、#28〜#30/#34 |
| 点字/小施設/路面蓋 | `assets/street/tactile*`、`plaza-facilities/`、`drainage/`、`assets/buildings/plaza-kiosk/` | 各README、layout、stats。型・位置の推定を保つ |
| 表示/歩行/見た目 | `src/main.ts`、`src/controls/viewer-controls.ts`、`src/world/`、`src/perf/budget.ts` | 読込、C除外、実際のscene登録、歩行ground/obstacle、共通Look |
| 台帳 | `docs/core/ASSET_REGISTER_V2.csv`、`STRUCTURE_REGISTER.csv`と各manifest | 実装状況と同定・寸法・年代の確認を別扱い。台帳の名称が確定とは限らない |

生成後は`npm run sync-assets`でassets→publicを反映する。publicは生成物。元のauthoring treeを編集する。共通生成器を変えただけでは既存GLBが変わらないので、対象を再生成し、manifest・出典・予算・画像も更新する。

## 6. Claudeに最優先で精査してほしい箇所

1. **初期画面・左右で見えるB正面。** 西側街区/駅前ビルの広告割付け、窓・店舗・丸い角、第一勧銀と追加建物の規則的な窓・空の看板。カメラを動かして欠落を隠さず、見える部分から改善してほしい。
2. **駅の施設同定と形。** 北側は部分B、連絡通路は浅い内部の表現、小施設/高架/南東施設の用途と写真対応は推定を含む。銀座線の設計幅12mを検査したことは、全ホーム/下部/10月外観の一致ではない。養生網・工事状態は年月を確認して見直す。
3. **像・広場のデザイン。** ハチ公の鼻/耳/体、台座/銘板、銀色レールの形、石縁/石板、低木/自然石、敷石の範囲・向き。2025年7月写真の選挙告知板は採用していない。銘文・掲示内容・植物種・実寸は未確認。
4. **足元と段差。** #12の駅前ビルでは当時+5cmの接地補正を記録。初期Bと最新facadeのdatum/hints/GLB絶対座標の扱いを混同しない。標高補間は部分的に埋まり/裾を補っただけで、全歩行経路の接地・段差を保証しない。
5. **小施設。** 売店候補を交番と断定しない。喫煙設備の小さなOSM形状は約1.7×0.45mで、喫煙区画全体ではない。灰皿/箱の種類と配置、名称不明施設の扉・外装・10月状態を再確認してほしい。
6. **歩行動作（未修正）。** 地面のレイが外れるとheight=0、急な段差制限なし、膝/胸の2レイで衝突。像/像周辺/小施設は衝突登録に未追加。静止画の接地成功だけでは歩行品質を評価できない。

写真に明確な根拠がある場合は、規則外装やPLATEAUの不足を修正してよい。屋根頂点保持テストは元データとの一致を守る検査で、元データが現実の正解という意味ではない。根拠ある変更ではsource/テスト/台帳も更新し、接地の問題を屋根や全体高さの無根拠な移動で隠さない。

## 7. 資料の年代・同定・広告の限界

- 駅前の目標は2025年10月。初期の高所写真は1月/2月、像は7月/11月、周辺は2010/2019/2020/2023/2024の補助も含む。別年の形を使ったことを10月確認済みにしない。
- #35の109は2019年、シネは2010年、フクラスは2020年、スクエア/ストリーム/サクラは2023年、パルコは2024年、マークシティは2025年6月、ヒカリエは2025年3月など。正確な出典・作者・ライセンスは各refs/SOURCESで確認。
- 高木・ビック・東側雑居の独立写真同定は未達。旧OSM平面形の取得は2026年9月で、2025年の外観証拠ではない。
- 駅前ビルの参考写真の屋上広告と実装広告には1月/11月差がある。広告の切り貼り・字形・不足素材・UV/割付け・夜の画像発光は完成していない。以前は内容補正を後工程にしたが、今回オーナーはClaudeによる精査/実装を希望している。修正時は撮影年月とライセンスを確認し、別レイヤーで扱う。
- 写真位置や寸法が未確認でも、種類の明らかな物を普通の見た目で制作する既存方針を維持。未確認だけを理由にすべて削除/非表示へ戻さない。推定は台帳と注記に残す。

## 8. 画像・検証の入口

最新の機械検査は138件（全体136＋白線の実GLB接地2）、型/ビルド/資産・全体予算成功。#36は追加前5視点/後9視点でブラウザエラーと資産失敗なし、仮fill置換と追加点字の実scene登録も確認。これは最後の実装時の結果で、引き継ぎ資料の作成時にモデルを変更/再検査した結果ではない。

#36の実GLBで、追加交通面と保護Core、DEMと仕上げ面、新旧点字の平面重複0㎡。**写真に対する誤差0ではない。** [geometry-check.json](../../evidence/c2-exterior/geometry-check.json)参照。旧Core仮fill範囲の約7,835㎡が追加道路に置き換わっている。

過去の各レポートのテスト数/予算/地形範囲/C数は当時の値。現在の数はGLB/manifestと最新テストで確認する。写真のカメラは多くが未校正。M027の既存フィット誤差も、新しく置いた全設備の位置精度や舗装色の精度を保証しない。

まず見る画像：

- [最新：109の写真・前・後](../../evidence/c2-nearby/boards/shibuya109.png)、[ヒカリエ](../../evidence/c2-nearby/boards/hikarie.png)、[マークシティ](../../evidence/c2-nearby/boards/mark-city.png)。規則外装の粗さと写真との差を確認。
- [109前の道路の前後](../../evidence/c2-exterior/boards/exterior_walk.png)、[駅周辺](../../evidence/c2-exterior/boards/terrain.png)、[初期昼](../../evidence/c2-exterior/boards/entry.png)、[初期夜](../../evidence/c2-exterior/boards/entry_night.png)。
- [駅前ビルの写真・前・後](../../evidence/c1-ekimae-b/boards/stream.png)、[駅連絡通路](../../evidence/c1-station-concourse/boards/references.png)、[銀座線夜](../../evidence/c1-ginza-canopy/boards/hall_night.png)。
- [ハチ公像](../../evidence/c2-hachiko/boards/photo-v1-after.png)、[周囲](../../evidence/c2-hachiko-surround/boards/photo-v1-after.png)、[顔の後続修正](../../evidence/c2-plaza-finish/boards/face.png)。
- 各`evidence/<対象>/before/after/v1*/boards/`と`capture_log.json`。v1や古い「after」を最新GLBの見た目と誤認しない。

必要な比較には`scripts/capture-street-fix.mjs`等の既存カメラを使う。既定品質の通常URLも撮影し、q=low/SwiftShaderの成功を通常品質の合格としない。撮影前build/sync、撮影中はassets/srcを固定、ブラウザは一つずつ。FPSはクラウド値で保証せず、オーナーPCの`?bench=auto`を節目で使う。

## 9. 未着手の計画と、Claudeへの依頼

[CODEX_COMPLETION_PLAN.md](CODEX_COMPLETION_PLAN.md)は**計画だけで実装していない**。歩行の安全化→接地→点字/路面→形の不足→見た目→表示/負荷→総合確認の順。今回Claudeが別の優先順で精査・実装してよく、Codexが並行してこの計画を実行する予定ではない。

Claudeには、(1) 最新ブランチで通常画面と比較画像を実際に見る、(2) 写真と食い違う主要な形・施設同定・広告/外装を特定する、(3) 一項目ずつ直して写真と同じカメラ前後で確認する、(4) 接地/重複/予算/ロードを回帰検査する、の順で進めてほしい。調査だけを長く続けず、最初の修正PRから見える改善を含める。

この資料で既存の実装を「完成」と認定していない。Claudeの判断で粗いデザインを修正し、未確認を残し、修正内容と根拠を更新してほしい。
