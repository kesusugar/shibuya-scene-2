# 引き継ぎ（Claude Code → Codex）：Shibuya Scene 2.0 Core v1

> **2026-10-13 追記：C3a の比較・既定値反映・昼夜の比較画像・検証を完了。** 結果と未達は `C3A_REPORT.md`、画像は `evidence/c3a/boards/`。採用値は昼露出0.85、ガラス反射1.6、外壁反射0.5、夜の路面0.5（C2bで街灯を入れたら0に戻す）。次の実装対象はC2b。以下は2026-10-12の引き継ぎ時点の記録として残す。

- 2026-10-12 時点の状態と、次にやること。
- **まずこのファイルを読み、続けて `DECISIONS.md` と `C2A_REPORT.md` を読むこと。**

## 0. 守ること（オーナーの決まり）
### リポジトリ
- 旧リポジトリ `kesusugar/shibuya-scene` は**一切変更しない**（読み取りのみ）。
- 新リポジトリ `kesusugar/shibuya-scene-2` は Private。公開範囲を変える前に、オーナーへ報告する。
- 作業中のブランチに対して、`reset --hard`、`clean -fd`、`stash`、force-push はしない。
- 作業は `git worktree` で分ける。
- **西武 A 館の未コミットのファイル**（ブランチ `claude/g4-seibu-a`、`assets/buildings/seibu-a/`）は消さない。

### 素材とライセンス
- 流出した GTA V のソースは使わない。
- Street View はテクスチャに使わない。
- 写真はすべて、ライセンスとともに台帳に記録する。ライセンスがはっきりしない画像は公開しない。
- 2018 年の広告を 2025 年のものとして扱わない。広告は建物の形とは別の層にする。
- **再現する時点は 2025 年。駅前は 2025 年 10 月（東急東横店の撤去後）。**
- 2025 年の写真がない部分は、看板だけ最新のものにする。

### 確認と比較のしかた
- 比較は同じカメラ同士だけで行う。
- 1 回に変えるのは 1 つの項目だけ。
- 実装、資産と証拠、資料は、別々のコミットにする。
- AI の主観で「合格」にしない。差と未達の点は正直に書く。
- **FPS は節目にだけ、オーナーの PC で測る**（`?bench=auto`）。クラウドや画面なしの SwiftShader の FPS は無効。日々の作業では、`tests/budget.test.ts` の予算で管理する。

### コミットと報告
- 報告は日本語で、画像を付ける。
- 人や車は、中心部の静的な街並みが完成してから入れる。

## 1. 完了したこと（`main` にマージ済み）

| PR | 内容 |
|---|---|
| #3 | MAGNET v2 |
| #4 | Gate C0 の監査、自己レビュー、補足監査 |
| #5 | C2a：地面と高さの基準 |

### PR #4（Gate C0 と補足監査）
- `docs/core/` 一式：台帳（`ASSET_REGISTER_V2.csv`、`STRUCTURE_REGISTER.csv`、`REFERENCE_REGISTER.csv` に `era_class` の欄）。
- 7 視点の見え方：地上 5 視点と、高所の X01（REF-A）・X02（REF-B）。

### PR #5（C2a：地面と高さの基準）
- ブラウザの Y = T.P. − 15.000 m。
- 建物は `viewer.json` の `groundElevationTP` で上下に動かす（QFRONT +0.202 m、MAGNET と栄楽ビル −0.093 m）。
- 地面は `assets/ground/core/`：PLATEAU LOD3 の道路、縁石、航空写真で幅を測った横断歩道。

## 2. 作業中：C3a WebGL の共通品質（ブランチ `claude/core-c3a-look`）
- 作業ツリーは `/home/user/ss2-look`。他の環境では、`origin/claude/core-c3a-look` を取得して始めればよい。

### できているもの（すべてこのブランチにコミット済み。未コミットの WIP はない）
- **材質の区分**（`src/world/look.ts`）
  - `classify()`：glass / sign / interior / wall / road / sidewalk / kerb / marking / fill
  - `?pass=class`：区分ごとの単色で描く表示
- **見た目の調整を 1 か所に集めたもの**（`applyLook()`、`LookParams`）
  - 項目：昼と夜の露出、ガラスと外壁の反射の強さ、車道と歩道の色、夜の路面の明るさ、夜の看板の倍率。
  - 試すときは `?look=key:value,...` で値を変えられる。
  - 不具合を直した：three.js は、材質に環境マップが直接付いていないと材質ごとの反射の強さを無視する。そのため、ガラスと外壁には `scene.environment` を付けている。
- **写真との比較**
  - `scripts/capture-look.mjs`：写真のある 4 視点の通常画像と区分画像を撮る（`VIEWS`、`PASSES` の環境変数で絞れる）。
  - `scripts/look-metrics.py`：区分ごとに写真と画像の平均の色を比べる（CIE L\*a\*b\*）。撮影位置が合っている M027・Q032 は重み 1、ずれのある REF-A・REF-B は 0.5。
  - `scripts/look-sweep.sh`、`look-sweep2.sh`：1 回に 1 項目だけ変えて比べる。
- **性能の予算**（`src/perf/budget.ts`、`tests/budget.test.ts`）：A・B・C の段階ごとと、場面全体の予算。今は三角形 21.3 万、描画の単位 128、容量 10 MB。
- **`?bench=auto`**：URL 1 つで 7 視点を自動で測り、結果の JSON を表示してコピーする。
- **資料**：`DECISIONS.md`（オーナーの決定）、`OWNER_PC_MEASUREMENT.md`（`?bench=auto` を追記）。

### 比較の結果（`evidence/c3a/sweep/*/metrics.json`）
- 数値は、区分ごとの写真との明るさの差（|ΔL\*|）の平均。

| 案 | 内容 | 昼 | 合っている 2 視点 | 夜 | 判断 |
|---|---|---|---|---|---|
| base | 今のまま | 9.73 | 3.07 | 19.5 | — |
| **E1** | 昼の露出 0.85 | **8.78** | **2.58** | — | **採用する** |
| E2 | 昼の露出 0.92 | 9.13 | 2.67 | — | |
| R1 | 車道 0.03 | 9.91 | 3.70 | — | 悪化。0.045 のまま |
| R2 | 車道 0.07 | 11.62 | 4.92 | — | 悪化。0.045 のまま |
| S1 | 歩道 0.18 | — | — | — | REF-A の歩道は写真の別の物が混ざるため判断に使えない。0.30 のまま |
| N1 | 夜の路面 1.5 | — | — | 31.1 | 明るすぎ（車道 +13、歩道 +49） |
| N2 | 夜の路面 4 | — | — | 45.8 | さらに明るすぎ |
| G1 | ガラスの反射 0.5 | 9.80 | 3.15 | — | ガラスは M027 で暗すぎ、Q032 では改善。全体ではわずかに悪化 |
| K1 | 夜の看板 0.5 | — | — | — | 夜の写真に看板の区分が十分写らず、判断できない。1.0 のまま |

- 引き継ぎの時点で、G2・W1・N3（夜の路面 0.5）・N4（夜の路面 0.8）を撮影中だった。

### 次にやること（順番どおり）
1. **残りの案の結果を見る**：`evidence/c3a/sweep/{G2,W1,N3,N4}/metrics.json`。
   - 結果がない場合は、`sh scripts/look-sweep2.sh http://127.0.0.1:5182 evidence/c3a/sweep` を、開発サーバーを動かした状態で実行する。
2. **採用する値を `LOOK_DEFAULT` に入れる**
   - 昼の露出は 0.85（E1）。
   - 夜の路面は、N3 と N4 のうち夜の差の小さい方。
   - ガラスと外壁の反射は、昼の差の平均（合っている 2 視点を優先）が下がる場合だけ変える。
   - 案を組み合わせたら、すべての視点で撮り直して `metrics.json` を作り、基準（base）より良くなったことを確かめる。
3. **前後の比較画像を作る**：写真、前、後の 3 枚を並べた画像を、昼と夜の両方で `evidence/c3a/boards/` に置く。
4. **テスト**：`npm run typecheck && npm test`。今は 30 件と、ここで追加した look 6 件・budget 3 件がある。
5. **コミット**：実装、証拠、資料を分ける。`docs/core/C3A_REPORT.md` を作る（下の未達の点を正直に書く）。push して PR を作る。
6. **オーナーへの日本語の報告**：画像を付ける。`?bench=auto` は、節目に頼むだけでよい。

### C3a の未達の点（報告に書くこと）
- REF-A と REF-B のカメラは、旧プロジェクトで写真から求めたもので、2.0 の模型とは 20〜40 px ずれている。
  - `scripts/solve-ref-camera.py`（横断歩道の縞の端を目印にする）は作りかけで、まだ使えない。
  - 斜めの横断歩道は、縞が中央の島で切れるため、端の目印が不安定。
  - 解決策：建物の屋根の角も目印に加えて解き直す。
- 夜の比較は REF-B の 1 枚だけ。街灯がまだないので、夜の路面の明るさは**仮の値**（C2b で街灯を入れたら 0 に戻す）。
- 看板の明るさは、比べられる写真がなく未調整。

## 3. その後の予定（オーナーが採用した順序）
1. **C2b（街路設備）**
   - 信号、街灯、地下鉄の出入口 6 か所、樹木、標識、ガードレール。
   - PLATEAU の都市設備は Core の範囲にないので、OSM と写真から作る（`docs/core/STRUCTURE_REGISTER.csv`）。
2. **建物の制作（A・B・C の段階）**
   - 優先度は、見え方（`ASSET_REGISTER_V2.csv`、7 視点）に、写真の入手しやすさ（`coverage_v2/commons_survey_summary.json`）と制作の手間を加えて決め直す。
   - 第一候補は、センター街入口の西側の街区（way/136690966、平和クワトロ、センター 244）、渋谷駅前ビル、駅側（JR の駅舎は PLATEAU のみの 3 棟、連絡通路、山手線の高架）。駅側は 2025 年 10 月の写真で形を確かめる。
   - 建物 1 つにつき 1 フォルダ（`assets/buildings/<id>/`）。中身は `source/`、`web/*.glb`、`viewer.json`（`groundElevationTP` は `assets/ground/core/source/blender/ground_anchor.py` で測る）、`manifest.json`、README。
   - MAGNET の生成スクリプト（`assets/buildings/magnet/source/blender/build_magnet.py`、`matlib.py`）が手本になる。
   - 建物の追加のたびに、`tests/budget.test.ts` の `ASSET_LEVEL` に段階を登録する。
3. 西武 A 館を再開する：坂で最大 2.5 m 埋まるので、1 階を坂に合わせる。
4. 周辺へ広げる。最後に NPC、車、ゲームの仕組み。

## 4. 環境とつまずきやすい点
- **Blender 4.2.3**：作業用ディレクトリ（scratchpad）の `blender/blender-4.2.3-linux-x64/blender` にあった。新しい環境では入れ直す必要がある。
- **PLATEAU の元データ**：`https://api.plateauview.mlit.go.jp/datacatalog/citygml/m:53393596` の一覧から、bldg・tran・brid・frn・veg・dem・コード表を取得する。抽出は `tools/core/plateau_core.py`。
- **画面なしの撮影**：Playwright と SwiftShader（`--use-angle=swiftshader`）。1 枚に 30〜60 秒かかる。
- **開発サーバーの再読み込み**：撮影中に `src/` を書き換えると、vite がページを再読み込みして撮影が壊れる。撮影中は `src/` を触らない。
- **プロセスの停止**：`pkill -f <パターン>` は、自分のシェルのコマンドにも一致して自分を落とす。`ps aux | grep "[x]yz"` で PID を調べてから `kill` する。
- **Wikimedia Commons**：HTTP 429 が出やすい。User-Agent を付け、4 秒以上の間隔を空け、指数的に待ってから再試行する。429 を「写真がない」と扱わない。
- **sync-assets**：`npm test` は `public/buildings` と `public/ground` を作り直す。動いている vite は、再起動が必要になることがある。
- **作業ツリーの node_modules**：作業ツリーでは、`node_modules` をメインの作業ディレクトリへのシンボリックリンクにしていた。`.gitignore` の `node_modules/` は、シンボリックリンクには効かない。コミットのときは `git add` にパスを明示する。
