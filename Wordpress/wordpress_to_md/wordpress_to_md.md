あなたはフロントエンドに強いシニアエンジニア兼、開発体験を重視するUXエンジニアです。  
これから、**WordPressのエクスポートXML（WXR）を、記事ごとのMarkdownファイル(.md)に変換するローカルWebツール**を作ってください。

## ゴール・全体像

- ローカルのブラウザだけで動くシンプルなツールにしてください。
- ユーザーは以下の流れで使えるようにします：
  1. ブラウザで `converter.html` を開く
  2. 画面上の「XMLファイルを選択」ボタンから、WordPressのエクスポートXMLファイルを指定
  3. 「変換開始」ボタンを押す
  4. カテゴリごとにフォルダ分けされたMarkdownファイル一式をZIPでダウンロードできる

- サーバーやPythonは一切使わず、**HTML + JavaScript（＋必要ならCSS）だけ**で完結させてください。

## 仕様詳細

### 1. ファイル構成

- 出力は **単一のHTMLファイル**（例：`wp-xml-to-md.html`）に全てのコードをまとめてください。
  - 外部JS/CSSへの依存を極力減らしてください。
  - ただし、どうしても必要なら以下のようなCDN利用はOKです（その場合は `<script>` タグをHTML内に記述）：
    - HTML→Markdown変換用ライブラリ（例：Turndown）
    - ZIP生成用ライブラリ（例：JSZip）

### 2. 画面UI

シンプルでOKですが、最低限以下を実装してください。

- 要素：
  - アプリのタイトル：例）「WordPress XML → Markdown 変換ツール」
  - `input type="file"`：WordPress export XMLを1ファイル選択
  - 「変換開始」ボタン
  - ステータス表示用テキストエリア or ログ表示領域
    - 何件の記事を読み込んだか
    - どのカテゴリ/ファイル名で出力したか
    - エラーがあればメッセージ表示

### 3. 対応するWordPress XML（WXR）の想定

- 典型的なWordPressエクスポートXML（WXR）を前提としてください。
- 構造の例：
  - ルート： `<rss><channel>...<item>...</item>...</channel></rss>`
  - 記事は `<item>` 要素
  - 主に使うフィールド：
    - タイトル：`<title>`
    - 本文HTML：`<content:encoded>`
    - 投稿日：`<wp:post_date>` または `<pubDate>`
    - スラッグ：`<wp:post_name>`
    - 投稿タイプ：`<wp:post_type>`（post, pageなど）
    - ステータス：`<wp:status>`（publishなど）
    - ID：`<wp:post_id>`
    - カテゴリ／タグ：`<category>` 要素
      - `domain="category"` のもの → カテゴリ
      - `domain="post_tag"` のもの → タグ

### 4. 変換対象のフィルタリング

- デフォルトでは以下のみをMarkdownとして出力してください：
  - `wp:post_type = "post"` のもの（＝通常の投稿）
  - `wp:status = "publish"` のもの（公開済み記事）
- その他（下書き、固定ページなど）は一旦スキップでOKですが、後から拡張しやすいようにコメントを入れてください。

### 5. Markdownファイルの構造

各記事ごとに1ファイルのMarkdownを生成してください。

#### 5-1. ファイル名ルール

- ベース案：
  - `YYYY-MM-DD-slug.md`
- 例：
  - 投稿日が `2023-05-01 10:30:00`
  - スラッグが `my-first-post`
  - → `2023-05-01-my-first-post.md`
- もしスラッグが空、または存在しない場合は、タイトルをスラッグ化した文字列を使ってください。
  - 日本語タイトルなどは、簡易で構わないので以下のように変換：
    - 全角→半角
    - 空白→ハイフン
    - 記号類を削除
    - 小文字化

#### 5-2. フォルダ構造（カテゴリ分け）

- ZIP内は、カテゴリごとにフォルダ分けしてください。
- 仕様：
  - `domain="category"` の `<category>` 要素からカテゴリ名一覧を取得
  - 複数カテゴリがある場合：
    - とりあえず「1つ目のカテゴリ」をメインとして使う
    - 残りはfront matterの `categories:` 配列に入れる
  - カテゴリが1つもない場合：
    - `uncategorized` というフォルダに入れる
- フォルダ名は、カテゴリ名をスラッグ化したものを使う（英数字・ハイフンのみなどに正規化）
  - 例：`恋愛コンサル` → `rennai-consulting`
- フォルダパス例：
  - `rennai-consulting/2023-05-01-my-first-post.md`

#### 5-3. Front Matter（YAML）

Markdownファイルの先頭にYAML front matterをつけてください。

```yaml
---
title: "記事タイトル"
date: "2023-05-01 10:30:00"
slug: "my-first-post"
status: "publish"
post_type: "post"
wordpress_id: 123
categories:
  - "カテゴリ名1"
  - "カテゴリ名2"
tags:
  - "タグ1"
  - "タグ2"
---
