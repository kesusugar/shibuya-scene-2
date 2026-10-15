# ハチ公植栽区画：石縁前面と埋込み灯器の交換用モジュール

状態：**モデル制作・単体検証済み、街への組込み待ち**。このPRは追加ファイルのみ。既存 `assets/street/hachiko-surround/web/hachiko-surround.glb`、像、植栽、銀色レール、地面、歩行・FPSコードを変更しない。

## 制作した範囲

縦長の石板、分割された笠石、石壁を実際に切り欠いた開口、奥まった灯器枠・拡散面・横桟。単なる黒い矩形の貼付けではない。灯器は非発光。植栽区画全周・隅角・裏側・レール・植物は本品に含まれない。

2025年7月13日の近景で確認できる形状を手掛かりに、2026年8月8日の実写で石縁・銀色レール・下部の横長灯器が存続することを補助確認した。後者では人に隠れる範囲が多く、2026年10月15日現在の全体形状を実測・確認したという意味ではない。撤去された小庭園と残存する樹木区画を混同しない。

## ファイル

- hachiko_stone_front_module.glb：テクスチャ内蔵、メートル、底面中央原点。Blender正面+Y、glTF正面-Z。
- hachiko_stone_front_module.blend：Blender 4.2.3編集用、合成石肌画像をパック。
- synthetic_granite.png：固定乱数から作った自作石肌。写真画素は使用しない。
- source/regenerate.py：外部素材不要の再生成Python。
- source/render.py：GLBを読み直して正面・側面・斜めを撮影。
- source/test_model.py：原点・寸法・メッシュ・開口・非発光などを確認。
- placement.json：既存の相対配置を保持するための組込み参考値。配置自体は推定のまま。
- SOURCES.md：出典、年代、権利、推定箇所。
- evidence/：実GLBの確認画像と検証結果。

## 再生成

リポジトリルートから、任意の出力フォルダへ実行できる。

    blender -b --python-exit-code 1 -t 4 -P assets/street/props/incoming/hachiko_stone_front_module/source/regenerate.py -- /tmp/hachiko-module
    blender -b --python-exit-code 1 -t 4 -P assets/street/props/incoming/hachiko_stone_front_module/source/render.py -- /tmp/hachiko-module
    blender -b --python-exit-code 1 -t 4 -P assets/street/props/incoming/hachiko_stone_front_module/source/test_model.py -- /tmp/hachiko-module

Blenderは4.2.3 LTS。外部Pythonパッケージは不要（Blender同梱numpyを使用）。正面・側面・斜め画像は実際のGLBを描画したもので、AI生成イメージではない。

## Codexへの組込み手順

1. 最新mainと並行変更を確認。基準mainは `2c9b8327df024fa8e2fd1189c79dae1f6f9c0825`（PR #58マージ後）。
2. 本モジュールを旧石壁へ単純重ね置きしない。凹部を塞ぐ旧前面の石と、連続した前笠石、旧小型灯器だけを取り除いて交換する。
3. 元の `street_surround_stone` は石板・裏壁・戻り壁も結合したメッシュ。ノード丸ごとの削除は禁止。生成元で `wall_<segment>` / `cap_<segment>` / `wall_light_<segment>` に当たる前面部位のみ差替える。
4. placement.jsonの左右中心・軸・接地標高を保持。後ろの石、土、自然石、植物、レール、記念石板、像、地面はそのまま。新しい物理衝突や歩行面は追加しない。
5. 完全な既存GLBを取得できる環境で、対象外三角形・材質と接地を比較し、既存surroundテスト・予算・同一カメラ全景を確認してから通常表示へ反映する。

この制作環境では現在mainの1MB超バイナリを取得できず、現行生成スクリプトと保存済み接地点からの再生成は再現したが、生成GLBのGitハッシュはmainと不一致だった。そのため本PRではランタイム全体のGLBを置き換えない。ソース再生成同士の対象外形状一致を、現在mainバイナリとの一致と取り違えない。

街全体・ブラウザ表示・FPSはこの単体検証の対象外。全周復元の完了でもない。
