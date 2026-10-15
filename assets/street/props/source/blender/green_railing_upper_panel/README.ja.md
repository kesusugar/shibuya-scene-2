# 緑色柵の上側パネル：未配置の形状資料

既存納品の上側アーチ・中央U字くぼみ・横管2本だけを保存する独立資料です。参照場所は東京都港区南麻布であり、渋谷の設置証拠ではありません。支柱、下部、足、基礎は含まず、柵全体・1スパンの完成品でもありません。ランタイムへ登録・配置しません。

## 寸法と日時
幅2.000 m、奥行0.044 m、高さ0.49004224 m。全寸法・管径・対称性・曲線・塗装色は制作上の仮定で、測量・製品仕様ではありません。上管44 mm、中管36 mm、装飾管26 mm。底面中央原点は部分モデルの底であって地面ではありません。Blenderはメートル/Z上、GLBはY上です。
原資料の写真日時は2025-07-13 15:58:23（時刻のタイムゾーン未検証）。2025年10月の渋谷設備や現地採用形式は未検証です。制作日2026-10-15。

## 出典と権利
参照写真：RuinDig / Yuki Uchida。原納品に記録された出典：
https://commons.wikimedia.org/wiki/File:Tokyo-Shibuya-and-Shinbashi---2025-07-13_164.jpg
原納品記録のライセンス：CC BY 4.0 https://creativecommons.org/licenses/by/4.0/
今回の公開準備では出典ページの再取得に失敗したため、写真・切抜き・写真入り比較図は収録していません。この権利表示は原資料の来歴であり、写真ライセンスの再検証済みという意味ではありません。写真テクスチャなし。
モデル・Python・スタジオ画像は本プロジェクト用に新規生成された成果。第三者の写真を含む画像はありません。新たな一律ライセンスの付与は行いません。

## 再生成と検証
Blender 4.2.3 LTSのみ（外部Python依存なし）。このフォルダをコピーし、以下を実行します。

    blender -b --threads 4 --python-exit-code 1 -P generate.py
    blender -b --threads 2 --python-exit-code 1 -P validate.py

生成時は同じフォルダのGLB、blend、PNG、generation.jsonを更新します。検証はvalidation.jsonを出力します。納品GLBは3448三角形、84756 bytes、1 mesh/1 material、外部画像・参照なし。blendはASSETの3編集部品と書き出さないSTUDIO_RENDER_ONLYを含みます。保存済みblendからの再出力も納品GLBと完全一致。
公開準備で変えたのは生成スクリプトの保存render pathの相対化、および側面撮影のフレーミングだけです。モデルは変更していません。

## 取り込み仕様と対象外
main 1bec9a4964a10cbba7cf2dd6a6283761acc36c11ではprops README/import_prop.py/src/world/props.tsが存在しません。PR38系列a524057a1074d46d397412a2bf61ab157ecc02dfの仕様を読み取り専用で参照し、importerを一時領域で実行しました。警告なし、倍率1、3448三角形、prop_furniture_0。旧基盤は復活させません。
GLBはsource内だけに保存し、web/、layout、world registry、建物、QFRONT、西武、歩行表示、FPSは変更しません。実景配置・衝突・全景品質・FPSの合格を主張しません。
