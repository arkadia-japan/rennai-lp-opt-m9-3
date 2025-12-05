# OCR to Google Docs 自動化ツール

画像ファイルやPDFからOCRでテキストを抽出し、自動的にGoogle Docs/Driveに保存するWindowsアプリケーションです。

## ⚠️ 重要な注意事項

**このツールは、あなたが権利を持つコンテンツにのみ使用してください。**

- DRMで保護されたコンテンツの処理は違法です
- 著作権で保護された商業コンテンツの無断複製は禁止されています
- 利用規約に違反するコンテンツには使用しないでください
- 個人所有の文書、自分で作成したコンテンツ、権利処理済みの資料にのみ使用すること

---

## 機能

✅ 画像（JPG/PNG/TIF）とPDFのOCR処理
✅ 日本語・英語の混在文書対応
✅ テキスト自動整形（見出し検出、ページ番号除去など）
✅ ファイル名の自動生成（先頭10文字ベース）
✅ Google Docsドキュメント作成
✅ PDF/TXTファイルも自動生成してDriveに保存
✅ 大量ファイルのバッチ処理
✅ エラー時の安全な中断・再開機能
✅ 詳細なログ出力

---

## システム要件

- **OS**: Windows 10/11
- **Python**: 3.11 以上
- **必須ソフトウェア**: Tesseract-OCR
- **必須アカウント**: Googleアカウント（Google Drive/Docs API有効化）

---

## セットアップ手順

### 1. Tesseract-OCRのインストール

#### ダウンロード

1. [Tesseract公式リリースページ](https://github.com/UB-Mannheim/tesseract/wiki) にアクセス
2. 最新のWindows用インストーラをダウンロード
   例: `tesseract-ocr-w64-setup-5.3.3.20231005.exe`

#### インストール

1. ダウンロードしたインストーラを実行
2. **重要**: インストール時に「Additional language data」で **Japanese** と **English** を選択
   - デフォルトでは英語のみなので、必ず日本語を追加してください
3. インストール先はデフォルト推奨:
   `C:\Program Files\Tesseract-OCR`

#### パス確認

インストール後、以下のパスに実行ファイルがあることを確認:

```
C:\Program Files\Tesseract-OCR\tesseract.exe
```

コマンドプロンプトで動作確認:

```cmd
"C:\Program Files\Tesseract-OCR\tesseract.exe" --version
```

### 2. Pythonのセットアップ

#### Python 3.11+ のインストール

[Python公式サイト](https://www.python.org/downloads/) から最新版をダウンロードしてインストール。

**重要**: インストール時に「Add Python to PATH」にチェックを入れること。

#### 仮想環境の作成

プロジェクトフォルダで以下を実行:

```cmd
python -m venv .venv
```

#### 仮想環境の有効化

```cmd
.venv\Scripts\activate
```

（有効化されると、プロンプトの先頭に `(.venv)` が表示されます）

#### 依存ライブラリのインストール

```cmd
pip install -r requirements.txt
```

---

### 3. Google Cloud プロジェクトのセットアップ

#### プロジェクト作成

1. [Google Cloud Console](https://console.cloud.google.com/) にアクセス
2. 新しいプロジェクトを作成（例: `ocr-to-docs`）

#### APIの有効化

プロジェクト内で以下のAPIを有効化:

1. **Google Docs API**
   - [有効化リンク](https://console.cloud.google.com/apis/library/docs.googleapis.com)
2. **Google Drive API**
   - [有効化リンク](https://console.cloud.google.com/apis/library/drive.googleapis.com)

#### OAuth 2.0 クライアントIDの作成

1. [認証情報ページ](https://console.cloud.google.com/apis/credentials) に移動
2. 「認証情報を作成」→「OAuth クライアント ID」を選択
3. アプリケーションの種類: **デスクトップアプリ**
4. 名前: 任意（例: `OCR Desktop Client`）
5. 作成後、**JSONをダウンロード**

#### credentials.json の配置

1. ダウンロードしたJSONファイルを `credentials.json` にリネーム
2. プロジェクトの `secrets/` フォルダに配置

```
project/
  ├─ secrets/
  │   └─ credentials.json  ← ここに配置
  ├─ main.py
  └─ ...
```

---

### 4. 環境変数の設定

`.env.sample` をコピーして `.env` ファイルを作成:

```cmd
copy .env.sample .env
```

`.env` ファイルを編集:

```ini
# Tesseract設定
TESSERACT_EXE=C:\Program Files\Tesseract-OCR\tesseract.exe
TESSERACT_LANG=jpn+eng

# Google Drive フォルダID（オプション）
DOCS_FOLDER_ID=
PDF_FOLDER_ID=
TXT_FOLDER_ID=

# OCR設定
OCR_DPI=300
MAX_IMAGE_SIZE=3000

# ログ設定
LOG_LEVEL=INFO
LOG_RETENTION_DAYS=30
```

#### DriveフォルダIDの取得方法（オプション）

特定のフォルダに保存したい場合:

1. Google Driveで保存先フォルダを開く
2. URLから以下の部分をコピー:
   ```
   https://drive.google.com/drive/folders/【ここがフォルダID】
   ```
3. `.env` の該当項目に貼り付け

例:
```ini
DOCS_FOLDER_ID=1AbCdEfGhIjKlMnOpQrStUvWxYz
PDF_FOLDER_ID=1AbCdEfGhIjKlMnOpQrStUvWxYz
TXT_FOLDER_ID=1AbCdEfGhIjKlMnOpQrStUvWxYz
```

---

## 使い方

### 初回実行（OAuth認証）

初回実行時のみ、ブラウザでGoogleアカウント認証が必要です。

```cmd
.venv\Scripts\activate
python main.py
```

1. ブラウザが自動的に開きます
2. Googleアカウントでログイン
3. アプリケーションへのアクセスを許可
4. 「認証が完了しました」と表示されたらブラウザを閉じてOK

認証が完了すると、`token.json` が自動生成され、以降は認証不要になります。

### 基本的な使い方

1. **入力ファイルを配置**

   `input/` フォルダに処理したい画像やPDFを配置:

   ```
   input/
     ├─ scan001.pdf
     ├─ photo001.jpg
     └─ document.png
   ```

2. **実行**

   ```cmd
   python main.py
   ```

3. **結果確認**

   - Google Driveに以下が作成されます:
     - `{prefix}_doc` (Googleドキュメント)
     - `{prefix}.pdf` (PDFファイル)
     - `{prefix}.txt` (テキストファイル)

   - ローカルの `output/` フォルダにもPDF/TXTが保存されます

4. **処理済みファイル**

   成功したファイルは `input/` から自動削除されます。
   失敗したファイルは残るため、再度処理できます。

### コマンドラインオプション

```cmd
# デフォルト（日本語+英語）
python main.py

# 英語のみ
python main.py --lang eng

# 日本語のみ
python main.py --lang jpn

# 高解像度PDF処理（600dpi）
python main.py --dpi 600

# フォルダ監視モード（常駐）
python main.py --watch
```

---

## ファイル名ルール

OCR結果の **先頭10文字** から自動生成されます。

### 例

| OCR結果の冒頭 | 生成されるプレフィックス |
|---------------|-------------------------|
| 「幸せ」から考える哲学入門... | `幸せから考える哲` |
| Chapter 1: Introduction to... | `Chapter1In` |
| （空白・記号のみ） | `converted_20250106_153045` |

### ルール

- 使えない文字（`\ / : * ? " < > |`）は `-` に置換
- 空白・改行は除去
- 先頭10文字が無効な場合は `converted_{日時}` を使用
- Drive上に同名ファイルがある場合は `_v2`, `_v3` を自動付与

---

## トラブルシューティング

### Tesseractが見つからない

**エラー例:**
```
Tesseract executable not found at C:\Program Files\Tesseract-OCR\tesseract.exe
```

**解決策:**
1. Tesseractが正しくインストールされているか確認
2. `.env` の `TESSERACT_EXE` パスが正しいか確認
3. 実際のインストール場所に合わせて修正

### 日本語が認識されない

**原因:** Tesseractの日本語言語データが未インストール

**解決策:**
1. Tesseractを再インストール
2. インストール時に「Additional language data」で **Japanese** を選択
3. または、手動で言語データをダウンロード:
   - [tessdata リポジトリ](https://github.com/tesseract-ocr/tessdata)
   - `jpn.traineddata` をダウンロード
   - `C:\Program Files\Tesseract-OCR\tessdata\` に配置

### Google API認証エラー

**エラー例:**
```
FileNotFoundError: 認証ファイルが見つかりません: secrets/credentials.json
```

**解決策:**
1. `secrets/` フォルダを作成
2. Google Cloud Consoleからダウンロードした `credentials.json` を配置
3. ファイル名が正確に `credentials.json` であることを確認

### PDFが処理できない

**エラー例:**
```
Unable to get page count. Is poppler installed and in PATH?
```

**解決策（Windows）:**
1. [Poppler for Windows](https://github.com/oschwartz10612/poppler-windows/releases/) をダウンロード
2. 解凍したフォルダの `bin/` を環境変数PATHに追加
3. またはpopplerパスを明示的に指定:
   ```python
   # ocr.py の convert_from_path 呼び出し時に追加
   images = convert_from_path(str(pdf_path), dpi=dpi,
                             poppler_path=r'C:\path\to\poppler\bin')
   ```

### 大きなファイルで失敗する

**症状:** 10万文字以上のドキュメントでエラー

**解決策:**
- 自動でチャンク分割処理されますが、それでもエラーが出る場合:
  - `docs_drive.py` の `chunk_size` を小さくする（デフォルト900000）
  - 画像を分割して複数回処理する

---

## ディレクトリ構造

```
project/
├─ input/              # 処理対象ファイルを配置
├─ output/             # PDF/TXT出力先
├─ tmp/                # 一時ファイル・状態保存
├─ logs/               # ログファイル
├─ secrets/            # Google API認証情報
│   └─ credentials.json
├─ tests/              # テストコード
├─ main.py             # メインスクリプト
├─ ocr.py              # OCR処理
├─ cleaning.py         # テキスト整形
├─ naming.py           # ファイル名生成
├─ docs_drive.py       # Google API操作
├─ requirements.txt    # 依存ライブラリ
├─ .env                # 環境変数設定
└─ README.md           # このファイル
```

---

## 高度な使い方

### 見出しスタイルのカスタマイズ

`cleaning.py` の `detect_headings()` 関数で見出し検出ルールをカスタマイズできます。

例: 「●」で始まる行を見出しレベル2にする
```python
heading_patterns = [
    (r'^■', 1),        # ■ → レベル1
    (r'^●', 2),        # ● → レベル2  ← 追加
    (r'^【.+】', 1),
    # ...
]
```

### カスタムOCR設定

より高精度なOCRが必要な場合、`ocr.py` の `preprocess_image()` 関数をカスタマイズ:

- **ノイズ除去を強化**: `cv2.medianBlur(gray, 5)` (3→5に変更)
- **コントラスト強調**: `cv2.equalizeHist(gray)` を追加
- **シャープニング**: `cv2.filter2D()` でシャープ化

### バッチ処理の自動化

Windowsタスクスケジューラで定期実行:

1. タスクスケジューラを開く
2. 「基本タスクの作成」
3. トリガー: 毎日深夜など
4. 操作: 「プログラムの起動」
   - プログラム: `C:\path\to\project\.venv\Scripts\python.exe`
   - 引数: `main.py`
   - 開始場所: `C:\path\to\project\`

---

## ログの確認

ログは `logs/` フォルダに日付ごとに保存されます。

```
logs/
├─ app_2025-01-06.log
├─ app_2025-01-07.log
└─ ...
```

エラーが発生した場合は、該当日のログファイルを確認してください。

---

## パフォーマンス

### 処理速度の目安

- **A4 1ページ (画像)**: 約10-20秒
- **A4 10ページ (PDF)**: 約2-3分
- **100ページ以上**: 10分以上

※ファイルサイズ・画質・テキスト量により変動

### 高速化のヒント

1. **DPI を下げる**: `--dpi 200` (デフォルト300)
2. **画像を事前圧縮**: 大きすぎる画像は事前にリサイズ
3. **並列処理**: 複数ファイルを同時実行したい場合は、複数のコマンドプロンプトで実行

---

## セキュリティとプライバシー

- **認証トークン**: `token.json` には認証情報が含まれます。第三者に共有しないでください
- **credentials.json**: Google Cloud Consoleからダウンロードしたファイル。Gitにコミットしないでください（`.gitignore`で除外済み）
- **入力ファイル**: 成功時に自動削除されますが、機密情報を含む場合は処理後に `tmp/` フォルダも確認してください

---

## ライセンスと免責事項

このツールはMITライセンスで提供されます。

**免責事項:**
- このツールの使用により生じたいかなる損害についても、開発者は責任を負いません
- 著作権法・利用規約を遵守してご利用ください
- DRM保護コンテンツへの使用は違法です

---

## サポート

問題が発生した場合:

1. まず本READMEのトラブルシューティングを確認
2. ログファイル (`logs/`) を確認
3. GitHubでIssueを作成（該当する場合）

---

## 更新履歴

### v1.0.0 (2025-01-06)
- 初回リリース
- OCR → Google Docs/Drive 自動化機能
- 日本語・英語対応
- 見出し自動検出
- エラーリトライ機能

---

**Happy OCR! 📄✨**
