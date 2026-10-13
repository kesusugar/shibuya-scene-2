# 横断歩道アプローチの補足

元の164枚を別資産として保持し、Core地面にある残り14横断歩道へ局所アプローチを生成。28端点中16か所で108枚（警告と誘導）が歩道に収まった。12端点は完全な警告面を配置できず、stats.jsonに記録して追加しない。道路や地形補填へ黄色の面を置かない。

9点の台板確認だけでは歩道の微小な隙間を見落としたため、突起・線の生成予定頂点も歩道へ照会し、柵との離隔12 cmも確認してから配置を決める。元の点字面との平面重複は0㎡。形・位置・経路・2025年10月の全配置は推定。2025年2月の形の参考は元のtactile資産の出典とC2_TACTILE_REPORT.md参照。

```sh
blender -b --python-exit-code 1 -t 4 -P assets/street/tactile-extra/source/blender/build.py -- assets/street/tactile-extra/source/data/layout.json assets/ground/core/source/data/crosswalks_measured.json assets/street/core/source/data/street_input.json assets/ground/core/web/ground_core.glb assets/street/tactile-extra/web/tactile-extra.glb assets/street/tactile-extra/source/data/stats.json
```

PLATEAU 2025と元の横断歩道測定・2025年OSM（© OpenStreetMap contributors / ODbL-1.0）の入力を使用。座標の独立した測量ではない。
