# 円形路面蓋（部分試作）
M027（Taufik、CC0、2025-09-01）の円形の固い蓋を1個作る。排水・下水・通信などの用途は未確認。既存のカメラと道路へ3画素を投影し、中心と径約0.38mを推定。建物のカメラ誤差11.4pxは道路上の位置精度を保証しない。

蓋・枠・ひし形の凹凸と補修跡をBlenderで生成。模様・色・補修幅は近似、ロゴや排水孔を創作しない。写真はテクスチャにしない。既存12mm白線との重なり回避の16mmオフセット（凹凸最大17mm）は描画上の処置で、測定した段差ではない。歩行判定は従来の地面。通常表示に追加し、HUDに推定を注記。`drainage=off`で非表示、`drainageurl=missing`で失敗を確認できる。

```bash
node assets/street/drainage/source/tools/project_cover.mjs
blender -b --python-exit-code 1 -t 4 -P assets/street/drainage/source/blender/build_cover.py -- assets/street/drainage/source/data/layout.json assets/ground/core/web/ground_core.glb assets/street/drainage/web/drainage.glb assets/street/drainage/source/data/stats.json
python assets/street/drainage/source/tools/write_manifest.py
```

他の蓋・側溝・グレーチングは未実装。交差点全体の排水設備が完成したという意味ではない。
