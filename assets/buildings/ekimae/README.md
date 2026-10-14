# 渋谷駅前ビル — B段階・写真に基づく再構成

現行版（2026-10-14）：23,730三角形・27描画単位・2,088,436 bytes。Samsung画面はメーカー公表21.6×16.32mに整合。編集用は `source/blender/ekimae-fidelity.blend`。出典・未達・再生成は下の「写真に基づく外装再構成」と `C1_EKIMAE_FIDELITY_REPORT.md` を参照。

## 旧 B 初版の記録（以下の数値・配置説明は旧版）

way/60739635 / PLATEAU bldg_6abf2261-478c-437a-93f4-8ba23d7b1cad。元の屋根・裏側を残し、角の斜めの壁2面を丸い角へ置換。窓、赤い窓枠、明るい水平部材、黄色い低層の店とカフェ、庇、屋上ビジョンの支持物を制作した。通常表示に追加し、同じIDのCを除外した。駅舎・連絡通路とは別の建物。

`ekimae.glb`は建物の形と支持物、`signs-2025-11.glb`は11月の広告・店舗の写真画像。Joli Rumi / CC BY-SA 4.0。帰属・改変・継承ライセンスは `source/textures/LICENSE.md`。2月のYakult広告は混ぜていない。看板の色のテクスチャを夜の発光にも使う。

元のPLATEAU面は `source/data/plateau.json`、写真の四隅・推定・補正の根拠は `facades.json`、地面の82点と生成結果は `stats.json`。T.P.15.290へアンカーし、元の地面15.240から屋根までの差は+0.050 m。まず角を作り、初版の同じカメラで不足した東側正面を一項目として補正した。

階高、窓割り、入口、看板・ビジョンの寸法は推定。HiTの左側は写真外に切れ、アイシティ・ロクシタンは不鮮明。画像の残る遠近、曲面と平面への文字の重複、店の用途、裏側、夜の明るさは未達。B資産は6,640三角形・18描画単位・1,736,204 bytes。

## 共通の再生成・全体試験の手順

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


## 2026-10-14 写真に基づく外装再構成

短い北面と長い東面への店舗・画面の割り付けを修正し、カフェ、窓枠、入口、装飾植栽、支持鉄骨を追加。Samsung はメーカー公表21.6×16.32m。隣接 HiT は別物で、写真にない部分は暗い無地。詳細・未達・出典は `docs/core/C1_EKIMAE_FIDELITY_REPORT.md`。

今回の編集用ファイルは `source/blender/ekimae-fidelity.blend`（Blender 4.2.3、メートル単位、画像パック済み）。`ekimae-uv.blend` は前の UV 修正版を残した履歴。建物の既存地理座標とT.P.15.29mを保ち、原点を動かしていない。

このフォルダでの再生成：
```bash
BLENDER=/path/to/blender-4.2.3-linux-x64/blender
$BLENDER -b --python-exit-code 1 -t 4 -P source/blender/build_ekimae.py -- source/data/plateau.json source/data/facades.json ../../ground/core/web/ground_core.glb web
```

既存の地面 GLB がない環境では、明示して保存済み82点を再使用できる（新しい照会ではない）：
```bash
$BLENDER -b --python-exit-code 1 -t 4 -P source/blender/build_ekimae.py -- source/data/plateau.json source/data/facades.json unused web --recorded-ground
```

元画像からの再切り出し（モデル再生成自体には不要）：
```bash
python source/blender/recrop_ek01.py /path/to/EK01-full.jpg
```
Pillow、NumPy が必要。4032×2268 の元画像は SOURCES.json の EK01 URL/ハッシュで照合する。画像のない部分を生成しない。

正面・側面の検証画像：リポジトリルートと出力パスを指定し、`source/blender/render_ekimae.py -- REPO_ROOT output.png front`（または `side`）を Blender で実行。


## 看板の向き・階境界の修正

現行の飲食店看板は全3階を通した2面を先に透視補正し、同じ縦の窓枠を共通U座標へ揃え、その後にY方向だけで階境界を整える。各階を独立にずらす方式は撤回した。詳細は `docs/core/C1_EKIMAE_SIGN_ALIGNMENT_REPORT.md`、拡大比較は `evidence/c1-ekimae-sign-alignment/comparison.jpg`。初期の全体比較も現在のモデルで更新済み。
