# MAGNET メイン画面だけの既存納品反映

検証日: 2026-10-15 UTC。基準main: 1bec9a4964a10cbba7cf2dd6a6283761acc36c11。

## 差分

既存の納品ZIP magnet-active-screen-update.zipの最終GLBをそのまま採用。現在mainの看板GLBは固定before入力とGit blob a3c390f735b05a3a22ebb7ded6a0e8ba883b4206で一致。最終GLBは083ab6d91e93aae4e61a23fe971f046bb32ce766。新規モデリングではなく、映像面の4頂点・8座標成分のみ。バイナリ変更24 byte、アクセサ境界JSON長により全体44 byte増。16,092三角形、31メッシュ、19マテリアルは不変。

運営者仕様の8.64×4.80 mへ。X中心39.8、Y8.67、0.030000877 mの前面離隔は維持。Z16.46–21.26、中心18.86 mは2025-10-24公開資料の写真による推定。撮影日は不明。筐体の写真から読む上下端と各約0.69 mの差、感度18.72–19.00 mは残る。測量精度・全体外観の完成は主張しない。

## 年代・通常表示・権利

既存のnominal2025看板レイヤーだけを更新し、viewer.json・srcは変更しない。既存自作仮画像5枚、文字、他看板、Eirakuの看板もバイト不変。これは2025年10月の実広告復元ではない。資料には2025年9月/11月と2026年2–3月が混在し、全看板の10月状態は未確認。今回、新しい年代広告の有効化や元看板の非表示化は行わない。

参考写真・キャンペーン画像は追加配布しない。出典URL、公開日と撮影日の区別、権利・推定はsource/active-screen-v1/sources/SOURCE_AND_INFERENCE.md。既存manifestのPLATEAU/写真帰属を維持しCC0とはしない。

## 検証

- 固定入力7件（看板before、本体、Eiraku、viewer、昼夜発光表、元signage）と現main blobの一致。
- Python標準ライブラリの正規生成で最終GLB/source JSONが納品物とバイト一致。
- 変更可能領域を4頂点のX/Zに限定し、全JSON（アクセサ境界除く）、親子関係、ノード、画像、素材、UV、法線、索引、残り全binaryを不変検査。
- 既存magnet-asset.test.ts 5/5成功。専用Python回帰成功。既存テストの書換え・緩和なし。
- Blender4.2.3で保存済み編集blendを再open、5枚すべてのpack・画素読出し、対象頂点・座標・コレクション成功。保存時のpacked-image警告はあるが再open検査成功。
- 同じ既存southカメラ1100×1400、Cycles CPU24sample、AgXで現main/最終を直接JPEG出力。比較boardはこの2枚から作成。写真画素を含まない。beforeは実before GLBの保存座標を読み、他データ同一性は別の厳密検査で証明。

元blendは納品バイトを保存。再生成blendは構造検証のみでバイト同一は主張しない。全scene・build・ブラウザ・歩行・FPS・衝突の検証は実施していない。QFRONT、西武、他建物、本体GLB、viewer、srcは変更なし。
