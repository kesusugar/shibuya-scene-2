# 広場の低層施設（売店候補）

way/155538676のPLATEAU壁・屋根を保持し、店舗の窓と桟・空の店舗枠を追加。元台帳の売店候補との用途の対応は未確認で、交番と断定しない。2025年の高所写真は交差点の補助資料で、この建物の正面・広告・用途・窓割りを独立して同定したとは扱わない。元の屋根の頂点を2 mm以内で照合し、Cの同じsource_idを除外。歩道へ54点を照会して下端を補完。広告・施設名や点灯を創作しない。

```sh
blender -b --python-exit-code 1 -t 4 -P assets/buildings/plaza-kiosk/source/blender/build.py -- assets/buildings/plaza-kiosk/source/data/plateau.json assets/buildings/plaza-kiosk/source/data/layout.json assets/ground/core/web/ground_core.glb assets/buildings/plaza-kiosk/web
```
