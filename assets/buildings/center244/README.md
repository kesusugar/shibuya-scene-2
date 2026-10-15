# Current bounded successor

Current combined delivery: 8,471 triangles, 19 primitives, 1,055,044 bytes. Reproduce final geometry with python source/cassette/scripts/add_cassette.py. See source/cassette/README.ja.md for source dates, editable file, inference and precise scope. Historical generator instructions below are not the final successor pipeline. Existing source geometry, ground datum, sign attribution and sign-era registration are retained. Detail is based on 2022/unknown-date reference imagery with partial February 2025 corroboration, not direct October 2025 proof. Rear clearance is estimated 15 mm, not physical attachment. January signs remain unregistered. No browser, full-scene, walking or FPS claim.

## Historical predecessor documentation

# センター244ビル: 2025年写真に基づく個別外装

対象は way/136691379、PLATEAU bldg_edef4503-f1ef-4f11-839a-3fad9862036c、宇田川町24-4。NAVITIMEの店舗座標が元の建物ポリゴン内に入り、公式外観と2025年1・2月の写真の形状が一致する。別の平和クワトロではない。QFRONT・西武は変更しない。

## 再生成

Blender **4.2.3 LTS**。追加アドオン・ネットワーク不要。

```sh
blender -b --python-exit-code 1 -t 4 -P assets/buildings/center244/source/blender/build.py
```

メートル、原点35.6595N / 139.7005E、X東・Y北、Z=T.P.-15m。元地盤TP16.590、元上端TP49.843。建物全体の平行移動なし。viewer groundElevationTP=15。既存の接地照会値をrecorded_ground.jsonから再利用し、全周の新規測量とは主張しない。元の3点の欠測は残る。

## 構造と推定

元plateau.jsonはバイト一致。source/blender/center244.blendには完全な元面を非表示REFERENCE_RAW_PLATEAU_DO_NOT_EXPORTコレクションにも保存。これは公開表示の形状と区別する。

- 写真で見えるクリーム石材の折れ面、連続タイル目地、広い不均等な窓、奥まったガラス・見込み、最上部の黒い帯、小窓、金色の扇形を個別形状にした。全面写真貼付は使用しない。
- 旧9階×1.8mの一様窓割は廃止。物件資料の7F/B1は階数の補助資料であり、高さを7等分する根拠とはしない。窓の上下位置・石材目地・奥行・色・下階の内装は写真比率からの推定。
- 低い主屋根12（z20.153）と笠木0,2,6,8–11（z21.635）は元面のまま。
- 上部の閉じたPLATEAU形状は広告設備の粗い包絡と解釈した**表示用仮説**。屋根1,3,4,5,7、内側立上り14,27,32,33、壁25/26のz21.635より上、複合壁17/29のz21.635より上を表示メッシュから除き、看板・露出支持鋼材に置換。25/26の低い取合い部分と17/29の低層壁は保持。元上部屋根の形状を表示メッシュで保存したとは主張しない。
- 写真で直接確認できるのは正面の広告面・その下の開いた支持材。背面全体が空洞であること、内部・背面ブレース本数は未確認。背面の開いた鋼材も原形包絡に沿う控えめな推定であり、実測構造ではない。元の閉じたソリッドは別途完全保存。
- 看板は面26の方位を使用。写真の幅に合わせて推定約8.955m、下端z25.15m、上端z34.843m以下。元の細い上部面幅7.355mそのものを看板実幅と断定しない。全体の元地理原点・上端TP49.843を維持。元planBoundsと細い支持材・看板の表示境界は異なる。
- 遮蔽された左下店頭は簡素なガラス・中立面。現行の公式サイト写真にある店舗・文字を2025年の事実としてコピーしていない。

## 年代と権利

広告は **signs-2025-01.glb** に分離。1月31日の写真で見える看板とDA VINCI 4Fの画素だけ。ベースは中立の看板筐体。現在のローダーはviewer.layers登録を無条件読込するため、**1月レイヤーはviewer.jsonへ登録しない**。通常ビューの10月表示へ1月広告を混入させず、日付切替や他建物のランタイムには変更なし。比較レンダーのみ1月レイヤーを明示的に読込。

WB01: Syced、2025-01-31、CC0 1.0。WB02: Syced、2025-02-07、CC0 1.0。写真のライセンスは著作権者の広告イラスト・商標等の権利を別途許諾するものではない。広告の内容・現在の出稿を主張しない。

看板テクスチャは単一の平面透視補正。左下隅は前景看板に隠れているため上の見える辺から外挿し、隠れた画素を透明マスクにして中立背板を見せる。欠けた絵柄や文字を生成・補完しない。詳細はtexture_quad.json、再処理はprepare_texture.py WB01.jpg。DA VINCIは解像度の低い観測画素のまま。

公式外観画像2枚は形状を目視確認しただけの著作権・撮影日不明資料。配布物・テクスチャ・比較ボードには含めない。

## 検証の範囲

元GLBをGitHubからそのまま取得し同一カメラで前後を撮影。写真用の近似カメラは測量校正ではない。正面・側面・接写も前後同一。単体資産の再生成・予算・GLB・窓の実奥行・広告面前後関係を検査。完全な周辺シーンは入手できず、全景描画・実機FPSは未実施。写真一致／完成の認定ではない。
