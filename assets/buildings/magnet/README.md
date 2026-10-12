# MAGNET by SHIBUYA109（G3 v1）

スクランブル交差点の北東の角に建つ MAGNET by SHIBUYA109 を、QFRONT v5 と同じ手順で作ったモデルです。
**再現する年は 2025 年です。** 看板・広告・画面は「2025 年の年代レイヤー」として、建物本体とは別のデータに分けています。

## 中身
| 場所 | 内容 |
|---|---|
| `source/blender/build_magnet.py` | 生成スクリプト（Blender 4.2.3）。毎回ここから組み立てる |
| `source/blender/matlib.py` | 材質と部材の共通部品（QFRONT v5 から変更せずに流用） |
| `source/blender/export_web.py` | GLB の書き出し（コレクション単位で 3 つの GLB に分ける） |
| `source/data/magnet_plateau_lod2.json` | PLATEAU 2025 LOD2（建物 ID `bldg_d47d8aa9…`）を Blender の軸に直したもの |
| `source/data/measurements.json` | 寸法。どの数値が PLATEAU 由来で、どれが写真由来かを明記 |
| `source/data/camera_m027_fit.json` | 2025-09-01 の写真 M027 に合わせたカメラ |
| `source/data/signage_2025.json` | **2025 年の年代レイヤー**（看板・広告・画面） |
| `source/tools/` | カメラ合わせ（`camfit.py`）、写真の画素から高さを求める（`backproject.py`）、看板画像の生成（`make_signs.py`）、ROI 計測（`roi_metric.py`）、写真取得（`fetch_commons.py`） |
| `source/refs/` | 参考写真 25 枚と台帳（`REFERENCE_REGISTER.csv`）。すべて CC0／CC BY／CC BY-SA |
| `source/blend/` | 昼と夜の `.blend`（フォントと看板画像を同梱。HDRI は QFRONT のものを相対パスで参照） |
| `web/` | ブラウザ用：`magnet.glb`（建物）、`magnet_signs_2025.glb`（2025 年の看板）、`viewer.json`、昼夜の発光の表 |
| `renders/v1/` | 比較用の描画結果 |

栄楽ビル（MAGNET の東隣、アコム・レイク・アイフルの看板がある細いビル）は PLATEAU では MAGNET の建物に含まれています。
しかし実際は別の建物なので、`assets/buildings/eiraku/` に分けました。

## 作り方
```
cd assets/buildings/magnet/source
python3 tools/make_signs.py textures/
blender -b -P blender/build_magnet.py -- renders/v1 day final view=m027      # 写真 M027 と同じカメラ
blender -b -P blender/build_magnet.py -- renders/v1 night final view=sw      # 夜、南西の上空から
blender -b -P blender/build_magnet.py -- blend day final save norender       # .blend を保存
blender -b -P blender/build_magnet.py -- renders/v1 day final era=none       # 看板なし（建物だけ）
```

## 年代レイヤー
- 看板の位置・大きさ・色・文字は `source/data/signage_2025.json` にあります。
- 別の年の JSON を作り、`era=<年>` を付けて生成すれば、看板だけを差し替えられます。
- 文字はフォントで作り直しています。広告や画面の絵は自作の仮の絵です。**写真の画素は一切使っていません。**

## 写真について
- 2025 年の写真は M027（2025-09-01、CC0）と M004（2025-11-01）です。2026 年 2〜3 月の写真（M001〜M003）は、看板の確認に使いました。
- 2019〜2020 年の写真（M014 など）は、形の確認にだけ使いました。看板は 2025 年のものに合わせています。
