# QFRONT（v5、オーナー承認済みの完成版）

Shibuya Scene 2.0 の最初の建物資産であり、**今後の建物の品質基準**です。

## 構成
| パス | 中身 |
|---|---|
| `source/` | 制作プロジェクト `qfront-photoreal` 一式。**全履歴を含めて取り込み済み**（subtree で統合。元の 25 コミットは `git log 0da0383^2` で、元のパスのまま確認できる） |
| `source/blender/build_qfront.py` | 生成スクリプト（原本）。形状・材質・照明・カメラ・描画設定をすべてここで生成する |
| `source/blend/qfront_v5_{day,night}.blend` | スクリプトから書き出した Blender ファイル。フォントは内部に埋め込み済み。テクスチャと HDRI は相対パスで参照 |
| `source/data/` | 実測データ：寸法、写真に合わせたカメラ、PLATEAU LOD2、平面形状 |
| `source/textures/`、`source/hdri/` | 自作のテクスチャと、CC0 の HDRI |
| `source/refs/` | 参考写真（ライセンスを確認済みの 105 枚）と台帳 `REFERENCE_REGISTER.csv` |
| `source/deliverables/` | v1〜v5 の比較画像、v4 の監査結果、描画の記録 |
| `source/docs/` | 設計、計画、各回の報告書、素材のライセンス一覧、Phase 0 の監査 |
| `renders/v5/` | v5 の最終描画（PNG、6 枚） |
| `web/` | Web 用の GLB と LOD を置く場所（G2 で作成予定） |
| `manifest.json` | 座標、高さの定義、出典、ライセンス、ファイルごとのハッシュ値 |

## 再生成の方法
```
blender -b -P assets/buildings/qfront/source/blender/build_qfront.py -- out day final view=q032
```
Blender 4.2.3 LTS と Cycles を使います。

## 年代の扱い
- v5 は **2018 年の写真（Q032）に合わせて** 作りました。完成版はこのまま保存します。
- 2.0 の再現年代は **2025 年** です。2018 年と 2025 年で違う部分は、本体とは分けて差し替えられるようにします。差し替えの対象は次のとおりです。
  - 看板：TSUTAYA、STARBUCKS、QFRONT の文字
  - 大型画面（Q's EYE）の映像
  - 店舗の内装
  - 周辺の広告
- 2025 年版を作るときは、`build_qfront.py` 内のこれらの部品を「年代レイヤー」として分ける作業から始めます（建物本体の形状は変えません）。

## 主な数値（詳細は `manifest.json`）
- 王冠の上端 52.13 m（PLATEAU LOD2）、内側の屋根 48.4 m、PLATEAU の measuredHeight 45.9 m（建物本体の高さ）
- Q032 の写真に合わせたカメラのずれ：13 px RMS、外形線のずれ：中央値 12 px
