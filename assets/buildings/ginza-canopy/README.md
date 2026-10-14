# 銀座線ホーム上屋 — 上部の部分B試作

元の形は国土交通省Project PLATEAU「渋谷区2025年度3D都市モデル」を加工した。

way/810356690の元の屋根・上部デッキの全頂点を保持し、上部の閉じた壁を開放。M形フレーム、推定の島式ホーム、ホームドア、点字帯、線路、照明を追加した。下部の元の形は残し、完成Bとは扱わない。

形の種類は2025年3月・2024年12月の補助写真を参照。10月内部の独立照合は未達。床は隣接PLATEAU高架のT.P.28.125〜29.531 mを補間した推定。線路・ドア・フレームの位置と寸法は推定。共通T.P.15 m基準で上面の差0 m、上下移動0。

地面4点を照会し、西端付近1点T.P.15.282 mが得られた。残る3点と下部の地面合わせは未達で、元の下部を一括移動していない。

初版は外側のMフレームが屋根に埋まったため、フレームだけ0.35 m下げた。初版はlayout.jsonのrib_drop_mを0、最終版は0.35として再生成できる。フレーム補正ではドアの不透明度0.8、床・照明・元の屋根は同時に変えていない。その後、ドア間の固定部の隙間だけを補正した。初版はrib_drop_m=0・continuous_housing=false、フレーム補正後は0.35・false、最終版は0.35・trueで再生成できる。ドアの見え方と屋根の外観の精密化は未達。

## 再生成

リポジトリルートからBlender 4.2.3 LTSで実行：

```sh
blender -b --python-exit-code 1 -t 4 -P assets/buildings/ginza-canopy/source/blender/build_ginza_canopy.py -- assets/buildings/ginza-canopy/source/data/parts.json assets/buildings/ginza-canopy/source/data/layout.json assets/ground/core/web/ground_core.glb assets/buildings/ginza-canopy/web
```

11,314三角形・11描画単位・715,544 bytes。通常表示に追加し、同じIDのCを一度だけ除いた。context=nostationでは駅側5資産を除き、既存5資産を残す。推定を台帳とHUDへ記載。広告・人物・列車は追加していない。

出典はsource/refs、報告は `docs/core/C1_GINZA_CANOPY_REPORT.md`、画像は `evidence/c1-ginza-canopy/boards/`。

公式の2019-10-28設計資料（GC05）がホーム幅約12 mと明記するため、試作6 mを12 mへ訂正し、ドア・点字帯を新しい端、線路を端の外1.35 m（推定）へ合わせた。幅補正前はplatform_width_m=6・rail_edge_offset_m=2.7、最終版は12・1.35で再生成できる。フレーム・床の高さ・ドア区画数・透明度・照明は変えていない。

## 地形補填後の追記

Core外側をDEMで補填した後の照会結果はstats.jsonとC1_STATION_FINISH_REPORT.md参照。補填は地形の推定であり、実際の仕上げ歩道を測った高さではない。屋根・上面は保持。生成時に最後の引数へ `assets/ground/extension/web/extension.glb` を追加する。旧い未取得の記録は当時の結果として保持。

外側道路追加後の足元を再生成する場合は、最後の引数へextension.glbとexterior-west/middle/eastの各GLBを順に渡す。追加道路使用時は旧Coreの仮fillを照会から除き、測ったCore面・追加交通面・DEMへ照会する。屋根・上面は保持。
