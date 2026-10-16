# Hachikō uploaded-scan candidate v001

独立したローカル確認候補です。既存モデルは置換していません。統合・配置・マージ・デプロイは未実施です。

- 元スキャンの像、足・尾と一体のブロンズ座、石台座、銘板、最下段タイルを維持しました。
- 余分な周囲舗装だけを、UV島と接続関係で確認した既存の境界に沿って除去しています。一律の高さ切断ではありません。
- 旧設計の全高 2.40559 m に合わせた単一の一様スケールです。実測寸法ではなく、台座に合わせた押し縮めもしていません。
- 原画像のJPEGバイト、UV座標、材質パラメータを保全しています。像の彫刻・リメッシュ・穴埋めはしていません。
- 底中心原点、glTFは上+Y／正面−Z、Blenderは上+Z／正面+Yです。

## 確認するもの

1. `evidence/scan_front.png` と `evidence/scan_front_oblique.png`: 実際のGLBをBlender 4.2.3でレンダリング。
2. `evidence/legacy_vs_scan_front_oblique.png`: 既存v001と同一カメラ・同一全高・同一照明での比較。
3. `REPORT.md`: 実施内容、測定値、保全検証と既知の制約。
4. `model/hachiko_uploaded_scan_candidate_v001.glb`: 正規の候補データ。
5. `model/hachiko_uploaded_scan_candidate_v001.blend`: 一体のスキャン＋確認用照明／カメラ。比較用の旧モデルは保存していません。
6. `PROVENANCE.md`: 作者、CC BY 4.0、元モデルURL、変更内容。配布時も保持してください。

## 再生成

必要環境: Python 3 + NumPy、Blender 4.2.3 LTS。

    python source/build_candidate.py
    /path/to/blender-4.2.3-linux-x64/blender -b -t 4 --python-exit-code 1 -P source/render_verify_editable.py
    python source/compose_comparison.py

比較レンダーの既定入力は隣接する `hachiko_complete_local_candidate_v001/hachiko_complete_local_candidate_v001.glb`。異なる場所にある場合はBlenderコマンド末尾に `-- --baseline /path/to/hachiko_complete_local_candidate_v001.glb` を付けます。比較入力がなくても新候補の2視点と編集可能BLENDは再生成できます。

`inputs/hachiko_source_unchanged.glb` はアップロード原本の無変更コピーです。入力ハッシュと削除元面IDを固定し、同一入力から決定的にGLBを再生成します。`model/transform.json` に順逆変換を保存しています。元の面を完全に復元する場合は保全した原本を使用します。

底面を閉じる追加面は作っていません。下端には原スキャンの傾き・不整形があり、小さい像の穴と座付近の非多様体辺も原状のままです。忠実度・現地の現況・実測精度を保証する完成版ではありません。
