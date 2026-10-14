# 渋谷第一勧銀共同ビル：対象同定の修正と外装の再制作

対象は way/114755219 / PLATEAU bldg_5e891186-4803-48a0-9664-284f212881ac。宇田川町23-3の「UC屋上看板・外付けX筋交い・みずほ」の建物です。隣の渋谷駅前ビルにある赤い窓枠、EyeCity、L'Occitane、曲面広告ではありません。

以前のlayout/READMEは隣ビルの外観特徴を取り違え、赤腰壁・全面ガラス・大きな東面スクリーン・横一列の黒い広告帯を誤って付けていました。今回はそれを撤去し、2025年1月31日/2月7日の写真に写る正しい横ルーバー、外付け筋交い、東面の細い連続窓、UC塔、屋上看板支持架構へ変更しました。既存PLATEAUの全壁面/屋根の頂点と位置は保持。既存モデルの重複や建物移動ではなく、付加外装の取り違えの修正です。

## 日付と表示

- 建築本体：web/daiichi-kangin.glb。写真テクスチャなし。
- 別レイヤー：web/signs-2025-01.glb。2025-01-31 Syced / CC0写真由来のUC 2面・龍角散・Vanguard・みずほ、5枚。
- 1月の広告を10月と扱わない。ビューアーの既定年代やレイヤー設定はこの変更では触らない。新レイヤーの通常表示への接続は別途確認が必要。
- 比較画像は1月の別レイヤーを明示的に重ねたBlender画像。既存WebGLの通常画面を検証したものではない。

## 再生成（Blender 4.2.3 LTS）

    blender -b --python-exit-code 1 -P assets/buildings/daiichi-kangin/source/blender/build_daiichi.py

引数なしで、同じ資産フォルダのsource/data/plateau.json、recorded_ground.json、同梱PNGを読み、webの2 GLB・viewer/emissive設定・stats・編集用blendを再生成。ネットワーク/外部Pythonパッケージ不要。旧4引数CLIは誤ったlayoutの再適用を避けるため明示的にエラーにする。build_daiichi_fidelity.pyが本体。blendは全画像をpack済み。source/data/layout.jsonは正しい対象と寸法推定の説明用で、生成の数値定義はPythonに集約。

T.P.15 m基準と既存地理原点を保持。建物は街路小物の底面原点へ移動しない。viewer groundElevationTP=15。足元は既存49サンプルの記録を再利用して同じスカートを作る。新しい地面測定をしたとの主張はしない。

## 根拠と推定

- 建物同定：所有者の「渋谷共同ビル」公式ページ、宇田川町23番3号、地上8階・地下2階。https://www.seiwa-building.co.jp/building/office/item_off_shibuya.html 。公式写真は同定の閲覧参考のみ、再配布やテクスチャ化なし。掲載写真の日付は不明。
- 2025-01-31、Syced、CC0: https://commons.wikimedia.org/wiki/File:Shibuya_crossing,_seen_from_Shibuya_Stream.jpg 。UC・X筋交い・横ルーバー・屋上看板を直接確認。5画像は透視補正・縮小のみ。看板の輪郭の少量の周辺画素/撮影時の陰影は残り、欠けた文字を描き足していない。
- 2025-02-07、Syced、CC0: https://commons.wikimedia.org/wiki/File:Shibuya_crossing_(12214).jpg 。別角度で筋交い/横ルーバー/東面窓帯を確認。
- PLATEAU：国土交通省 Project PLATEAU「渋谷区2025年度3D都市モデル」を加工。https://www.mlit.go.jp/plateau/ 、https://www.mlit.go.jp/plateau/site-policy/ 。全元頂点の保持を検査。
- 推定：正面有効範囲u=.265–.975、3.75 m階間隔、筋交い材0.16–0.20 m、5段ルーバー間隔0.22 m、東面窓高さ0.92 m、看板支柱/奥行、屋上サービス箱、入り口分割・室内カーテン。実測ではなく写真の種類・比率をPLATEAUへ合わせた値。
- 屋上看板は1月写真の大まかな投影と既存屋根内の支持位置を用いた推定。UC塔の既存屋根は保持。隠れる背面のテナント文字は生成しない。

## 残る差 / 検査

実写では隣の駅前ビルと西側街区が大きく手前を隠す。比較モデルは対象単独のため、その遮蔽を意図的に再現していない。投影は西側街区写真の近似カメラを転用し、本建物の精密測量カメラではない。正面全体の窓数、1階の隠れた店舗詳細、裏面・屋上設備の正確な配置、光沢/汚れ、10月の看板は未達。フォトリアル完成の判定はしていない。

Blender 4.2.3で再生成、全元壁/屋根頂点の保持、建築本体の画像なし、日付別画像5枚、B予算（120k tris/40 primitives/3MB）内を検証。全体npm test/build/ブラウザ統合/FPSはこの環境では未実施。旧テストの赤い腰壁必須・大きな窓の位置固定は誤外装を正当化するため、正しい材質/細窓・別レイヤーの検査への差分を別途提供する。
