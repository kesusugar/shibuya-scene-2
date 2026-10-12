# センター街入口西側の街区 — B段階

way/136690966 / PLATEAU `bldg_e6e4de58-1a37-4345-8795-6b759771ade6`。通常表示に出し、C段階の同じ建物を除いた。PLATEAU 2025の段差のある外形に、写真の縦の切れ目で推定した薬局・果物店・中間の区画・赤い角の外壁と窓、店舗、庇、屋上看板を付けた。完成・写真品質の合格ではない。

- `west-block.glb`：形状・外壁・窓・店舗・看板の支持物。
- `signs-2025-01.glb`：Hisamitsu/サロンパス、楽天、DMM、大盛堂書店、西村、薬局、飲食店の看板。2025-01-31の静止した広告状態。建物の形とは別の層。
- 写真：Syced、CC0、[Shibuya crossing, seen from Shibuya Stream](https://commons.wikimedia.org/wiki/File:Shibuya_crossing,_seen_from_Shibuya_Stream.jpg)。既存の `assets/street/core/source/refs/stream_2025.jpg` を使用。写真とライセンスの公式応答は同じrefsフォルダ。Street Viewや生成AIで看板を作っていない。
- `source/data/facades.json` に画像の四隅（900×1195で読んだ画素）、区画、推定状態を記録した。PILの透視変換で写真から看板面を取り出し、`source/textures/` に保持した。これはモデル用の画像で、写真と比較する元画像は変更していない。
- `source/data/plateau.json` はPR #9のcontext_inputから対象だけを抽出したもの。ZはT.P.−15。生成時はその建物の地面を0に戻してから、viewer.jsonの測量したanchorへ配置する。C2a地面の前面82点の最小値はT.P.15.347、最大15.410。PLATEAU地面との差は+0.017 m。
- 四区画の境界、窓の割り付け、曲面、庇、看板の寸法・向き・支持物はB段階の推定。1階の細部と個々の入居者・看板の親の同定は未達。奥側は写真から再現していない。

## 再生成

```bash
source /workspace/setup-tools/core-env.sh
blender -b --python-exit-code 1 -t 4 -P assets/buildings/west-block/source/blender/build_west.py -- \
  assets/buildings/west-block/source/data/plateau.json \
  assets/buildings/west-block/source/data/facades.json \
  assets/ground/core/web/ground_core.glb assets/buildings/west-block/web
npm test
npm run build
npx vite preview --port 5189 --strictPort
VIEWS=stream,hachiko,night node scripts/capture-street-fix.mjs \
  http://127.0.0.1:5189 evidence/c1-west-b/<run>
```

撮影中にビルドや資産同期をしない。ブラウザは1つずつ使う。通常表示の既定building一覧へ追加済み。`select_context.py` のOWN_ASSETSにも登録し、既存のcontext入力から同じIDを除いて再生成した。

屋上の縦看板は、最初の15.4 m中心が写真より低かったため25.4 mへ変更した。看板の高さという1項目だけを変えた比較は `evidence/c1-west-b/first/` と `after/`。夜は看板画像をemissiveMapにも使用し、白い一枚板として発光させない。
