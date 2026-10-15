# dots小物の通常シーン配置

`web/layout.json` が配置台帳。白黄ボラード2本、無地の自立掲示板1基、白帯2本コーン3個を、既存のハチ公周囲と駅境界へ配置。すべて写真を参考にした**推定座標**で、測量・校正済み写真投影ではない。白ポストは7月写真で、10月の存続は未確認。

`web/*.glb` は各 `incoming/<id>/<id>.glb` のバイトコピー。形、寸法、色、原点、元材質を変更せず、実行時だけ家具の材質分類名を設定する。小物loaderは同種をインスタンス化し、地面9点を照会、最大点へ接地。足元の高さ差6 cm超や地面欠測はその配置だけ除外して画面に報告。原点ずれはGLBの底面bboxを使用し、サイズ異常を拡縮で隠さない。

全6個で10,983三角形、12描画単位（影等の追加パスは別）。通常表示、昼夜の材質処理、分類表示、歩行衝突へ登録。比較用に `?props=off`、街路全体を外す場合 `?street=off`。

南麻布の設備盤と#57の柵上部パネルは、渋谷の設置位置の根拠がなく未配置。後者は支柱・基礎なしなので既存柵の代替にしない。#38 importerはmainに未統合のため依存せず、正本GLBを直接利用する。

## 出典・制作・ライセンス

モデル作者はdot。各資産の既存条件を継承し、一括の新規ライセンスは設定しない。
- 白黄ポスト: [元ライセンス](incoming/hachiko_white_bollard/SOURCE_LICENSE.md)、[元制作資料](incoming/hachiko_white_bollard/README.md)。参照写真はRuinDig/Yuki Uchida、2025-07-13、CC BY 4.0。
- 自立掲示板: [制作・CC BY-SA 4.0条件](../../../docs/core/PROP_STANDING_NOTICE_SIGN.md)。参照写真はウィ貴公子、2025-10-10、CC BY-SA 4.0。文字なし・写真テクスチャなし。
- コーン: [元ライセンスと未確認事項](incoming/oct2025_two_band_cone/SOURCE_LICENSE.md)、[元制作資料](incoming/oct2025_two_band_cone/README.md)。今回の配置の型の参考は既存SC04写真/メタデータ。単体制作時の写真確認の制約と今回の現地座標推定は別。

元blendと生成スクリプトは `source/` に保持。今回モデルの再生成はしない。詳細、配置前後画像、再検証コマンドは [配置報告](../../../docs/core/DOTS_PLACEMENT_57_REPORT.md)。追加制作依頼は [90候補](../../../docs/core/DOTS_NEXT_ASSETS_57.md)。
