# 灰色ルーバー設備箱（形状参照のみ・未配置）

港区の写真から制作した、単独の灰色設備箱です。緑の柵・自転車・植栽・建物・道路はモデルに含みません。渋谷シーンへの配置は保留です。

## 出典・利用条件
- 写真: [Tokyo-Shibuya-and-Shinbashi---2025-07-13 164](https://commons.wikimedia.org/wiki/File:Tokyo-Shibuya-and-Shinbashi---2025-07-13_164.jpg)
- 作者: RuinDig / Yuki Uchida。撮影: 2025-07-13 15:58:23。
- 場所: 南麻布ビル、東京都港区。ファイル名に Shibuya があっても、渋谷の設置証拠にはしません。
- 写真ライセンス: [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/)。比較画像では写真のトリミング・縮小を行いました。写真をモデルのテクスチャには使用していません。
- モデルとPythonは本プロジェクトのための新規生成物です。参照写真の権利表示は写真および比較画像と共に保持してください。

## 寸法・座標と推定
- 外接寸法: 幅 1.280 m、奥行 0.441 m、高さ 1.920 m。すべて制作上の仮定で、実測ではありません。
- 胴体: 幅 1.23 m、奥行 0.37 m、高さ 1.83 m。写真の正面比率と浅い箱形を参考にしました。
- Blender: メートル、Z上、正面−Y。外接底面の中央を原点 (0,0,0)。GLBは標準Y上へ変換。
- 写真から読める特徴: 全面の密な横リブ、左寄り上部3区画枠、下部サービス枠、左側面の上部グリル、上端の薄い張り出し。
- 推定部分: 全絶対寸法、底部の厚さ、遮蔽された下部枠の右側構成、左右の対応、背面。背面は無地とし、内部構造・用途・メーカーは推定しません。
- 写真の汚れ、傷、枯葉、側面の色むら、判読不能な金具は再現していません。写真より清潔で均一な材質です。上面の明るさも撮影照明と一致しません。

## 内容と再生成
- incoming の GLB: 1設備箱、1メッシュノード。カメラ・照明・床・他の小物なし。
- blend: 部材別に編集可能な原本。ASSETコレクションのみがモデル。STUDIOは確認画像の床・照明・カメラで、書き出し対象外。
- Python: 外部画像・ライブラリ不要。出力先はスクリプトと同じフォルダー。
- Blender 4.2.3 で実際に生成・GLB書き出し・レンダリング・保存・再読込検証を実施。異なるバージョンではスクリプトが明示的に停止します。

再生成:

    blender-4.2.3 -b --threads 8 --python-exit-code 1 -P generate_grey_cabinet.py

公式 Linux x64 配布のSHA-256:

    3a64efd1982465395abab4259b4091d5c8c56054c7267e9633e4f702a71ea3f4

配布元: https://download.blender.org/release/Blender4.2/blender-4.2.3-linux-x64.tar.xz
照合元: https://download.blender.org/release/Blender4.2/blender-4.2.3.sha256

## リポジトリ取込との関係
main には props 取込基盤が未マージのため、この変更は incoming/source/evidence の素材保管のみです。web/layout、ランタイム、配置情報は変更しません。

PR #38 系列の `claude/core-exterior-review`、コミット `c00c7db` の `tools/props/import_prop.py` を別作業領域で使用して、Blender 4.2.3による実際の取込テストを行いました。取込処理そのものは本変更へコピーしません。基盤マージ後に、同じspecから再実行してください。

    blender-4.2.3 -b --python-exit-code 1 -P tools/props/import_prop.py -- assets/street/props/source/data/specs/grey_louvered_cabinet.json assets/street/props/incoming/grey_louvered_cabinet/grey_louvered_cabinet.glb /tmp/grey_louvered_cabinet.glb /tmp/import_report.json

取込結果: 本体2,484三角形、LOD1 621三角形、上限4,000内、倍率1.0。LODは同じGLB中の別ノードです。汎用ビューアで両方同時に描画すると重なるため、LOD対応ローダーで切り替えてください。incoming はLODなしの原本で、この問題はありません。

## 視覚確認と残差
比較画像は「参照写真」と「写真に近い斜め視点」を横に並べています。カメラは目視近似で、校正済み一致・測量精度・場面との合成ではありません。輪郭と上部枠の比率を優先し、初回の明るすぎる色を暗い灰色へ修正し、左側面が見える角度を調整しました。正面・側面は直交投影です。実景の材質汚れ、レンズ歪み、遮蔽の再現は未達です。

実景への配置には、対象シーン内での存在と位置を示す別の根拠が必要です。
