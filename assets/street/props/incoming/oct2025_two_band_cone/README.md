# 2025年10月写真参考・白帯2本コーン（未配置）

既存納品の1コーンを保存する単独のソース・レビュー追加です。街並みへの配置・runtime登録は行いません。GLBは元納品と同一バイト、1,044三角形、34,680 bytes、1 mesh node、3 PBR材質、テクスチャなし。BlenderはZ上、GLBはY上、メートル、底面中央原点です。寸法0.38×0.38×0.70mは制作上の仮定です。

## 内容と再生成
- incoming/oct2025_two_band_cone/: 元納品GLB、説明、ライセンス
- source/blender/oct2025_two_band_cone/: 生成スクリプト、3部品の編集用blend、厳密検証
- source/data/specs/oct2025_two_band_cone.json: PR38形式の寸法・予算・材質・出典
- source/data/reports/: 今回検証とPR38取り込み結果
- evidence/props/oct2025_two_band_cone/: 実モデル正面・側面・斜め、モデルのみの一覧画像（リポジトリルート基準）

Blender 4.2.3 LTSを使い、generate.pyだけを空の任意フォルダへコピーして次を実行します。外部素材・追加Pythonパッケージは不要です。

    blender -b --threads 4 --python-exit-code 1 -P generate.py

生成GLBのSHA256は 501b57d84214ded62f4846ce534ee2129a3eac08d0dc109c22a0d19140dc0b29。撮影スタジオはblendのSTUDIO_RENDER_ONLYにあり、GLBには入りません。公開用blendは相対レンダー出力パスへ直して再保存したため元blendと同一バイトではありません。生成スクリプトの唯一の修正も保存前の相対レンダーパス設定です。形状・材質は変更していません。

リポジトリルートからの厳密検証:

    blender -b --python-exit-code 1 -P assets/street/props/source/blender/oct2025_two_band_cone/validate_release.py -- assets/street/props/incoming/oct2025_two_band_cone/oct2025_two_band_cone.glb assets/street/props/source/blender/oct2025_two_band_cone/oct2025_two_band_cone.blend assets/street/props/source/data/specs/oct2025_two_band_cone.json result.json

## mainとの境界
確認main: e78de4e4ec41efa9edd8dfb61bb8060954a7fb54。props README/import_prop.py/src/world/props.tsはこのmainにありません。PR38 head a524057a1074d46d397412a2bf61ab157ecc02dfの既存仕様を読み、同じimport_prop.pyをローカルの検証だけで使用しました。倍率1.0、警告0、1,044三角形で取り込み成功。取り込み後は材質名正規化等で34,720 bytesとなり、配布元GLBとは別の検証出力です。その出力やadapter自体は追加しません。

将来の配置には別途import adapter・layout登録・地面検証が必要です。この追加はそれらを導入せず、世界座標を捏造しません。QFRONT・西武・歩行表示・FPS・src・global予算を変更しません。場面全体、ブラウザ表示、FPSを合格とする検証ではありません。

## 参考写真の未検証と残る差
過去納品が申告した写真の作者・ライセンス・EXIF日時は今回一次資料で確認できませんでした。写真切り抜きと写真入り比較画像を配布対象から除外し、自作モデルの画像のみとしています。過去の写真参照申告はSOURCE_LICENSE.mdに未検証として残しました。型番・台座・実寸・正確な帯境界、現場位置・向き・継続設置は未確認です。正面と側面は独立した直交視点です。画像は写真一致や年代の独立確認を証明しません。
