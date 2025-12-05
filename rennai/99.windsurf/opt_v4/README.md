# THE ONLY ONE - オプトインLP

このリポジトリには、誠実な男性のための恋愛戦略LP「THE ONLY ONE」の静的ファイルが含まれています。`index.html` と同フォルダの CSS / JS をそのままホスティングするだけで動作します。

## ローカルで確認する方法

### 1. VS Code Live Server 拡張を利用
VS Code をお使いの場合、[Live Server](https://marketplace.visualstudio.com/items?itemName=ritwickdey.LiveServer) 拡張をインストールし、`index.html` を右クリック → **Open with Live Server** を選択してください。

### 2. Python 組み込みサーバーを利用
Python がインストール済みであれば、以下コマンドで簡易サーバーを起動できます。
```bash
# Windows PowerShell で実行（同ディレクトリを Cwd に指定してください）
python -m http.server 8000
```
ブラウザで `http://localhost:8000` にアクセスすればページを確認できます。

## ディレクトリ構成
```
opt_v4/
├── index.html         # LP 本体
├── styles.css         # デザインシステム・レイアウトスタイル
├── script.js          # モーダル・アコーディオンなどのインタラクション
├── assets/            # 画像素材（プレースホルダーを含む）
└── README.md          # このファイル
```

## マイスピー フォーム埋め込み
`index.html` 内の `<iframe class="myasp-form-placeholder">` を、マイスピーが発行するフォーム埋め込みコードに差し替えてください。

フォーム下のボタン `.form-btn` は CTA ボタンと同じオレンジ (`#f4a118`) にスタイリング済みです。必要に応じてフォーム側で自動送信後の遷移を設定してください。
