# 開発環境（Codex などで同じ作業を再現するため）

これは、Claude Code のクラウド環境で実際に使っていた構成である（Linux x86_64、2026-10-12 時点）。

## 1. 必要なもの

| 道具 | 使っていた版 | 用途 |
|---|---|---|
| Node.js | 22.22.2（22.13 以上） | ビューアー（Vite + three.js）、テスト、撮影 |
| npm | 10.9.7 | `npm ci` |
| Python | 3.11.15 | データ処理と比較のツール |
| Python のパッケージ | numpy 2.4.6、Pillow 12.3.0、shapely 2.0.6、scipy 1.17.1 | PLATEAU の処理、地面の準備、比較、カメラ合わせ |
| Blender | **4.2.3 LTS**（Linux x64 の公式 tar 版。アドオンは不要） | 建物と地面の GLB の生成、見え方の計算 |
| Playwright | 1.56.1（Chromium build 1194） | 画面なしでの撮影 |
| Git | 普通の版 | — |

- npm の依存は `package.json` と `package-lock.json` で決まっている：three 0.186.1、vite 7.3.7、vitest 5.0.3、typescript 5.9.3、@gltf-transform/core 4.5.1。
- **MCP は使っていない。** Blender も、コマンドラインから画面なしで直接起動している。

## 2. セットアップ（Linux）

```bash
git clone https://github.com/kesusugar/shibuya-scene-2.git && cd shibuya-scene-2
npm ci
npx playwright install chromium          # すでにブラウザが入っている環境なら不要
pip install numpy pillow "shapely==2.0.6" scipy

# Blender 4.2.3（どこに置いてもよい。以下の例では BLENDER にパスを入れる）
curl -LO https://download.blender.org/release/Blender4.2/blender-4.2.3-linux-x64.tar.xz
tar xf blender-4.2.3-linux-x64.tar.xz
export BLENDER=$PWD/blender-4.2.3-linux-x64/blender
$BLENDER -b --version
```

- Windows では `CLAUDE.md` の手順でよい。Blender は 4.2.3 の Windows 版を入れる。

## 3. いつも使うコマンド

```bash
npm run dev            # sync-assets のあと vite を起動（http://127.0.0.1:5173）
npm run typecheck
npm test               # sync-assets のあと vitest
npx vite --port 5182 --strictPort --host 127.0.0.1   # 撮影用のサーバー

# Blender（画面なし。-- の後ろがスクリプトへの引数）
$BLENDER -b -P assets/ground/core/source/blender/build_ground.py -- \
  assets/ground/core/source/data/ground_input.json assets/ground/core/web/ground_core.glb assets/ground/core/source/data/ground_stats.json
```

### 画面なしでの撮影（見た目の確認用。FPS は無効）
- `node scripts/capture-core.mjs http://127.0.0.1:5181 evidence/c2a`：地面の前後比較。途中で止まっても続きから撮れる。
- `node scripts/capture-look.mjs http://127.0.0.1:5182 evidence/c3a/<名前> ["look=..."]`：写真のある 4 視点の通常画像と区分画像。
- `python3 scripts/look-metrics.py <dir> <dir>/metrics.json`：写真と画像の差を測る。
- Chromium は `--use-angle=swiftshader --enable-unsafe-swiftshader` で起動する。GPU がなくても描ける。

## 4. 外部のデータ（リポジトリには含めないもの）

| データ | 取得先 | 備考 |
|---|---|---|
| PLATEAU 2025 渋谷区（地域メッシュ 53393596 とその周辺） | `https://api.plateauview.mlit.go.jp/datacatalog/citygml/m:53393596` の一覧にある URL（bldg・tran・brid・frn・veg・dem、`codelists/`） | `tools/core/plateau_core.py` で、交差点の周り 320 m を JSON に抜き出す |
| 旧プロジェクトのデータ | `kesusugar/shibuya-scene` の `public/data/shibuya-scene-data.json` | 読み取りのみ。旧リポジトリは変更しない |
| 国土地理院のシームレス空中写真（ズーム 18） | `https://cyberjapandata.gsi.go.jp/xyz/seamlessphoto/18/{x}/{y}.jpg` | 横断歩道の測定にだけ使う。出典は「国土地理院」 |
| Wikimedia Commons の写真 | `Special:FilePath/<ファイル名>` | User-Agent を付け、4 秒以上の間隔を空ける。429 は待って再試行する |

## 5. フォルダの構成（要点）
- `assets/buildings/<id>/`：`source/`（生成スクリプト、データ、参考写真）、`web/`（GLB、`viewer.json`、発光の設定表）、`manifest.json`。
- `assets/ground/core/`：地面。生成の手順は README にある。
- `src/`：ビューアー。`world/`（建物、地面、見た目、照明）、`controls/`、`perf/`（予算、計測）。
- `tools/core/`：監査と台帳のツール。`scripts/`：撮影と比較のツール。
- `docs/core/`：監査、計画、報告、決定事項（`DECISIONS.md`）、引き継ぎ（`HANDOFF_CODEX.md`）。
- `evidence/`：比較画像と、その計測値。

## 6. つまずきやすい点
`HANDOFF_CODEX.md` の「4. 環境とつまずきやすい点」も見ること。特に次の 3 つ。
- 撮影中に `src/` を変更すると、vite が再読み込みして撮影が壊れる。
- 環境に GPU がないと FPS は測れない。FPS はオーナーの PC で `?bench=auto` を使って測る。
- three.js では、材質ごとの反射の強さは、その材質に環境マップが付いているときだけ効く（`look.ts` で対応済み）。
