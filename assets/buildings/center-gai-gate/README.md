# センター街入口ゲート — 写真の形を参考にしたB試作

センター街入口のアーチ型構造を、2025-01-31のStream写真（Syced、CC0）を参考に自作。支柱2本、滑らかな曲線フレーム、湾曲した掲示面と小さな照明器具を通常表示へ追加する。既存のQFRONT・西側街区・街路設備を変更せず、別の資産として読み込む。

OSMやPLATEAUで確認した設備IDではないため、source_idはphoto/center-gai-entrance-gate。足元の位置はQFRONTと西側街区の間の通路へ推定配置。広告・テナントの文字・ロゴは貼っていない。黄色い面は掲示面の構造表現で、2025年10月の広告を認定しない。将来の広告は別GLBレイヤーにする。

2025年11月の夜写真（Joli Rumi、CC BY-SA 4.0）は街の照明の文脈のみで、ゲート自体を独立同定した資料ではない。写真をモデルテクスチャに使っていない。出典とハッシュはsource/refs/REFERENCE_REGISTER.csv。地面は国土交通省Project PLATEAU渋谷区2025年度モデルを加工した既存C2a資産で、出典・条件はSOURCE.json。

ブラウザの高さはT.P.−15、viewer.jsonのgroundElevationTP=15。支柱位置(-31.2,36.0)、(-23.0,35.0)は未実測。周辺各5点、合計10/10点がC2a地面に当たり、足元中央値はT.P.15.270 / 15.326 m。台座の下を近傍最小地面より0.025 m下げて接地。地面種別の確認で左5点はground_road、右5点はground_fill（補填面）。これは既存モデルへの接触であり、右側の現地実測標高を確認したものではない。通路幅は約8.261 m、掲示面の最小下端は高い側の足元から約4.276 m。数値は試作寸法で、現地測量ではない。

夜は器具の自発光だけ。道路や壁へ当たる光・実光量は未調整。通常building一覧へ読み込むが、street=offでゲートも非表示にする。context=nostationでもゲートは残る。PLATEAUの同じ形を置き換えたものではないので、Cの除外は追加していない。

## 再生成

```bash
source /workspace/setup-tools/core-env.sh
blender -b --python-exit-code 1 -t 4 -P assets/buildings/center-gai-gate/source/blender/build_gate.py -- assets/buildings/center-gai-gate/source/data/layout.json assets/ground/core/web/ground_core.glb assets/buildings/center-gai-gate/web
```

生成にはBlender4.2.3の標準glTF書き出しだけを使う。layout.jsonの設定・地面の照会・再生成統計を保存。位置、支柱間隔、高さ、掲示面の厚さ、文字と広告、光量、10月の状態は未確認で、写真品質の完成・Gate合格ではない。

初版の掲示面色はRGB(0.74,0.60,0.025)、補正後は(0.90,0.72,0.003)。位置・形・光は固定。設定をevidence/c2-center-gai-gate/{first,after}/layout.jsonへ保存し、別フォルダへコピーして別の出力先で再生成できる。stats.jsonは渡したlayoutの隣へ保存される。
