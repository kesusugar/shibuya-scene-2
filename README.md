# Shibuya Scene 2.0

実在の渋谷スクランブル交差点を、ブラウザで歩ける写真品質の街として作り直すプロジェクトです。
旧リポジトリ `kesusugar/shibuya-scene` は変更せずに残し、ゲーム機能の参照元として使います。

## 方針
- 静的な街並み → 歩ける街 → 人と車、の順に進めます。
- 群衆は最終的に 1,978 人を目指し、少人数から段階的に検証します。
- 再現する年代は 2025 年です。看板・広告・店舗は年代レイヤーとして分けて管理します。
- 建物は 1 棟ずつ独立した資産（`assets/buildings/<id>/`）として管理します。どれか 1 棟の読み込みに失敗しても、他の建物は消えないようにします。

## 現在のゲート
- G0：監査完了
- QFRONT v5：保全完了
- G1／G2：Three.js の新しいビューアで QFRONT を表示（オーナーの PC で問題なしを確認）
- **G3：2 棟目の MAGNET（2025 年）**。v1 を作成し、オーナーの確認待ち（`docs/G3_REPORT.md`）

## 資産
- `assets/buildings/qfront/`：QFRONT v5（品質基準）
- `assets/buildings/magnet/`：MAGNET by SHIBUYA109 v1。看板は 2025 年の年代レイヤー（`magnet_signs_2025.glb`）として分離
- `assets/buildings/eiraku/`：栄楽ビル（MAGNET の東隣。PLATEAU では MAGNET に含まれるが、別の建物として分離）

## ビューア
```
npm ci
npm run dev        # http://127.0.0.1:5180/
```
- `?buildings=qfront,magnet,eiraku`（既定）：建物を 1 棟ずつ独立に読み込みます。1 棟が失敗すると、その場所に赤い仮の箱が出て、他の建物は表示を続けます。
- `?view=q032`：QFRONT の写真 Q032 と同じ視点。`?view=m027`：MAGNET の写真 M027 と同じ視点。
- `?time=night`、`?q=low|medium|high`、30 秒計測ボタン。
