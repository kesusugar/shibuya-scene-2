# Hachikōスキャン候補：リポジトリ収録範囲と再生成

このフォルダはDrive納品ZIPの**部分コピー**です。リポジトリの通常表示はPR #76でこのスキャンを採用済みですが、このフォルダのGLB自体は底中心原点のローカルモデルです。世界配置は `src/world/hachiko.ts` が剛体変換で与えます。

## このリポジトリに収録されているもの

このREADMEからの相対パスです。

- `model/hachiko_uploaded_scan_candidate_v001.glb`：元JPEG・形状・UV・材質を保持する候補正本。
- `model/transform.json`：元スキャンと候補の順逆変換。推定縮尺は正本へ適用済み。
- `model/geometry_validation.json`：納品時の形状検証記録。
- `PROVENANCE.md`：Maurice Svay／CC BY 4.0、元モデルURL、納品時の加工内容。
- `REPORT.md`：納品時点の結果・制約の記録。「未統合」等は当時の状態です。
- `manifest.json`：Drive完全版の納品時目録。全ファイルがこの部分コピーにあることを示しません。このREADMEはリポジトリ向けに改訂済みであり、目録の旧READMEハッシュとの一致は主張しません。ローカル収録物の現在のハッシュは `../../manifest.json` を参照。

`source/build_candidate.py`、`source/render_verify_editable.py`、`source/compose_comparison.py`、`inputs/hachiko_source_unchanged.glb`、`source/trim_face_indices.json`、編集用BLEND、納品時の `evidence/` はこの部分コピーにはありません。

## A. リポジトリ単体で可能：配信用GLBの再生成

以下は**リポジトリのルート**で実行します。Blender、NumPy、Driveの完全版は不要です。

```sh
python -m pip install Pillow==12.3.0
python assets/street/hachiko/source/tools/build_scan_runtime.py
```

入力は `assets/street/hachiko/source/scan-candidate/model/hachiko_uploaded_scan_candidate_v001.glb`、出力は `assets/street/hachiko/web/hachiko.glb`。スクリプトは入力SHA-256を検査し、形状・索引・UV・法線を保ったままJPEGを4096角→1536角へLanczos縮小し、quality80／4:2:0へ再圧縮します。材質名のみ既存の街路設備分類へ合わせ、材質値は保持します。元候補を作り直す工程ではありません。

期待する配信ファイル：2,911,696 bytes、SHA-256 `0d68077edad1fc24858cdb9c42001439488728fc2e4779676ee3f0e3e821077e`。JPEGのバイト再現には上記Pillow版を使用してください。実行後は `npm test -- --maxWorkers=2` と `npm run build` で確認できます。

## B. Drive完全版が必要：候補正本・BLENDの再生成

[完全版ZIP](https://drive.google.com/file/d/1dxpHOjS3VloGbndj2oYqoDVAP4lW66v2/view)：
`hachiko_uploaded_scan_candidate_v001_delivery.zip`

- サイズ：28,660,411 bytes
- SHA-256：`7982eff7ba6346c03d12d27d062305e321add19245c1a65a4d3fbd35b328328e`

別の一時フォルダへ取得し、サイズ・SHA-256・全CRC・展開パスを検査してください。**このリポジトリの部分コピーへ上書き展開しないでください。** 展開後の `hachiko_uploaded_scan_candidate_v001/` 内で、完全版manifestの全29ファイルを照合し、`inputs/hachiko_source_unchanged.glb`、`source/trim_face_indices.json` と各スクリプトの存在を確認してから実行します。

Python 3＋NumPyで候補GLBを生成します（カレントディレクトリは完全版のパッケージルート）。

```sh
python source/build_candidate.py
```

任意のGLB再取込・スタジオレンダー・編集用BLEND生成には**Blender 4.2.3 LTS**を使用します。

```sh
blender -b -t 4 --python-exit-code 1 -P source/render_verify_editable.py
```

生成対象は完全版の `model/hachiko_uploaded_scan_candidate_v001.glb` と同名BLEND、`evidence/scan_front.png`、`evidence/scan_front_oblique.png` 等です。候補GLBの期待SHA-256は `cd20601d57308a1b50892c05d509a6295ca24ca2045cfd37421995a840bf039e`。

旧**ローカル統合候補**との比較レンダーは別途そのGLBが必要です。既定は展開先の隣の `hachiko_complete_local_candidate_v001/hachiko_complete_local_candidate_v001.glb`。別の場所ならBlender引数末尾へ `-- --baseline /path/to/hachiko_complete_local_candidate_v001.glb` を指定します。リポジトリの `source/legacy/hachiko.glb` は座標系の異なる旧ワールド配置モデルで、代わりに指定しません。

比較PNGの `python source/compose_comparison.py` は、旧候補レンダー `evidence/legacy_front_oblique.png` と新候補レンダーの両方、Pillow、スクリプト指定のDejaVuSansフォントが揃った場合のみ実行できます。旧候補がなくても新候補とBLENDは生成できますが、比較PNGは生成できません。これはリポジトリ単体の再生成手順ではありません。

## 形状・権利・精度の制約

全高2.40559mへの一様縮尺は旧設計に合わせた推定で、実測ではありません。像・青銅座・石台座・銘板・下段タイルを一体で保持し、余分な周囲舗装だけを除去しています。底中心原点、glTF +Y上／-Z正面。正本は元JPEGを保持し、配信用派生物のみ画像縮小しています。

元の小穴、非多様体辺、開いた不整形の下面、写真由来の陰影を保持しています。彫り直し・穴埋め・平坦化はしていません。現況・実測精度・実物忠実度を保証する完成版ではありません。出典と加工通知 `PROVENANCE.md` を配布時も保持してください。
