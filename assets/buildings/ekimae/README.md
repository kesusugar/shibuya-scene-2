# 渋谷駅前ビル — B段階

way/60739635 / PLATEAU bldg_6abf2261-478c-437a-93f4-8ba23d7b1cad。元の屋根・裏側を残し、角の斜めの壁2面を丸い角へ置換。窓、赤い窓枠、明るい水平部材、黄色い低層の店とカフェ、庇、屋上ビジョンの支持物を制作した。通常表示に追加し、同じIDのCを除外した。駅舎・連絡通路とは別の建物。

`ekimae.glb`は建物の形と支持物、`signs-2025-11.glb`は11月の広告・店舗の写真画像。Joli Rumi / CC BY-SA 4.0。帰属・改変・継承ライセンスは `source/textures/LICENSE.md`。2月のYakult広告は混ぜていない。看板の色のテクスチャを夜の発光にも使う。

元のPLATEAU面は `source/data/plateau.json`、写真の四隅・推定・補正の根拠は `facades.json`、地面の82点と生成結果は `stats.json`。T.P.15.290へアンカーし、元の地面15.240から屋根までの差は+0.050 m。まず角を作り、初版の同じカメラで不足した東側正面を一項目として補正した。

階高、窓割り、入口、看板・ビジョンの寸法は推定。HiTの左側は写真外に切れ、アイシティ・ロクシタンは不鮮明。画像の残る遠近、曲面と平面への文字の重複、店の用途、裏側、夜の明るさは未達。B資産は6,640三角形・18描画単位・1,736,204 bytes。

## 再生成

```bash
source /workspace/setup-tools/core-env.sh
blender -b --python-exit-code 1 -t 4 -P assets/buildings/ekimae/source/blender/build_ekimae.py -- assets/buildings/ekimae/source/data/plateau.json assets/buildings/ekimae/source/data/facades.json assets/ground/core/web/ground_core.glb assets/buildings/ekimae/web
npm test
npm run build
npx vite preview --port 5191 --strictPort
VIEWS=stream,hachiko,night node scripts/capture-street-fix.mjs http://127.0.0.1:5191 evidence/c1-ekimae-b/<run>
```

撮影前に同期・ビルドを済ませ、撮影中は資産・srcを変えず、ブラウザは一つずつ実行する。画像は元写真の記録した四隅をPILの透視変換で抽出したもの。写真のライセンスとSHA256は `source/refs/REFERENCE_REGISTER.csv`。

結果は `docs/core/C1_EKIMAE_B_REPORT.md`、比較板は `evidence/c1-ekimae-b/boards/`。写真品質の完成とは扱わない。
