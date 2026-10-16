# 第3段階残り・第4段階 一括レビュー記録（2026-10-17）

基準は `main` の `586dbf5990168bb383d07be83982973536f03263`（PR #83 まで）。従来資料の対象別PR・順番待ちは今回の一括指示で更新した。対象パッケージは [Drive素材索引](https://drive.google.com/file/d/1V2IyuNLkbBOGqhSG57f1nLV47rpxtMpa/view) と各同梱README・manifestから選んだ。ZIPと参照写真はリポジトリ外に保持し、8件すべての実ファイルサイズ、SHA-256、ZIP全CRC、manifest記載の内部ファイルを照合した。白柵ZIPにはmanifestにない `SHA256SUMS` が1件あるがCRCは検証済み。

| パッケージ | 実サイズ（byte） | ZIP SHA-256 |
| --- | ---: | --- |
| `a28_lottery_three_window_frontage_candidate_v002` | 7,631,875 | `ff737e17f8afaa82375be08af25e80b04e727442753323e32d87163563e2d2e7` |
| `a29_a8_entrance_shell_2025_v001` | 5,862,709 | `14379f1cda3007f001caa6086c89224bedf20bd8d45d76b5bcd1db349b7f504a` |
| `station_north_louver_frontage_v001_FRONT_ONLY` | 11,187,370 | `b816e35e149af2a188bdd843e58761c4b5cd0857c14b5d7e051c64a4fcb86ecc` |
| `hachiko_memorial_bilingual_v001_20261016` | 21,590,353 | `7bb7dc92af6928dfb2befdefccde44ca3ec1fe2327cd38d40c2e06336bc83a22` |
| `hachiko_rear_tree_candidate_v001_PROTOTYPE` | 36,521,679 | `3161c580ad2b8c9945c499d909232e2dabc1868f1e8b6b9ffd20e880a1bd46a9` |
| `hachiko_white_guardrail_detail_v001_PARTIAL` | 4,997,245 | `4dceec3743ef66109aa0a385530b86768daf89d865f0e7bc6df838eff7b6e2b5` |
| `hachiko_fan_paving_sample_v001` | 32,223,312 | `9142bb32135e90a2f77447d1c7f946cbba3ffc00062b8333c1995ba219c9beac` |
| `hachiko_rectangular_tactile_units_v001` | 24,319,491 | `2cb91c5451104a1a7de30f9b46af40b732a5e6248020289cd52d237f4be0444c` |

| 対象 | 判定 | 根拠と今回の処理 |
| --- | --- | --- |
| 宝くじ売場 v002 | 根拠不足で保留 | [v002](https://drive.google.com/file/d/1G06KvpHipMhSkpVu1e7udK0ouySU9fF_/view) は白い正面3窓と中央下枠の細い2脚を持つ。`placement_hint.json` のworld座標・回転はnull。既存 `plaza-facilities` と `plaza-kiosk` のどちらに対応するか未同定で、重複・誤置換の危険がある。ポスター等は制作しない。 |
| A8入口外観シェル | 根拠不足で保留 | 索引の `a29_a8_entrance_shell_2025_v001`。公式2025年資料でA8とBOX/JRは区別される。world座標・回転はnull、既存 `plaza-kiosk` との同一性は未証明。BOX/JR/交番をA8に改名・削除しない。地下や通路は作らない。 |
| 駅北側ルーバー可視正面 | 既存のまま、候補は保留 | `station_north_louver_frontage_v001_FRONT_ONLY` の2×4ベイは場所と片側/両側の選択が未確定。現行 `station-north` の14枚の暗色面と共有鋼材は個別面との対応がなく、全材質削除は他部位を消す。`station-service` の9スラット換気口、西高架とも別物。 |
| 記念碑・石碑 | 部分置換 | [二言語碑](https://drive.google.com/file/d/1vt5OAwlY00wnj6jCwUIGutHIGCeGUAcM/view) が既存 `hachiko-surround` の `stone_panel` と `unread_inscription` を明示的に置換する。旧2部品だけ生成を止め、旧パネルの像相対中心 `[-3.65,-1.25]` を幅1.60mの干渉回避のため外側へ0.35mずらした `[-4.00,-1.25]` とし、新しい足元6点の歩道標高から単一のGLB変換を算出。像スキャン・台座・左右石縁・レール・植栽は維持。幅1.60m、奥行0.22m、高さ0.82mは写真からの推定値。 |
| 大木・根元石囲い | 根拠不足で保留 | `hachiko_rear_tree_candidate_v001_PROTOTYPE` は背後の個体を対象とするが、囲い内の幹位置・向き・地面高は未記録。既存OSMの6本は別地点なので自動置換できない。パッケージに石囲い全体のモデルはない。 |
| 設置場所を同定できる柵 | 既存のまま、追加候補は保留 | `hachiko_white_guardrail_detail_v001_PARTIAL` は2025-07-13写真の左接合部0.57m幅の切片で、全ベイ・設置線・接地を含まない。既存の像周辺銀色レールと道路柵をそのまま維持。他地域の形状参考柵は採用しない。 |
| ハチ公周辺の舗装・縁石 | 既存のまま、追加候補は保留 | `hachiko_fan_paving_sample_v001` は90度の非シームレス試片で、world座標・実際の敷設範囲・段差がない。既存 `plaza-finish` と重ねると二重面になる。道路網・地面全体の標高は維持。 |
| 誘導ブロックと接地 | 既存のまま、追加候補は保留 | `hachiko_rectangular_tactile_units_v001` は部品展示用レイアウト。線形部品は `NOT_LOCAL`、world座標と経路端点がない。既存の通行・警告ブロックを維持。記念碑の足元だけ既存歩道接点で接地。 |

## 出典・時期・推定

- 記念碑前面の写真は [RuinDig/Yuki Uchida、2025-07-13、CC BY 4.0](https://commons.wikimedia.org/wiki/File:Tokyo-Shibuya-and-Shinbashi---2025-07-13_090.jpg)。写真投影を新規形状へ施した二次著作物。モデルは同梱 `PROVENANCE.md` によれば CC BY-SA 4.0。画像は碑面テクスチャとしてGLB内に埋め込み、元写真そのものは追加しない。
- A8の出典は渋谷駅周辺まちづくり関連の[2025年2月資料](https://shibuyaplusfun.pictona.jp/scc-admin/asset/shibuyaplusfun/000002/000002/38f57a3e.pdf)と[2025年8月資料](https://shibuyaplusfun.pictona.jp/scc-admin/asset/shibuyaplusfun/000002/000002/9ca91390.pdf)。撮影日は不明。
- 宝くじ売場の2025年公開写真は撮影日不明。ルーバーは2025-11-01、木の枝は2025-11、葉は2026-08、柵の接合部は2025-07の資料で、同時点の景観を示すものではない。通常表示には既存の異なる時期の資料も含まれる。
- 記念碑の位置は現地実測値ではない。施設同定は旧パネル置換指定に基づき、寸法と接地高さの推定は別に記録した。各候補のnull座標を0とは扱わず、非均等拡縮は行わない。

## 確認

`evidence/st3-st4/before` と `after` に同一カメラのPNGと `capture_log.json` を保存。碑正面・外側斜め・足元、像と石縁の全景、近隣施設を確認した。夜景は `after/surround_night.png`。旧パネルを画面内だけで再現する比較では、記録済みmainのGLBを読み、碑の表示を切っている。昼夜・GLB読込失敗なし、碑と石縁の非重複、碑の接地、像・台座・通路の維持を確認した。分類表示は既存 `applyClassPass` に新規rootを通し、形状分類テストとあわせて確認した。

WindowsではGitの自動CRLF変換で既存の固定SHA検査が失敗したため、Git記録と同じLFの作業コピーに戻して検証した。Python依存の既存検査はリポジトリ外のPython 3.12 + Shapely 2.2.0で実行。`npm test -- --maxWorkers=2 --testTimeout=30000` は58ファイル・257件成功。`npm run build` 成功。`tests/memorial.test.ts`、`tests/surround.test.ts` と既存予算検査は9件成功。性能上限は変更していない。
