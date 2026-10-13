# ハチ公像・石の台座（部分試作）
2025年7月13日の正面写真2枚（RuinDig/Yuki Uchida、CC BY 4.0）と11月1日の側面写真（Joli Rumi、CC BY-SA 4.0）から、座った犬、非対称の耳、首輪、前脚、後脚、尾、金属の基台、石の台座と銘板を自作。7月の選挙告知は10月の設備として採用しない。11月は形の補助資料で、10月状態の独立確認ではない。

位置はOSM node/597685675の履歴から2025年10月以前の最終版48（2025-06-08）を取得し、旧プロジェクトと同じ原点へ換算。東11.568 m・北-48.686 m。向きと寸法は推定。1.2×1.1 mの足元9点で既存歩道へ照会し、最低点T.P.15.439 mに接地、最大約3 cm埋める。写真からの実測値ではない。

色と風化は自作ノイズ、銘板は「忠犬ハチ公」をNoto Serif CJKで組版したもの。写真テクスチャはなし。実彫刻の顔・毛彫り・風化・字形の忠実な再現には達していない。周辺ベンチ・植え込み・案内板は別工程。通常表示に追加しHUDに注記、`hachiko=off`と`hachikourl=missing`で比較・障害を確認できる。既存の歩行地面は変更しない。

```bash
python assets/street/hachiko/source/tools/generate_surfaces.py
blender -b --python-exit-code 1 -t 4 -P assets/street/hachiko/source/blender/build_hachiko.py -- assets/street/hachiko/source/data/layout.json assets/ground/core/web/ground_core.glb assets/street/hachiko/web/hachiko.glb assets/street/hachiko/source/data/stats.json
python assets/street/hachiko/source/tools/write_manifest.py
```
Python numpy/PillowとNoto CJKフォントが必要。別の場所にあるフォントはgenerate_surfaces.pyの第1引数へ。出典・日時はsource/refs/SOURCES.json。
