# ST-1入口の浅い外観：派生モデルの生成元

`station-north-pr81.glb` はPR81の変更前構造GLBをバイト単位で保存した原本。
SHA-256は `eb1b9607fa28c0410ada219fd42cbb6f19592ddb2bb6002050869eb5bf65ed09`。
通常表示へ二重に読み込まない。

`opening.json` は対象面・開口範囲・浅い奥行き・写真の対応箇所と推定を記録する。
共通配置は既存の `../st-1/placement.json` を読み、そちらを変更しない。
リポジトリルートから：

```sh
node scripts/build-st-1.mjs
npx vitest run tests/st-1-opening.test.ts tests/st-1.test.ts tests/station-north.test.ts tests/budget.test.ts
npm run build
```

`scripts/build-st-1-opening.mjs` はこの保存原本から通常の `web/station-north.glb` を生成する。
`stn_concrete` のprimitive 0、元三角形94/95のうち、看板直下の矩形だけを切り欠く。
他の元三角形と頂点属性は保持。左右・上部の見込みと暗い奥面を追加する。
地面・床面・歩行／衝突処理・FPSは変更せず、床・改札・通路・階段・内部設備は追加しない。
奥面で閉じる浅い外観であり、通行可能な入口ではない。

写真はST-1と同じ宮益坂側入口の2025-04-09撮影と明記されたものだけを開口形状の根拠にする。
写真の人物・内部・ポスター・配管を制作・複写しない。写真や切抜きを配布しない。
幅・高さはST-1の仮寸法を継承。0.65mの奥行き、6mmの看板下公差、暗い奥面の位置・色は
視覚表現上の推定で、写真で測った内部寸法ではない。現地の取付位置・2025年10月状態の制約は保持する。

変更範囲・原本ハッシュ・切欠き面積・追加形状と単一行列は `build-report.json`。
対象外形状の保持は実GLBの回帰テスト、見え方はPR81と同じカメラで検証する。
