# ハチ公背後の白いボラード（独立素材、未配置）

承認済みの白い円柱＋黄色帯の形状を Blender 4.2.3 LTS で再生成した。実測復元ではない。全高 0.800 m、本体径 0.114 m は作業上の仮定。帯厚 0.0001 m により最大外径は 0.1142 m。根元と下部は写真で隠れ、同径の直管・平底で補完した。帯高 0.080 m、天端から帯上端 0.100 m は写真の径との比率からの概算で、仮定径に依存する。キャップ高 0.010 m・縁半径 0.002 m は推定。

文字、接続金具、柵、地下基礎、道路は作っていない。材質・色は近似、帯は物理的な再帰反射材ではない。写真は2025年7月13日。駅前の目標時点である2025年10月の外観を確認したとは扱わない。

- incoming の GLB が正本。1資産、3メッシュ、2材質、2,676三角形。カメラ・ライトなし。
- source/blender/hachiko_white_bollard の圧縮 blend は編集用。スタジオのカメラ・ライトを含むが背景メッシュはない。
- Blender は Z-up、GLB は標準 Y-up。再読込時の Blender Z=0 が底面、原点は底面中央。
- PR #38 の importer で材質名を prop_furniture_0/1 に正規化できることを検証した。incoming 自体は再生成しやすい記述的な材質名を保持する。
- importer は検証にコピーを用いた外部依存で、この資産PRには追加しない。main に未導入なら、先に該当 importer が利用可能なブランチで検証する。
- importer 出力は LOD0 と LOD1 が同じ場所に存在する。検証用だけであり、このPRに同梱しない。これを incoming の正本へ再入力しない。
- web/、layout、配置、レール、既存シーンに変更なし。既存ハチ公周囲のレール等へ重複配置しない。

## 再生成（リポジトリルートで実行）

Blender 4.2.3 LTS と Python 3 が必要。比較画像の生成だけは Pillow と CJK フォントも必要。BLENDER はインストール済み実行ファイルのパス、CJK_FONT は任意の日本語フォントのパスにする。出力はリポジトリ外の新しい一時ディレクトリに書くので既存素材を上書きしない。

```sh
BLENDER=/path/to/blender-4.2.3/blender
P=assets/street/props
S="$P/source/blender/hachiko_white_bollard"
OUT="$(mktemp -d)"
"$BLENDER" -b -t 4 --factory-startup --python-exit-code 1 -P "$S/regenerate_bollard.py" -- --output "$OUT"
# 再生成した shibuya_bollard.glb と shibuya_bollard.blend を確認後、必要に応じて採用する。
# 次の検証には PR #38 の tools/props/import_prop.py が必要。
"$BLENDER" -b -t 4 --python-exit-code 1 -P tools/props/import_prop.py -- \
 "$P/source/data/specs/hachiko_white_bollard.json" "$OUT/shibuya_bollard.glb" \
 "$OUT/importer_validation.glb" "$OUT/importer_report.json"
python3 "$S/check_glb.py" "$OUT/shibuya_bollard.glb" "$OUT/importer_validation.glb" "$OUT/budget_report.json"
# 比較画像の再生成。既存証拠画像を上書きしない。
mkdir "$OUT/evidence"
cp evidence/props/hachiko_white_bollard/reference_*.jpg "$OUT/evidence/"
python3 "$S/make_comparison.py" --renders "$OUT" --evidence "$OUT/evidence" --font /path/to/Japanese-font.ttf
```

Cycles CPU・48サンプル・デノイズ無効。生成形状は旧承認版と同じ。固定カメラで正面・側面を撮影する。比較画像は単体の写真参照とモデルの比較で、シーンの前後比較や校正済みの写真測量ではない。

検証記録は source/data/reports/hachiko_white_bollard_*.json。npm test/typecheck/build は完全なリポジトリと依存環境がないため未実行。ランタイム表示・配置・FPSは未検証。

出典と利用条件は同じディレクトリの SOURCE_LICENSE.md を参照。
