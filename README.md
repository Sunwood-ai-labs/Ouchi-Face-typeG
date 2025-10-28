# Ouchi Face

> おうちサーバーで動かす Hugging Face 風ポータル。ローカルのアプリやデータセット、リポジトリを可愛くまとめて即アクセスしよ〜！

## ✨ なにができるの？

- **リソース登録**: Gradio/Streamlit みたいなデモアプリの URL、NAS 上のデータセット、GitHub/Forgejo リポジトリをメタデータ付きで登録。
- **カード表示 & キーワード検索**: 登録したリソースをカードで一覧。名前検索＆種別フィルタで迷子知らず。
- **詳細ビュー**: アプリの起動リンク、ローカルパス、README プレビュー（GitHub/Forgejo なら自動取得）をひと目でチェック。
- **シンプルな API**: `/api/resources` から JSON で登録状況を取得できるから、他ツールとの連携もイージー。

## 🏗️ アーキテクチャ概要

| レイヤー | 使用技術 | 役割 |
| --- | --- | --- |
| Web アプリ | FastAPI + Jinja2 | リソース一覧・詳細・登録フォームを提供 |
| データ永続化 | SQLite (標準 `sqlite3` モジュール) | リソース情報をローカルファイルで保存 |
| README プレビュー | `requests` + `markdown` | GitHub / Forgejo から README をフェッチして Markdown → HTML 化 |

> 本当は Next.js でキメたいけど、オフライン環境向けに Python スタックで MVP をまとめたよ。将来の React 化も見据えた構成です。

## 🚀 クイックスタート

1. **依存インストール**
   ```bash
   uv sync  # または pip install -e .[test]
   ```

2. **サーバー起動**
   ```bash
   uv run uvicorn ouchi_face.main:app --reload --port 8000
   ```
   ブラウザで [http://localhost:8000](http://localhost:8000) を開くとポータルにアクセスできるよ。

3. **データベースの場所**
   - デフォルト: `data/ouchi_face.db`
   - 環境変数 `OUCHI_FACE_DB_PATH` をセットすると保存先をカスタム可能。

## 🧪 テスト

```bash
uv run pytest
```

## 📡 API スニペット

- 一覧取得: `GET /api/resources`
- 詳細取得: `GET /api/resources/{id}`

どちらもクエリパラメータ `q`, `resource_type` をサポート。`resource_type` は `app` / `dataset` / `repository` のいずれかだよ。

## 🗂️ テーブルスキーマ

| カラム | 型 | 説明 |
| --- | --- | --- |
| `id` | INTEGER | 主キー |
| `name` | TEXT | リソース名 |
| `resource_type` | TEXT | `app` / `dataset` / `repository` |
| `description` | TEXT | 説明文 |
| `link_url` | TEXT | 起動 URL や主要リンク |
| `location` | TEXT | NAS パスなど参考パス |
| `icon_url` | TEXT | サムネイル用 URL |
| `repo_url` | TEXT | GitHub / Forgejo リポジトリ |
| `created_at` | TEXT | ISO8601 形式の作成日時 |
| `updated_at` | TEXT | ISO8601 形式の更新日時 |

## 💡 運用 Tips

- README プレビューは外部ネットワークに接続できるときのみ取得。失敗しても画面でやさしくお知らせするよ。
- SQLite ファイルは `data/` 以下に保存されるから、バックアップはこのディレクトリごとコピーすれば OK。
- テスト実行時は一時 DB を使うようにしてるから、本番データが汚れる心配なし。

## 🛣️ 次の伸びしろ（ロードマップ）

- タグ＆カテゴリ機能
- 簡単ログイン（LAN 内パスコード）
- Docker Compose テンプレでの配布
- ローカルサービス自動ディスカバリ（mDNS / Docker ソケット連携）

おうち開発ライフ、もっとカラフルにしてこ〜ね！✨
