# BOX-2 看板分類の比較

左がPR79マージ後main `b0ce9d2`、右が修正後。建物一覧・品質・カメラは同一。
`boards/roof-{day,night,class}.png` と `boards/clock-{day,night,class}.png`。
分類表示では看板が黄色、壁が赤、ガラスが青。通常表示も看板が壁用反射から外れる。

```sh
node scripts/check-box-sign-look.mjs http://127.0.0.1:5204 evidence/box-2-sign-look/before
# 生成元の修正・再生成・テスト・ビルドを済ませ、撮影中は同期しない
node scripts/check-box-sign-look.mjs http://127.0.0.1:5204 evidence/box-2-sign-look/after --expect-signs
```

通常表示はUIの昼→夜→昼を使用。`day-return.png` と最初の昼PNGの一致を確認する。
変更前にも同じ一致を確認済み。既定nightSign=1の昼夜操作は画像検査、
非既定nightSign=0.37の適用は実GLBの回帰テストで確認する。
`checks.json` は各パスの6レイヤー・エラー記録、`invariance.json` は7GLBのmainとのバイト一致、
`validation.txt` はテストとビルドの記録。FPSや現地夜景の光量は検証していない。
窓枠で時計が一部隠れる既存制約は保持する。
