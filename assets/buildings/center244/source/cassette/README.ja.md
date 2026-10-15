# Center244 面取り入口・固定カセット追加候補

## 範囲
既存 Center244 に、小さな固定金属カセットを一つだけ追加した候補です。幅約 2.715 m、高さ 0.270 m、奥行 0.245 m。上部箱、左右の角形キャップ、細い暗色スリットの計4部品、48三角形、2マテリアルプリミティブです。布、腕、モーター、金具、文字、店舗名、商品、写真テクスチャは追加していません。正確な2025年再現ではなく、写真を参考にした寸法推定です。

対象は assets/buildings/center244、way/136691379、PLATEAU bldg_edef4503-f1ef-4f11-839a-3fad9862036c の面取り入口。元 WallSurface の配列番号18は位置の同定にだけ使い、元の面を置換しません。

## 根拠・日付・権利
- シブヤ経済新聞 https://www.shibukei.com/headline/16659/ 。公開2022-05-10、開店2022-04-26、撮影日不明。画像 https://images.keizai.biz/shibukei/headline/1652087551_photo.jpg を実際に目視し、右側入口上の浅い箱と角形端部を参照しました。著作権写真は閲覧のみで、保存・同梱・テクスチャ化していません。
- https://davinci-clinic.jp/clinic/access/ の外観 https://davinci-clinic.jp/wp-content/themes/da-vinci-theme/images/new/access/exterior1.png 。公開・撮影日不明。既存調査用画像を目視し形状を照合。閲覧のみで本パケットには複製していません。
- Syced、2025-02-07撮影・アップロード、CC0 1.0: https://commons.wikimedia.org/wiki/File:Shibuya_crossing_(12214).jpg 。既存クロップを目視しました。低層部は遮蔽があり、細い淡色帯の継続を部分的に支えるだけで、端部形状や寸法を解像する写真ではありません。この写真も今回は同梱・使用しません。
- 施工事例 https://www.tenken.co.jp/works-design/チュチュアンナ　渋谷センター街店/ は案件日2022-04-26。写真撮影日とはみなしません。本工程で写真を直接検証した出典には数えません。

詳細形状の根拠は2022年写真と年代不明写真です。2025年2月の写真は部分的継続根拠に限り、2025年10月の存続は中程度の確度の建築的推定です。直接の対象月証明が必要な用途では採用を保留してください。現在のテナントや看板を推定していません。

既存 base/sign の権利・出典は inputs/BASE_SOURCES.md を保持。既存 sign GLB 内の CC0写真由来画像はそのまま保持されます。写真CC0と広告・商標等の権利は別です。本追加は写真を使わないオリジナルの単純形状と無地マテリアルです。

## 座標・推定寸法・隙間
inputs/PROPOSAL.json の基準を変更せず採用。原点 A=(-69.497,70.742,0)、接線 t=(0.8828833046,0.4695924514,0)、外向き n=(0.4695924514,-0.8828833046,0)。P=A+u*t+d*n+(0,0,z)。u=0.3232590293..3.0386348751、d=0.055..0.300、z=4.430..4.700 m。Blender X東/Y北/Z=TP-15、glTF=(X,Z,-Y)。viewer の groundElevationTP=15 と既存アンカーは不変です。GLB float32 の数µmの誤差は検査許容値10µm以内です。

既存入口開口上端z=4.30から約130mm、上部パネル下端z=4.75まで約50mmを確保します。背面d=.055は既存金帯d=.040より15mm外にあり、壁d=0には接触しません。背面の小隙間を隠すための推定金具は作りません。これは離隔を持つ外観近似であり、物理的な接合・施工ディテールではありません。裏側接続、布の巻取り機構、架構は検証していません。既存金帯の一部を前から覆いますが、元の三角形は削除しません。

## 再生成
Python 3標準ライブラリのみでGLBを再生成できます。

    python scripts/add_cassette.py
    python scripts/verify.py

編集用 .blend と6枚の同一カメラ比較画像を再生成するには、正確に Blender 4.2.3 LTS を使います。

    blender -b -t 4 --python scripts/render_blend.py

出力は output/center244.glb、output/center244-cassette.blend。元入力は inputs/ に全て揃っています。ネットワーク・外部リポジトリ・外部画像は不要です。既存の全建物generatorを再実行せず、専用スクリプトでGLBに追加します。.blendは実際の納品GLBと変更なしのsign GLBをimportした編集可能なシーンで、画像はpackしています。納品GLBの再生成正本は専用Pythonスクリプトです。.blendからの再exportでは元binaryの完全一致を保証しません。

## 検証と画像の限界
evidence/verification.json は入力SHA256、元523100 byte binaryの完全prefix一致、旧mesh/material/accessor/bufferView/nodeのJSON一致、sceneの旧node保持、48三角形、正の体積、非退化面、法線、局所境界、離隔、非発光・非テクスチャ材を検査します。元UVもaccessor/binaryごと保持されます。

evidence/overview-before.png と overview-after.png は調査時と同じ診断カメラ。front/side もそれぞれ before/after でカメラ・照明を固定。写真との厳密なカメラ登録、実アプリの交差点全景・夜景・遮蔽・歩行表示を検証するものではありません。外形の目視で浅い横箱と角形端部を確認しました。

移設再生成も検査できます（この補助検査のみPillowが必要です）。PNGの保存時メタデータは比較せず、復号画素を比較します。

    python scripts/check_relocated.py /path/to/blender-4.2.3


## 入力照合
固定入力のハッシュを照合後に専用コードで追加します。背面15mmの離隔は推定値で、壁面との物理接合を主張しません。看板の未登録状態は維持します。
