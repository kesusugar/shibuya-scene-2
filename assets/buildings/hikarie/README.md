# ヒカリエ：既存実装の累積外装修正版

2026-10-15。既存のヒカリエ（PR35/36）を置き換える修正で、新規建物の追加ではありません。現在の main e6430b1a と比較し、北西面の個別外装、面90の凹形分割、屋根面0の分割修復、source91上部の汎用格子整理をまとめています。元の地理座標、99点の舗装標高、T.P.15m基準を維持。QFRONT・西武・109・高木ビル・歩行表示・FPS設定・共有ランタイムは変更しません。

## 見た目と未達
北面90は淡色パネル、疎な横スリットと独立窓、西面42/50/72は面に合う割付へ。source91では中間版から906三角形を除き204を保持し、不透明シェル129/288・隣のsource63を維持します。この906はmain全体との差ではありません。暗色帯の位置・幅、隠れた下部、浅い奥行きは推定。実測・写真精度の完成・2025年10月の一致は認定しません。広告や写真テクスチャは追加しません。

## 再生成
資産ディレクトリから：
python3 source/facade91-v1/tools/regenerate.py --output web/hikarie.glb
python3 source/facade91-v1/tools/validate.py

Python標準ライブラリだけで中間版14cb88b7から現行2f4e9512をバイト一致で再生成します。PLATEAUから全工程を再生する経路ではなく、過去の外装・屋根修復を含む固定中間GLBを入力とします。編集可能シーンは source/facade91-v1/source/hikarie.blend（Blender4.2.3）。新たに原シーンとGLBの意味的同一性を確認済み。Blenderの再exportのバイト一致を約束するものではありません。

## 検証と比較
現行は30,562三角形、15 primitives、2,349,752 bytes。mainは37,134三角形、8 primitives、2,344,448 bytes。三角形-6,572、primitives+7、容量+5,304 bytes。既存B予算内。
main GLBは空のAPI応答を利用せず、元生成器と厳密な舗装サンプルから再生成し、Git blob02554a5353162cc2dc70175d867f1592fa386416の完全一致で確認しました。source/main-baseline-v1/に再現入力を保存。evidence/cumulative-v2/はこのmainとの同一カメラ資産単体比較です。写真角度は近似・未校正。source/facade91-v1/evidence/の旧比較は中間版との比較です。

変更していないmainランタイムに対する13の限定テスト、再生成、編集シーン整合性は合格。全シーンbuild、全テスト、ブラウザ表示、FPSは未検証。マージ・デプロイなし。既存の歴史的ファイルは削除しません。

## 出典・権利
2025-06-15 Nesnad、CC BY4.0： https://commons.wikimedia.org/wiki/File:Hikarie_and_Shibuya_scramble_square_buildings_2025_June_15.jpeg
ライセンス： https://creativecommons.org/licenses/by/4.0/
含む写真は矩形切抜き・縮小、比較画像への配置。原画はパノラマ/TouchRetouch加工の注意あり。JuneはOctoberではなく測量写真でもありません。その他の非再配布写真は同梱しません。詳細 source/facade91-v1/docs/SOURCES.json。PLATEAU・既存モデルの権利表記は既存repositoryを継承し、写真ライセンスをモデル全体へ拡張しません。
