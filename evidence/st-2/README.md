# ST-2交番：通常表示の前後比較

`before/` はPR82マージ後main `ecd30e7` 相当の通常建物一覧と保存原本の駅GLB。
`after/` は同じカメラ・既定品質のST-2。`boards/` は左が変更前、右が後。
前画像のQA差替えは駅本体を保存原本へ戻し、既存のbuildingsクエリで新交番だけを一覧から除く。
地面・BOX・ハチ公・plaza-kiosk・JR入口レイヤー等は切り替えない。通常afterはクエリで建物を限定しない。

全景・正面・斜め・足元の4カメラは `scripts/capture-street-fix.mjs` のst2_*。
初期の北側斜め案では既存樹木が交番を覆ったため、南側からの斜めへカメラだけを変更した。
既存の樹木・柵・舗装を動かして見やすくしていない。前後比較は最終カメラで統一する。

```sh
# PowerShell: $env:VIEWS='st2_whole,st2_front,st2_oblique,st2_feet'
node scripts/capture-street-fix.mjs http://127.0.0.1:5204 evidence/st-2/after
node scripts/check-st-2-browser.mjs http://127.0.0.1:5204 evidence/st-2/look
```

beforeの再現は `ST2_BASELINE=1` と、origin/mainのsrc/main.tsから得た元のbuildings一覧をEXTRAの
`buildings=...` に設定する。保存原本のSHAと対象外GLBの保持は `invariance.json` と実GLBテストで確認する。
撮影前にbuild/sync、撮影中は資産・srcを固定、ブラウザは順次実行する。

`look/` は通常昼・夜・昼復帰・1秒間隔の非停止画像・分類。看板は黄、上部窓代理は青、外壁と帯・支柱は赤。
下部は浅い枠と暗い奥面の推定表現。ガラス越しに内部を制作したものではない。
写真で確認した曲面帯・銀色庇・支柱と赤帯の関係を維持し、目視範囲で新たな二重表示・浮き・ちらつきを認めない。
公共高架下の既存通行部は残り、敷居と支柱下部は浮きを避けて地面へ軽く埋めた推定。

- `validation.txt`：標準全体テスト253成功＋既存PARCOの5秒timeout1件、そのファイルの20秒設定での16件成功、ビルド。
- `invariance.json`：対象外17GLB、地面・context・BOX・歩行処理・FPS実装の保持。
- `before/after/capture_log.json`：同一カメラ、資産とレイヤーの取得成功・エラー状態。
- `look/checks.json`：分類と昼夜UI、昼画像の復帰一致、時間差画像一致。

地理的取付点・寸法・曲率・下部枠・敷居・隠れた支柱継続・奥面は推定。左右関係と可視部品の種類が写真根拠。
原写真・切抜きは公開せず、モデル画像だけを収録。2025年10月現況、現地夜間光量、入室機能は検証対象外。
詳細は [ST-2報告](../../docs/core/ST_2_REPORT.md)。ST-2と第3段階全体の完了を区別する。
