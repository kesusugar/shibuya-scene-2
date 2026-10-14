# BIG ECHO / 渋谷平和ビル21-8（互換ID: quattro）

`way/136691389` は隣のmineo / 平和クワトロ21-9ではなく、BIG ECHOのある渋谷平和ビル21-8。既存のフォルダ名・source_id・座標は変更しない。raw plateau内の旧名称は誤同定の履歴で、現実の名称の根拠にしない。

## 今回の範囲
- 元の壁・屋根・接地スカート全三角形を保持。T.P.15 m基準、地面15.659、上端46.015 m、低い南西正面15.586–15.612 mと北東へ急に立ち上がる屋根を維持。
- 汎用8層・188枚の窓から、低い正面4層・24枚の主要ガラス区画へ。銀色枠、赤い大小筐体、無地の画面筐体、張出し看板の箱と取付金物、屋根の手すりを制作。
- 側面はクリームの壁、急勾配屋根は暗い金属面。WB01に見える下段の暗い開口と淡色の頬/縁、上段の茶色い庇、頂部の銀色フレーム開口/格子を原形の上へ追加。張出し深さと区割りは推定。見えていない面へ窓を並べない。
- 初稿レンダーを見て屋根の明るい横線を削り、目地を弱めた。下段画面は無地の窪んだ筐体へ補正。架空の広告・医療テナント名・古いシャッターは追加しない。
- `signs-2025-01.glb` はCC0写真の2枚の縦看板だけを含む別資産。**viewer.jsonには登録しない**。2025年1月の資料を無条件の通常表示へ混ぜない。

## 再生成
Blender **4.2.3 LTS**。作業ディレクトリに依存しない。

```sh
blender -b --python-exit-code 1 -t 4 -P assets/buildings/quattro/source/blender/build.py
# 別のディレクトリへ同じGLBを再生成する場合
blender -b --python-exit-code 1 -t 4 -P assets/buildings/quattro/source/blender/build.py -- /tmp/quattro-rebuild
```

全入力はsource/dataとsource/refsに含む。`source/blend/quattro.blend`は写真2枚をpack済み。日付レイヤーは別コレクションでviewport/renderとも無効。外部の公式写真や個人の絶対パスには依存しない。元のshell JSONは、基準GLBをBlender4.2.3で読み込んだ座標と面の完全な記録。

```sh
blender -b --python-exit-code 1 -t 4 -P assets/buildings/quattro/source/blender/render_evidence.py -- assets/buildings/quattro/web/quattro.glb /tmp/quattro-front.png front
# 第3引数はfront / side / photo / photo-january。最後だけは非登録の1月レイヤーを明示的に読み込む比較用。photoは参考写真に近い方向であって測量校正ではない。
npx vitest run tests/quattro-fidelity.test.ts
npx vitest run tests/neighbourhood.test.ts -t 'quattro|center244'
npm run typecheck
```

## 検証と限界
元のPLATEAU raw hash、全原形三角形、上端、低い正面、date layer非登録、B予算、出力三角形の平面とQFRONT/西武元footprintの交差を検査。QFRONT・西武の資産・runtime・共通予算は変更しない。元形状から西武A館まで約0.829 mなので後方には看板等を張り出さない。今回の検査は保護された元footprintに対するもので、保護資産の全装飾形状との衝突を証明するものではない。

正面の区切り・金物の実寸、全テナント・10月状態、屋根の見える突起の実寸/用途・隠れた設備、裏面は未達。比較の前後は同じカメラだが写真の正確な位置合わせではない。完成・写真精度合格とは認定しない。出典・権利・推定は[出典台帳](source/refs/SOURCES.md)を参照。

既存のreference.jpg・reference.jpg.json・emissive_day.json・emissive_night.jsonは変更/削除しない。今回の配布一覧は変更ファイルのみで、これらは既存リポジトリからそのまま引き継ぐ。
