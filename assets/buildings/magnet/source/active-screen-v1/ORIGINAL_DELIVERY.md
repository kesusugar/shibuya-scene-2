# MAGNET メイン映像面・寸法/相対配置の更新

変更は08_SIGNS_2025_box_screenの映像四角形だけ。最終レイヤーはoutput/magnet_signs_2025.glb、恒久建物はinputs/magnet.unchanged.glb、付属Eirakuはinputs/eiraku.unchanged.glb。これらを同じ元座標で重ねます。編集用output/magnet_screen_editable.blendは3コレクションをまとめ、既存の5枚のオリジナル仮画像をpackした便利な編集シーンです。周辺形状・他看板・屋根・UV・画像・素材は変更していません。

## 独立再生成

Blender **4.2.3** で以下を実行すると、変更していない正規スクリプトを呼ぶ付属ラッパーがGLB/設定/編集blendを再生成します。全入力を同梱し、以前のZIP、ネットワーク、他リポジトリは不要。作業ディレクトリは任意。展開先を絶対パスへ置換してください。

    /absolute/path/blender -b -t 2 --python-exit-code 1 -P /absolute/package/tools/regenerate.py

GLBだけならPython3標準ライブラリでsource/correct_screen.py --inputs /absolute/package/inputs --output /absolute/fresh-output。編集blendはBlenderでsource/build_editable.py -- --root /absolute/package。--render追加で保存済みモデルカメラの前後・昼夜をレンダーできます。

GLB生成は既存バイナリを保持する局所パッチ。編集blend全体を再exportしてバイト一致させる方式ではありません。blend手編集は正規Pythonへ自動反映されません。

## 寸法・座標・推定

運営者2021-03-08資料の映像寸法8.64×4.80mを適用。X35.48–44.12、Y8.67、Z16.46–21.26m。X中心39.8と前面Y8.67は既存アンカー。上下位置はHUISの2025-10-24公開資料の写真を参考にし、撮影日自体は不明です。10月24日撮影とは断定しません。

1単位=1m、元のauthoring X東/Y北/Z上を保持。底面中央に移動せず、109と異なり頂点をT.P.15基準へ変換しません。既存viewerの高さoffset−0.093mは実行時に一度だけ適用する設定で、入力頂点に重ねて差し引かないでください。

写真の筐体を正規化した中心からZ18.8608mを推定し18.86mへ丸めました。実寸4.80mと写真上の筐体基準を両立できず、上下各約0.69mの不一致が残ります。中心18.72–19.00mは手動点の感度分析で、現実の信頼区間ではありません。レンズ、非共面、元筐体誤差も未解決。筐体・周辺を歪めて不一致を隠していません。

## 比較・権利

evidenceのboardとsouth/m027画像はモデルの実際の前後・昼夜レンダー。southは正面側、m027は斜め診断ビューで測量校正ではありません。JPEGは非可逆派生、元PNG画素一致は主張しません。rectified_anchor_schematic.svgは写真画素なしの新規図解です。

HUIS写真・切抜き・スクリーンショット・キャンペーン画素はcopyright reference-onlyにつき一切非同梱。原URLと数値観察のみsources/SOURCE_AND_INFERENCE.mdに記載。映像面の760×900仮画像は既存オリジナル作品を不変で利用し、横長面へ広げたものです。2025年実広告の復元ではありません。M027の元写真も非同梱で、カメラ数値のみ継承。

元MAGNET/EirakuのPLATEAU/写真由来来歴・利用条件を継承し、モデル全体をCC0とは扱いません。完全な上流権利台帳を新たに確認したという主張はしません。全景欠損、ブラウザ動作、歩行、FPS、衝突・経路、測量精度は未保証。配送ハッシュはSHA256SUMS.txt。

GLB SHA256: 72261c821608d40309254b838a11117af04d7100f13a6c6fc3acf645e168de7f

斜めM027ビューは正投影側面でもカメラ校正結果でもありません。映像面と筐体の距離0.030000877mは数値検査で確認し、レンダー見た目だけの距離証明とは扱いません。恒久MAGNET/Eirakuの同梱GLBは未変更の編集/表示文脈で、新しい建物版ではありません。
