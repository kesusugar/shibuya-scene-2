# 点字誘導：交差点アプローチと広場接続の試作

3本の既存横断歩道の両端、計6か所に警告用0.6×0.6 mと幅0.3 m・長さ1.8 mの
誘導用ブロックを追加する。25個の点状突起・4本の線状突起を立体で制作。
連続した実際の誘導ネットワークやバリアフリー適合を認定する資産ではない。

位置は横断歩道の測定端点・外向きの軸を使う規則による推定。
全タイルがC2a歩道に収まり、出入口のOSM平面範囲、樹木の根元、既存支柱から
離れる位置を探索する。仮補填面・車道には置かない。元の地面と街路設備は保持。
GLBは共通T.P.15 m基準で、基面に描画用2 mmのオフセット、突起は5 mm。
元の地形を歩行・衝突の基準として保持し、小さな突起を障害物へ追加しない。

```bash
source /workspace/setup-tools/core-env.sh
blender -b --python-exit-code 1 -t 4 -P assets/street/tactile/source/blender/build_tactile.py -- assets/street/tactile/source/data/layout.json assets/ground/core/source/data/crosswalks_measured.json assets/street/core/source/data/street_input.json assets/ground/core/web/ground_core.glb assets/street/tactile/web/tactile.glb assets/street/tactile/source/data/stats.json
python3 assets/street/tactile/source/tools/write_manifest.py
npm test
npm run build
```

`street_input.json`と同じフォルダの`street_layout.json`も支柱回避に使う。
既存の地面・街路GLBを再生成する必要はない。
通常表示で独立してロードし、street=off / ground=off / tactile=offでは除外する。
出典はsource/refs/SOURCES.json。実際の配置・接続先・10月の全経路・色は未検証。


## 広場接続（PR #25後）

元の60枚と6か所の配置を保持し、ハチ公側2か所を延ばして分岐部で接続する。
164枚（元60＋追加104）。分岐の警告面は3×3枚、0.9×0.9 m。
分岐中心は既存2本のアプローチ軸線の交点で、南側は2方向の平均軸へ9 m延ばす。
経路・分岐の座標は推定で、南端を実施設の入口へ接続したとは扱わない。

誘導面と突起を警告面の外形で切り詰め、重ねて描かない。
`assets/ground/core/source/blender/paving_boundary.py`の純粋な幾何処理を再利用する。
点字GLBだけを再生成し、元の地面・建物・街路設備は保持する。
テストは実GLBの平面上の経路接続と警告面内の線状突起の重なりを検証するため、
既存開発環境のPython・shapelyも使用する。
