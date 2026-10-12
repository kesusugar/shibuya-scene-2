# qfront-photoreal

QFRONT（渋谷）を写真と見間違える品質で再現する、独立した Blender プロジェクトです。Shibuya Scene とは別物で、そちらのコードには一切変更を加えません。

| フォルダ | 内容 |
|---|---|
| `docs/DESIGN.md` | 資料と建築の分析、寸法表、Blender での制作設計、マテリアル・ライティング方針（Phase 1） |
| `docs/PLAN.md` | 制作計画（P2-0〜P3）、評価表、レンダリング予算 |
| `refs/REFERENCE_REGISTER.csv` | Wikimedia Commons の写真 127 件の作者・日付・ライセンス・年代 |
| `refs/raw/` | 写真の縮小版。参照専用で、テクスチャには使いません |
| `data/` | PLATEAU 2025 LOD2 の QFRONT（JSON / OBJ） |
| `blender/blockout.py` | 部品構成のブロックアウト（構造図） |
| `blender/lod2_clay.py` | LOD2 のクレイレンダー |
| `deliverables/` | 主要参照・構造図・写真との並べ比較 |
| `tools/fetch_commons.py` | 写真とメタデータの取得スクリプト |

## 出典
- 写真：Wikimedia Commons（作者・ライセンスは `refs/REFERENCE_REGISTER.csv`）
- 3D都市モデル：国土交通省 Project PLATEAU（渋谷区 2025）
- 建物外形：© OpenStreetMap contributors（ODbL）
