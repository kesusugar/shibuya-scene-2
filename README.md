# QFRONT v5 の完全バックアップ（2026-10-12）

制作プロジェクト `qfront-photoreal` の作業ディレクトリをまるごと固めたものです。Git 管理外のファイルもすべて含みます。
- 含まれるもの：v1〜v4 の描画画像、作業ファイル、ライセンス不明の写真 6 枚（内部参照用。再配布はしないこと）

あわせて、Git の全履歴を `qfront-photoreal-history.bundle` として保存しています。

## 復元の方法
```
cat qfront-photoreal-full-20261012.tar.gz.part* > qfront-photoreal-full-20261012.tar.gz
sha256sum -c SHA256SUMS
tar -xzf qfront-photoreal-full-20261012.tar.gz
git clone qfront-photoreal-history.bundle qfront-photoreal-git
```

このブランチは保管専用です。通常の開発では `main` を使ってください。
`git clone --single-branch` を使えば、このブランチを取得せずにクローンできます。
