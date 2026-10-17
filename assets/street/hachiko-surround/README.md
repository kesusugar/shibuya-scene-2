# ハチ公像周辺の石縁・レール・植栽（部分試作）

## 現行：PR88後のv002統合

通常配信は `web/hachiko-surround.glb`（旧soil/rockだけ）、`web/shrubs.glb`（dot低木6株・world配置）、`web/seating.glb`（dot current_pair・local配置）の3点。像rootのyaw−65°と設備の35°は別。全surround比較版、左右別座面、曲線・舗装候補を重ねて読み込まない。

[統合・取付・検証記録](../../../docs/core/HACHIKO_FINAL_FIT_20261017.md)を優先。原本・blend・Python・出典・ライセンス・候補資料は `source/deliveries/` に保全。配信用座面だけテクスチャを512pxへ縮小、低木は配布GLBと同一バイト。旧PR88は `source/legacy/hachiko-surround-pr88.glb`。再現はrepo rootでPillow環境の`PYTHON`を指定し `node scripts/prepare-surround-runtime.mjs`。旧 `source/blender/build_surround.py` は履歴再現用で、現行webへ直接上書きしない。

以下は旧制作記録。旧針葉・球状コア、旧石縁・レールは現行では置換済み。低木根元の自然石は保持対象。

## 旧制作記録
2026-10-17 の一括取り込みでは、旧 `stone_panel` と `unread_inscription` の生成だけを停止し、`street/hachiko-memorial` に置換した。左右の石縁、レール、植栽は維持する。配置と寸法は現地実測ではなく、採用済み像に対する従来の相対配置から推定した。
2025-07-13の正面写真094/095（RuinDig/Yuki Uchida、CC BY 4.0）で確認できる、像の両側の石縁、傾斜した銀色レールと支持金具、低木・自然石、右側の石製掲示板を自作。標準の板座面ベンチへ置換しない。レールの用途・正確な呼称は未確認。

配置はOSM位置を使った既存のハチ公像を基準にした相対推定。像と同じ35度の軸を使うが、軸自体も未確認。実測の位置・幅・奥行・高さ・種・10月の状態ではない。左・右それぞれ2.35 mの局所区間、中央は像と通行の空間を残す。完全な植栽区画の輪郭や連続したベンチを復元したとは扱わない。

足元は既存歩道の9点ずつ、石板6点を照会し、各設備を最低点へ接地。点字との離隔を検証。既存の像・地面・樹木等は変更しない。植栽は低い枝と針状の葉束（遠目の読みやすさを保つ簡略表現で、実寸の葉1枚ではない）、自作の自然石。既存のOSM樹木の複製はなし。石縁の目地、金属管、支持、下部照明の筐体を制作。文字・地図・光量は不明なので石板は文字なし、照明は非発光。写真テクスチャはなし。

通常表示の独立street/hachiko-surround資産。`surround=off`で比較、`surroundurl=missing`で読み込み障害を検査。歩行地面は元の地面で、植栽へ衝突する専用の移動制限はまだ追加していない。

```bash
blender -b --python-exit-code 1 -t 4 -P assets/street/hachiko-surround/source/blender/build_surround.py -- assets/street/hachiko-surround/source/data/layout.json assets/ground/core/web/ground_core.glb assets/street/hachiko-surround/web/hachiko-surround.glb assets/street/hachiko-surround/source/data/stats.json
python assets/street/hachiko-surround/source/tools/write_manifest.py
```

## 区画の裏面の追記

土の面の奥が開いた初版へ、元の段取りと寸法に合わせた背面の石の小口と笠石を追加。像・前面・レール・低木の配置は保持。背面の実際の区画外形は写真で独立して測ったものではなく、区画を閉じる推定。実GLBの背面への水平の光線で、左右両区間の石壁があることを確認する。
