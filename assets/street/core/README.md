# Core 街路設備（C2b v2・仮）

**v2（2026-10-12、Claude Code）**：通常表示に、出入口 6（ガラス張りの箱）・樹木 6・歩行者用信号 10・車両用信号 4・街灯 3・標識 1・柵 220 m。
位置は OSM（出入口・樹木）、規則 R1〜R3（`source/tools/street_layout.py`）、Codex の写真投影（街灯・標識）。形は標準寸法の汎用品。
再生成は `docs/core/CODEX_C2B_REVIEW.md` §4、結果は `docs/core/C2B_FIX_REPORT.md`。台帳は `source/data/street_register_v2.csv`。
以下は PR #8（v1）の記録。`build_street.py` の引数は v2 で `street_layout.json` が加わった。


通常表示は2025-10-31のOSMにある出入口候補6件・樹木6件。出入口番号は5件だけ確認できた（A5a/A6a/A6b/A7a/A7b）。way/1335178869 は用途未確認の上屋候補であり、6か所すべてを地下鉄出入口として同定したわけではない。寸法・樹種・葉の形・地下の階段は確認済みではない。階段は書き出さない。

`?street=projected` は写真からの**仮配置**を追加する。街灯3基、うち1基に歩行者信号の試作、丸形標識の支柱1基（板2枚）、柵1区間。橙色と画面の注記で未確認を示す。車両信号の4個のOSMノードは支柱の位置ではないので、その座標へ支柱を置かない。根元が隠れた写真の支柱P05も書き出さない。

## 再生成（Blender 4.2.3 LTS）

```bash
source /workspace/setup-tools/core-env.sh
blender -b --python-exit-code 1 -t 4 -P assets/street/core/source/blender/build_street.py -- \
  assets/street/core/source/data/street_input.json assets/ground/core/web/ground_core.glb \
  assets/street/core/web/street_core.glb assets/street/core/source/data/street_stats.json
# 最後に leaves を追加すると、非採用の細密葉の比較案を再生成できる。既定は coarse。
blender -b --python-exit-code 1 -t 4 -P assets/street/core/source/blender/project_furniture.py -- \
  assets/street/core/source/data/photo_observations.json assets/ground/core/web/ground_core.glb \
  assets/street/core/source/data/photo_projections.json
blender -b --python-exit-code 1 -t 4 -P assets/street/core/source/blender/build_projected.py -- \
  assets/street/core/source/data/photo_projections.json assets/street/core/web/street_projected.glb \
  assets/street/core/web/projected.json
node scripts/street-manifest.mjs
npm run build
npx vite preview --port 5184 --strictPort
```

カメラを動かしたら観測画素・投影・GLBを再生成する。`calibration/stream-fixed-landmarks.json` から `scripts/solve-ref-camera.py fit` で現在の仮カメラを再計算できる。固定した2024年の位置と仮の屋根高さに依存している。制約のない解はRMS 3.2 pxでも高さ5882 mになったため棄却した。低いRMSだけでは位置の確認にならない。

`?street=off` / `?street=entrances` / 通常表示の順に一カテゴリずつ比較できる。`?street=projected&streetref=stream2025` は2025年1月の写真に合わせた仮カメラ。`?lamps=off` で実験のライトを消せる。ライトを点灯する実験のみ既定の路面発光を0へ戻す。通常表示には検証済みの街灯がないためC3aの暫定値0.5を残す。光量1800 cd・高さは未測定。ライトは3基、影なし。

地面を実際にレイキャストして高さを取得する。出入口の足元の床だけを歩行面へ追加し、屋根・葉を歩行面にしない。GLBは建物・地面から独立して読み込まれ、失敗しても他の資産を表示する。

## 出典・検証

- OSM: © OpenStreetMap contributors, ODbL 1.0。歴史クエリ・選択した応答は `source/data/osm_2025.json`。
- 写真: `source/refs/REFERENCE_REGISTER.csv` と保持したCommons API応答。CC0の2枚とCC BY-SA 4.0（Joli Rumi）の夜写真。原画像の色・内容は変更せず縮小版を保持し、参照だけに使用する。
- 葉・標識・上屋・支柱のメッシュは自作の手続き生成。写真をテクスチャとして使っていない。
- `furniture_register.csv`: 写真・画素・地面座標・状態・画素変動に対する感度。位置誤差の信頼区間ではない。別のカメラ前提では最大2.861 mの位置差が出た（`evidence/c2b/camera_sensitivity.json`）。
- `scripts/audit-street-sources.py` / `scripts/street-metrics.py` / `scripts/capture-street.mjs`、`docs/core/C2B_REPORT.md` と `evidence/c2b/`。
- 三角形・描画単位・容量は既存のB段階の予算内。クラウドのFPSは評価に使わない。
