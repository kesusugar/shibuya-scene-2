# 高木ビルディング：既存実装の累積修正

PR35/36で実装済みの高木ビルディングを更新するもので、新規建物ではありません。比較元は main b678e9364a2cb6fd8dd2869b3b5ee195c86bbe39 の実ファイルです。

## 通常表示と2025年1月看板
- 通常表示 web/takagi.glb は上層外壁、折れ屋根リブ、source52の三角形分割を修正。4,750三角形・12プリミティブ・381,208バイト。
- **通常表示では既存の黒い簡略屋上看板24三角形を除去します。IKEA看板は通常表示へ追加しません。**
- web/signs-2025-01.glb は169三角形・4プリミティブ・16,900バイト。2025年1月31日写真を参考にした歴史的IKEA看板です。現時点や2025年10月の存続を保証しません。
- viewer.json の layers は未登録。現行ローダーは登録した全レイヤーを自動表示するため、年代が合わない看板を通常表示しないようにしています。グローバルの表示・歩行・FPSコードは変更していません。
- January比較は両GLBを同じ原点へ重ねた検査表示です。Blenderでは二つを同時importするか、下記render_runtime.pyを実行。座標の移動、再中心化、接地オフセットの追加は不要です。
- 将来、明示的に2025年1月表示を採用する場合のみ viewer.json に layers: { signs_2025_01: "signs-2025-01.glb" } を登録できます。これは現行ローダーでは常時有効化になり、年代切替ではありません。本候補では登録しません。
- 両ファイル合計は4,919三角形・16プリミティブ・398,108バイト。manifest.stats は既存budgetテストに合わせ全web GLB合計、runtime_statsは通常表示のみです。

## 根拠・推定
source/cumulative-v2/NOTES.md と references/SOURCES.md に出典、寸法推定、権利を記録。写真はSyced撮影2025-01-31、CC0。モデルの窓割・看板寸法・支柱・書体は推定、公式ロゴデータではありません。写真のCC0は商標やモデル全体のライセンスではありません。既存PLATEAU/OSM等の条件を継承します。

## 再生成・編集
Blender 4.2.3で実行：

    blender -b -t 4 --python source/blender/build.py

source/cumulative-v2 は納品ZIPの相対配置をそのまま維持した正本です。元モデル→外壁/屋根→IKEAの2段階を再生成し、固定SHA256を照合後、Python標準ライブラリで属性バイトを変更せず建物と看板を分離します。従来のsource/data/layout.jsonは履歴として残り、この生成経路では使いません。

元の編集用完成blendは source/cumulative-v2/asset/source/blender/takagi.blend 。これはIKEAを含む合成モデルで、元の397,924バイトGLBとバイト一致再exportを検証済みです。source/blender/takagi.blend は通常表示の建物だけをimportした編集用。分離GLBの正本生成はsplit_runtime.pyで、編集用blendの再exportバイト一致は主張しません。

    blender -b -t 4 --python source/cumulative-v2/render_runtime.py
    python tests/test_takagi_cumulative.py  # repository rootから

## 検証・限界
source/cumulative-v2/review/main-default-january.jpg は実main／通常表示／任意January表示を同一カメラ・照明で比較。写真カメラ較正・交差点全景・ブラウザ・歩行・衝突・FPS・全シーン予算は未検証です。
元の屋根7三角形だけが新しい折れ屋根仕上げ材料へ移り、source52以外の屋根頂点順序は保持。source52は17頂点を保持し15三角形へ再分割。既存屋根回帰テストはTakagiのこの材料だけを追加対象とし、座標・接地・C親除外のassertionを保持しています。
