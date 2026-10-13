# 駅・マークシティ連絡通路 — B試作

way/355250634と、重なる橋brid_bd5e7fe1-da73-494d-83a9-2dfdb790bb3dを一つの資産へ置換。既存台帳と位置からの推定を含む。通常表示に追加し、Cの二件を除外した。

元の屋根の全頂点・絶対T.P.を保存。`viewer.json`のgroundElevationTPは15 m（移動0）。建物を地面の最小値に一括移動しない。橋との接続側x > -14 mだけ、下まで詰まった箱を柱・桁・開口へ置換し、西側の低層部は残した。新しい柱の足はC2a地面へ個別に合わせた。北面81点の地面はT.P.15.648〜15.888。床下面T.P.21 m、柱・窓・足場の配置と寸法は推定。

10月11日のJRホーム写真で構造の種類を参照。12月7日のCC0写真は窓・桁・柱の補助だけに使い、12月の重機・広告・工事状態を10月として入れていない。今回のモデルに写真テクスチャ・広告は追加していない。写真の帰属とSHA256は `source/refs/REFERENCE_REGISTER.csv`。

初版の窓枠約2.1 m間隔が粗いため、間隔だけ約1.15 mへ補正。初版はlayout.jsonのwindow_baysを24、最終版は44として再生成できる。床・屋根・開口・窓の高さは同時に変えていない。

## 再生成

```bash
source /workspace/setup-tools/core-env.sh
blender -b --python-exit-code 1 -t 4 -P assets/buildings/station-concourse/source/blender/build_station_concourse.py -- assets/buildings/station-concourse/source/data/parts.json assets/buildings/station-concourse/source/data/layout.json assets/ground/core/web/ground_core.glb assets/buildings/station-concourse/web
npm test
npm run build
npx vite preview --port 5192 --strictPort
VIEWS=station_concourse,overview,sw_island,night node scripts/capture-street-fix.mjs http://127.0.0.1:5192 evidence/c1-station-concourse/<run>
```

592三角形・7描画単位・38,484 bytes、B予算内。撮影中は資産・srcを変えず、ブラウザは一つずつ実行。`?context=nostation`は新しい通路も消す。

正確な同定、10月正面とのカメラ合わせ・寸法測量、開口・柱の位置、窓・外装の色、養生・足場の配置、夜の光量は未達。駅舎5棟はCのままで10月確認済みとは扱わない。結果は `docs/core/C1_STATION_CONCOURSE_REPORT.md`、比較板は `evidence/c1-station-concourse/boards/`。
