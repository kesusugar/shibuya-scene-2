# 渋谷スクランブルスクエア: 既存モデルの累積分割訂正

main e6430b1a に既にある北面外装を維持し、納品済みの WallSurface77 と RoofSurface28/49/35 の三角形分割訂正をまとめたものです。新規建物・新たな北面制作ではありません。実際の凹部・壁81・元の輪郭・地面36点は保持。寸法・窓割り・スリット・フィン・材質は写真による近似であり、建物全体の正確さや2025年10月の全現況を認定しません。

## 現行データと再生成

- 通常表示: web/scramble-square.glb
- 現行編集シーン: source/roof35-repair-v1/updated.blend
- 生成器: source/roof35-repair-v1/repair.py
- 固定入力: 同フォルダの prior.glb / prior.blend、repair-config.json、source/data/plateau.json、source/refs の写真。
- Blender 4.2.3 に限定。任意の作業場所から次を実行し、別の空出力先を指定してください。

    blender -b -t 2 --python-exit-code 1 -P /path/to/scramble-square/source/roof35-repair-v1/repair.py -- --output-dir /empty/output

GLB はバイト一致。編集シーンは保存時メタデータが変わるためファイルハッシュ一致ではなく、全メッシュ・法線・ポリゴン・材質・変換・packed写真の一致を確認しました。写真は参考資料でありモデルのテクスチャではありません。実行ログ・Blender本体・ZIPは登録しません。

## main 比較と限定検証

source/cumulative-v1/main.glb は current main の元生成器をそのまま再実行し、Git blob d834645cdb7eb500133a700ac7cd7ac56d684b77 と一致確認した比較入力です。同所の main-generator.py はこの比較用であり、現行生成器ではありません。再実行には source/data の plateau.json / layout.json / pavement-baseline.json を作業コピーの data/ へ配置し、その隣に空の blender/ ディレクトリを事前に作成してください。第3引数へ unused、第4引数へ出力先を指定します。元スクリプトは入力隣の stats と blender シーンも出力するため本番フォルダでは実行しないでください。

最終 GLB は ff02d1bf8234c0bde5af1a82b5729a3d9bbaf77f、44,392三角形、10 primitive、2,930,876 bytes。B予算120,000/40/3,000,000内。全 off-target 三角形は main と一致し、対象4面は元の境界・面積を満たします。通常表示登録・source_id 除外・予算設定の変更は不要。QFRONT・西武・109・Takagi・歩行表示・FPS・他アセットは変更しません。

検証結果と実際の main 前後比較は evidence/cumulative-v1。front/side は既存カメラと診断用 Workbench 光源で撮影。historical-roof35-detail.jpg は直前の roof28/49段階からの16-byte変更だけを示す過去比較であり main 比較ではありません。全体ビルド・ブラウザ・FPS・他の屋根はこの検証の対象外です。

## 出典とライセンス

SOURCE_AND_LICENSE_JA.md と source/refs/FACADE_SOURCES.md を参照。CC0 / CC BY 4.0 / CC BY-SA 4.0 の写真を属性と加工内容付きで保持。2025年6月・9月は10月の証明とはしません。PLATEAU/OSMの既存出典条件を継承し、全体に単一ライセンスを付与しません。旧生成器や未列挙の既存ファイルは削除・上書きせず歴史資料として残ります。manifest は今回の公開対象だけの完全な一覧です。
