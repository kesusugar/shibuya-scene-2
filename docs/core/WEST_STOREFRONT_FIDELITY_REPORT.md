# 西側街区：大盛堂・地上階の写真整合改善

## 今回の変更
- 旧モデルの同形2枚の暗いガラス扉と円弧下地を撤去し、左の明るい閉鎖面、角の明るい柱、センター街側の奥まった暗い入口と両脇の展示枠を再構成。
- 店舗・庇を既存の大盛堂看板と同じ2面・同じ角端点に統一。異なる幅と出幅の青い庇を各壁面に接続し、写真の明るい角柱が見える隙間を残し、写真で見える明るい前縁を追加。
- 新しい写真貼付、独立した階ごとの画像ワープ、新材質はなし。大盛堂・DMM・Rakutenを含む広告は完全に元のまま。
- Nishimura/薬局の棚や商品は低解像・遮蔽から確定できず、今回は変更しない。既存上階・PLATEAU原データ・地面82測点・年月レイヤー・QFRONT/西武は変更なし。

## 出典と確認
WB01: Syced、2025-01-31、CC0。 https://commons.wikimedia.org/wiki/File:Shibuya_crossing,_seen_from_Shibuya_Stream.jpg
WB02: Syced、2025-02-07、CC0。 https://commons.wikimedia.org/wiki/File:Shibuya_crossing_(12214).jpg
両写真の実画素を拡大確認。1月モデルに2月の広告を混ぜず、2月は安定した建築の確認に限る。photo_landmarks.jsonは両写真合計12の手読みランドマーク（元画像座標・約±5px）。これはカメラ校正や誤差最適化ではない。

## 比較と測定
before/afterのfull・front・sideは各々同一カメラ・照明・レンダリング条件。fullのみ既存の近似写真対応カメラ、front/sideは形状確認用の斜め近景。
旧店舗枠の四端点から対応する既存看板面端点までの平面距離は平均1.858m、新構成では同じ端点を使用し0m。旧庇同士の背面角の隙間4.349mは0m。これはモデル内部の境界整合性であり、実物との絶対座標誤差や写真再投影誤差ではない。

## 推定・未達
庇出幅0.68/0.92m、入口奥行0.46m、枠幅、展示枠の分割は写真の比率からの近似。隠れた店内は無地の暗面。商品・ポスター・文字は創作しない。既存看板自体の写真投影・形状推定の誤差を今回の整合指標で解消したと主張しない。全景の地面/歩行者/周辺との接続はこの単体レンダーでは証明されない。

## 再生成
Blender 4.2.3のみ。既存build_west.pyの4引数: source/data/plateau.json source/data/facades.json cached web。
render_storefront_evidence.pyの3引数: web 出力PNG full|front|side。比較はbaselineとcandidateに同じスクリプトを使用。
storefront_validation.jsonに容量・三角形・描画単位と保全ハッシュを記録。独立全体テストは別レビュー報告参照。
