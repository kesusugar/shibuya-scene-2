# ST-1 比較と受入記録

`before/` はPR80マージ後main `c33be62`、`after/` はST-1取込後。
全景・入口側正面・斜め・看板と柱の近景で同じカメラ、通常の建物一覧、既定品質を使う。
`boards/` は左が前・右が後。元の調査写真・切抜きは含めない。

```sh
VIEWS=st1_whole,st1_front,st1_oblique,st1_detail node scripts/capture-street-fix.mjs http://127.0.0.1:5204 evidence/st-1/after
node scripts/check-st-1-browser.mjs http://127.0.0.1:5204 evidence/st-1/look
```

PowerShellではVIEWSを `$env:VIEWS='st1_whole,st1_front,st1_oblique,st1_detail'` と設定する。
ビルド／同期後に撮影し、撮影中は変更しない。通常4画像は固定フレーム、look確認はレンダーを止めず、
1秒間隔の昼画像一致とUIの昼→夜→昼復帰を検査する。`look/` に通常昼・夜・復帰・分類画像を収録。
分類は看板=黄／柱外装=赤（壁）。詳細な全16プリミティブの分類は実アセットの回帰テストで確認。

- `validation.txt`：全体245テストとビルド、その後追加した接地テストを含むST-1の5テストと型検査。
- `invariance.json`：既存駅構造、QFRONT、BOX、ハチ公、地面の配信GLBがmainとバイト同一。
- `before/after/capture_log.json`：カメラ、資産の成功状態、全レイヤーのエラー状態。
- `source/st-1/delivery-verification.json`（駅北側資産）：ZIPの全ファイル一覧、CRCと原本manifest計35ファイルの照合数。

取付位置は推定。看板下の既存壁は残り、実写の入口開口・内部の完成を意味しない。
第3段階全体の完了、現地夜間の光量照合、オーナーPCのFPS合格とは区別する。
