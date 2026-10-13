# ハチ公周辺の敷石
2025年7月の写真に見える灰色の小さな方形敷石を自作アトラスで追加。0.30 mの目地付き正方形を参考寸法とし、10.4×7 mの推定区画を元の歩道三角形で切り抜く。地面は書き換えず、1 mmの描画オフセットを使う。歩行高さ・道路・縁石・白線・既存舗装は保持。寸法・方向・範囲は未測量で、10月の確認ではない。

`python source/tools/make_paving.py source/data/layout.json` と `blender -b -P source/blender/build_paving.py -- source/data/layout.json <ground.glb> web/plaza-finish.glb source/data/stats.json`。写真はstreet/hachiko/source/refs/july094.jpgとjuly095.jpg、RuinDig/Yuki Uchida、2025-07-13、CC BY 4.0。写真テクスチャなし。
