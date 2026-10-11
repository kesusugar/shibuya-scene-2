# 素材のライセンス一覧（写真以外）

写真のライセンスは `refs/REFERENCE_REGISTER.csv` にまとめてあります。写真は比較専用で、レンダーには一切使っていません。

| 素材 | 用途 | 出典 | ライセンス | 備考 |
|---|---|---|---|---|
| `hdri/wide_street_01.hdr`（4K） | 昼景で、ガラスに映り込む街並み（反射の光線にだけ使用） | Poly Haven、作者 Sergej Majboroda | CC0 | リポジトリには含めない（`.gitignore`）。取得手順は下記 |
| `hdri/shanghai_bund.hdr`（4K） | 夜景で、ガラスに映り込む街の灯り（反射の光線にだけ使用） | Poly Haven、作者 Greg Zaal | CC0 | 同上 |
| `textures/led_main.png`、`textures/art_text.png` | Q's EYE の映像 | 自作（スクリプトで生成した抽象ポスター） | — | 実在の広告ではない |
| DejaVu Sans / Sans Bold | QFRONT、STARBUCKS COFFEE、TSUTAYA の文字 | DejaVu Fonts | Bitstream Vera License（派生物を含め、再配布と利用が自由） | 実物のロゴ書体ではない（商標ロゴを複製しない方針） |
| IPAゴシック | 周囲のビルの、架空の看板の文字 | IPA | IPA フォントライセンス v1.0 | 看板の文言は一般名詞だけ（カラオケ、書店など）。ブランド名は使っていない |
| 人物、車、街灯、信号 | 通りのにぎわい | 自作（スクリプトで生成） | — | 実在の人物や車種を模していない |

## HDRI の取得手順
```
curl -s https://api.polyhaven.com/files/wide_street_01   # 4k の hdr の URL を取得
curl -s https://api.polyhaven.com/files/shanghai_bund
```
保存先は `hdri/<名前>.hdr` です。ファイルがない場合、スクリプトは HDRI なしで動きます（`nohdri` を指定した場合も同じ）。
