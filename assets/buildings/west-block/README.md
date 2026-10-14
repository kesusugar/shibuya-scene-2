# センター街入口西側街区 — 写真忠実度の改訂候補

対象は `way/136690966` / PLATEAU `bldg_e6e4de58-1a37-4345-8795-6b759771ade6`。QFRONT・西武は変更しない。

本改訂は**制作途中の改善候補**であり、完全な写真再現・配置検証・フルプロジェクト合格ではない。2025年1月31日の写真を基準に、従来の薄い面・均一な窓・誤った看板切り出しから作り直した。

## 入力と出力
- `web/west-block.glb`: 建築本体、深い開口、タイル壁、枠・庇・支持物。メートル、glTF Y-up。
- `web/signs-2025-01.glb`: **2025-01-31のみ**の広告・店舗表示。建築と分離した既存レイヤー方式を維持。
- `source/blender/west-block.blend`: Blender 4.2.3 LTSで生成・保存、使用画像をパックした編集用ファイル。
- `source/blender/build_west.py`, `facade_fidelity.py`, `corner_fidelity.py`: 再生成コード。
- `source/tools/extract_fullres.py`: WB01原寸写真からの再切り出し。Pillow/NumPy使用。
- `source/data/facades.json`: 推定寸法、`ground_measurements.json`: 既存82点測量キャッシュ、`fidelity_validation.json`: 実出力の統計・予算チェック。
- `source/refs/PHOTO_FIDELITY_SOURCES.md`: 原画像URL、著者、ライセンス、日付、原寸SHA-256、加工箇所。

## 改善した主な形
1. 西村の左の開口を、壁面上の黒い四角から奥行1.05 mの開口・側壁・上下スラブへ変更。
2. 左の幅広いタイル壁、四段の淡いカーテン窓、不均等な大枠と細い補助枠、厚みのある緑の帯・薄い明色の端部を制作。
3. 店先の奥行、柱・枠・閾、庇の下面・端部、照明器具・看板枠を追加。1階の区画寸法と見えない内装は推定。
4. 大盛堂側を、緩い曲面の楽天画面と、灰色上部・DMM・書店帯の二面構成として制作。DMMの黒い左面と右の広告面を分離。
5. 原寸写真から薬局、もんじゃ、三千里薬品、クスリ、西村、DMM、書店、Hisamitsuを再切り出し。誤った隣の看板や、欠けた文字を修正。

## 測量・推定・残る差
- 元のPLATEAU入力、屋根・裏側のソース形状、source_id、viewerの地理基準、地面アンカーT.P.15.347 mは維持。元の地面測量82点の最大T.P.15.410 m。
- **建物は小物のように原点へ再センタリングしない**。取り込み仕様に従い既存の地理座標を維持する。Blender Z-upからGLB Y-upへ変換。
- 窓割り、開口深さ、タイル間隔、庇、看板厚み、店内は写真を基準にした推定で、実測ではない。
- 角の従来の推定外形は写真より細かったため、地上のファサード・看板外形を改訂した。R=8 mの緩い曲面、中心(-41.53, 32.93) m、表示幅と高さは推定。元中心(-39.718,29.972)/R4.8 mからの変更であり、元の敷地面積を測り直したものではない。看板・外装の張り出しと元の建物平面との差は、実シーンで通路や隣接建物との関係を再確認する必要がある。
- 背面・屋根奥の大きな形は元PLATEAUを残した。孤立表示では写真の隣接建物に隠れる部分も見え、写真一致とは呼べない。
- 看板テクスチャには写真の影・解像度制限が残る。店先の細かい商品・人物・店舗内装は再現していない。
- カメラは三組の既存看板四隅から求めた**近似の比較用視点**。これは地理座標や寸法の正しさの証明ではない。

## 再生成

Blenderのバージョンは4.2.3固定。プロジェクトルートから:

```bash
blender -b -t 4 --python-exit-code 1 \
  -P assets/buildings/west-block/source/blender/build_west.py -- \
  assets/buildings/west-block/source/data/plateau.json \
  assets/buildings/west-block/source/data/facades.json \
  cached assets/buildings/west-block/web
```

`cached` は既存の測量値を読み直す経路であり、新しい地面を捏造しない。実際の地面GLBを利用する場合は、この引数を `assets/ground/core/web/ground_core.glb` へ置き換える。

切り出し画像の再生成:

```bash
python assets/buildings/west-block/source/tools/extract_fullres.py /path/to/WB01.jpg
```

同じ比較視点の単体描画:

```bash
blender -b -t 4 -P assets/buildings/west-block/source/blender/render_evidence.py -- \
  assets/buildings/west-block/web /tmp/west-full.png full
```

小さな敷居・枠の下端は地面基準より0.07 m下へ入り、元の地面アンカーは移動していない。

## 検証範囲

Blender4.2.3実行、GLB出力、画像の目視確認、同じカメラの前後比較、有限座標・三角形/プリミティブ/容量、再生成の同一性を確認する。`npm test`、`npm run build`、実シーンへの同期・全体描画、オーナーPCでのFPSはこの限定スナップショットでは未実施。技術予算に収まることを写真品質の合格と同一視しない。

現出力は建築7,526三角形/20プリミティブ、1月看板76三角形/15プリミティブ、合計7,602三角形/35プリミティブ/1,056,140 bytes。既存B予算120,000三角形/40プリミティブ/3,000,000 bytes内。独立したBlender4.2.3再生成で5つのweb出力がバイト一致。これらは技術検証であり写真品質の合格判定ではない。

## Ground storefront revision
Taiseido ground-only asymmetric solid/recessed storefront and plane-aligned blue awnings with exposed pale corner wedge; see docs/core/WEST_STOREFRONT_FIDELITY_REPORT.md. Upper facade and January sign images unchanged.
