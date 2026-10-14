# モデル上の出入口への点字接続（推定）

元の164枚と補足108枚を保持し、地下鉄上屋6か所の「モデル上の開いた端」の前へ経路を追加。既存歩道だけで経路を探し、出入口の平面形・樹木・支柱・柵・小施設を避け、歩道に収まる直線へ整理。実際の2025年の誘導経路や階段方向・正確なバリアフリー経路として認定しない。

新しい166枚の面と突起を既存の点字区画・警告面・歩道境界で切り詰め、表面の重複を防ぐ。台板の表示オフセット2 mm、突起の上面7 mm。2 mmの目地を持つため、経路の検査は6 mm以内の横・縦の目地幅も考慮する。実際の書き出しでは歩道端への2 mm以内の補正は0件。

```sh
python assets/street/tactile-links/source/tools/plan.py
python assets/street/tactile-links/source/tools/prepare.py
blender -b --python-exit-code 1 -t 4 -P assets/street/tactile-links/source/blender/build.py -- assets/street/tactile-links/source/data/geometry.json assets/ground/core/web/ground_core.glb assets/street/tactile-links/web/tactile-links.glb assets/street/tactile-links/source/data/stats.json
```

PLATEAU 2025と元の横断歩道測定・2025年OSM（© OpenStreetMap contributors / ODbL-1.0）の入力を使用。既存の出入口の形・位置は変更しない。
