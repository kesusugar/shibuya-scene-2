# JR入口の浅い開口：比較・検証

変更前はPR81マージ後main `a906f1b` の `../st-1/after/` を再利用。
通常表示・既定品質・カメラ・看板と柱のGLB／設定は同一。画像SHAは `invariance.json` に記録する。
`after/` は局所開口を追加した同じ4カメラ、`boards/` は左がPR81・右が今回。
全景・正面・近景で看板下の壁が開口に替わり、中央柱と周囲の構造は保持される。
PR81の斜めカメラは手前の既存建物で入口下部が隠れるため、これだけで奥行き確認済みとは扱わない。

`oblique-clear/` は遮蔽物を避けた追加の同一斜めカメラ。
beforeは保存原本GLBのみをブラウザの応答で差し替え、afterは通常の配信GLB。
他の素材・地面・設定を切り替えない。奥面の後退と見込み面を画像と実GLBの斜めレイで確認する。

```sh
# PowerShell: $env:VIEWS='st1_whole,st1_front,st1_oblique,st1_detail'
node scripts/capture-street-fix.mjs http://127.0.0.1:5204 evidence/st-1-opening/after
node scripts/check-st-1-opening-view.mjs http://127.0.0.1:5204 evidence/st-1-opening/oblique-clear
node scripts/check-st-1-browser.mjs http://127.0.0.1:5204 evidence/st-1-opening/look
```

撮影前にbuild/syncを完了し、撮影中は資産・srcを固定、ブラウザは順次実行する。
`look/` は通常昼→夜→昼復帰、1秒間隔の非停止画像一致、分類表示を検査する。
分類は看板=黄、中央柱と見込み面・奥面=赤（壁）。昼夜とも開口の縁が保持され、看板の向き・文字は既存のまま。
画像で見える範囲に新たな二重表示・裏抜け・公共通行部の閉塞は認めない。
固定昼フレーム一致はこのカメラでの時間的なちらつき検査であり、全角度の完全保証ではない。

- `validation.txt`：全249テスト、既存予算検査、型検査を含むビルド。
- `invariance.json`：対象外14 GLB、地面・look・歩行処理・FPSコードの保持、再利用画像のSHA。
- `after/capture_log.json`：通常4カメラと資産／レイヤーの取得成功、エラーなし。
- `oblique-clear/checks.json`：追加の同一斜め視点、原本差替えの有無と取得状態。
- `look/checks.json`：昼夜復帰、分類、エラーなしの記録。

写真で確認したのは看板・左開口・右中央柱の関係と見込みの存在。
実寸・奥行き0.65m・暗い閉鎖奥面は推定。内部や通行可能な入口は制作せず、現地夜間光量・2025年10月状態は未照合。
元写真・切抜き・認証情報は含めない。詳しくは [補完報告](../../docs/core/ST_1_OPENING_REPORT.md)。
