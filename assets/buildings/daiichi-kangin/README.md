# 渋谷第一勧銀共同ビル — 交差点側の個別B試作

way/114755219、PLATEAU bldg_5e891186-4803-48a0-9664-284f212881ac。初期画面の左側に見えるため、QFRONT等に隠れるセンター244・クワトロより先行した。元の全表面と屋根を保持し、共通窓柄を個別のガラス・窓枠・赤い腰壁・店舗面・看板筐体へ置換。通常ロードし、同じIDのCを一度だけ除く。

2025年1月31日のStream写真と2月7日の高所写真（Syced、CC0）で形の種類を確認。窓数、階高、店舗面、看板筐体の寸法・位置は推定。2025年10月の独立照合や実測ではない。既存写真はsource/refs/REFERENCE_REGISTER.csvの相対パスで参照し、再加工していない。

広告内容の切り貼り・個別テナントの文字は後工程。看板は支持物・筐体だけで、新しい広告テクスチャや日付不明の文字を貼っていない。黒い看板面が実写真と異なる点を未達に残す。将来の広告画像は別GLBレイヤーで追加する。

座標は元のcontext入力のT.P.−15。viewer.jsonはgroundElevationTP=15として二度引きを防ぐ。元の屋根と全体位置は移動0、屋根差0 m。南・東正面62点中49点でC2a地面に当たり、T.P.15.140〜16.135 m。外側の足元に地面へつながるスカートだけを追加した。13点は範囲外で、全周・入口の実段差や勾配は未確認。夜は店舗の自発光のみで、実配光は未調整。

## 再生成

```bash
source /workspace/setup-tools/core-env.sh
blender -b --python-exit-code 1 -t 4 -P assets/buildings/daiichi-kangin/source/blender/build_daiichi.py -- assets/buildings/daiichi-kangin/source/data/plateau.json assets/buildings/daiichi-kangin/source/data/layout.json assets/ground/core/web/ground_core.glb assets/buildings/daiichi-kangin/web
```

context_input.jsonの対象1棟だけを独立資産へ移した。将来全体を再抽出するときはselect_context.pyのOWN_ASSETSが同じIDを除く。両方の入力を更新し、build_context.pyで再生成する。

国土交通省Project PLATEAU「渋谷区2025年度3D都市モデル」を加工。出典 https://www.mlit.go.jp/plateau/ 、利用条件 https://www.mlit.go.jp/plateau/site-policy/ 。写真は参考のみで、生成モデルに写真テクスチャはない。

初版と最終版の設定はevidence/c1-daiichi-kangin/{first,after}/layout.jsonに保存。ガラス色だけを変更した。初版を再生成する場合はfirst/layout.jsonを/tmp等へコピーし、別の出力先で上記スクリプトを実行する（stats.jsonは渡したlayoutの隣へ保存される）。
