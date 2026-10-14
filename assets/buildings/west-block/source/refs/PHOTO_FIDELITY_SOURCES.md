# 写真と利用範囲

## WB01 / 制作・広告レイヤーの基準
- 写真: [Shibuya crossing, seen from Shibuya Stream](https://commons.wikimedia.org/wiki/File:Shibuya_crossing,_seen_from_Shibuya_Stream.jpg)
- 著者: Syced。撮影: 2025-01-31。写真ライセンス: CC0。
- 原寸: 3072 × 4080 px。
- 原画像: https://upload.wikimedia.org/wikipedia/commons/d/de/Shibuya_crossing%2C_seen_from_Shibuya_Stream.jpg
- SHA-256: `0b5cec75608be664a9f2e4ab08b906a245d3f00ce0e4d556fcc8b513579bc656`
- 本改訂では原寸を確認し、従来の誤った薬局・飲食店・DMM・西村・書店の切り出しを修正した。DMM/書店は二つの平面、楽天は64本の帯で曲面境界を展開。広告の文字は生成していない。
- `data/fullres_texture_sources.json` は900×1195座標系へ換算した全切り出し範囲、`data/rakuten_boundary_landmarks.json` は原寸の曲面境界を記録。原寸四隅の再読値は `tools/extract_fullres.py` の native 辞書にもある。
- カーテン用の広告を含まない建築面だけ、低周波の焼き込み照明を除去した。細かい襞は写真由来だが、同じカーテン試料を他階にも再利用しているため、各階を実測した再現ではない。広告と比較用写真にはこの補正を行っていない。

## WB02 / 建築種類の別日確認のみ
- 写真: [Shibuya crossing (12214)](https://commons.wikimedia.org/wiki/File:Shibuya_crossing_(12214).jpg)
- 著者: Syced。撮影: 2025-02-07。写真ライセンス: CC0。
- 原寸: 4080 × 3072 px。
- 原画像: https://upload.wikimedia.org/wikipedia/commons/7/75/Shibuya_crossing_%2812214%29.jpg
- SHA-256: `a0fe5f57da98657907c4fd915eda4ccf991185aa25a40aea76cf2cb1ad9a7ab4`
- 四段のカーテン窓、左の深い開口、幅広のタイル壁、庇、看板二面構成、曲面画面を確認。2月の広告は1月レイヤーへ混ぜていない。

11月資料の広告を使用していない。Street View・生成AIの画像を使用していない。CC0は写真著作者によるライセンスであり、写り込んだブランド・商標等の権利を別途譲渡する意味ではない。
