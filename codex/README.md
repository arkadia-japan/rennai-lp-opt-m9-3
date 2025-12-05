# Codex CLI for Windsurf

Windsurf IDE用のCodex CLI統合ツールです。OpenAIのCodexを使用してコード生成、説明、リファクタリングなどを行えます。

## 🚀 インストール

### 1. 依存関係のインストール

```bash
npm install
```

### 2. Codex CLIの初期化

```bash
npm run codex init
```

または

```bash
node bin/codex-cli.js init
```

初期化時に以下の情報を入力してください：
- OpenAI API Key
- 使用するモデル（gpt-4, gpt-3.5-turbo, codex-davinci-002）
- 最大トークン数

## 📋 使用方法

### 基本コマンド

#### コード生成
```bash
# プロンプトを指定してコード生成
codex-cli generate -p "JavaScriptでソート関数を作成" -f "./output/sort.js" -l javascript

# インタラクティブモードでコード生成
codex-cli gen
```

#### Windsurf統合
```bash
# Windsurf統合のセットアップ
codex-cli windsurf --setup

# 統合状態の確認
codex-cli windsurf --status
```

### Windsurfでのショートカット

設定後、以下のショートカットが使用できます：

- `Ctrl+Shift+G`: コード生成
- `Ctrl+Shift+I`: CLI初期化
- `Ctrl+Shift+E`: コード説明
- `Ctrl+Shift+R`: リファクタリング
- `Ctrl+Shift+O`: コード最適化

## ⚙️ 設定

### 環境変数（.env）

```env
OPENAI_API_KEY=your_openai_api_key_here
CODEX_MODEL=gpt-4
MAX_TOKENS=2048
```

### 設定ファイル（.codex-config.json）

```json
{
  "model": "gpt-4",
  "maxTokens": 2048,
  "temperature": 0.1,
  "outputDir": "./output",
  "windsurf": {
    "integration": true,
    "autoSave": true,
    "formatOnSave": true
  }
}
```

## 🔧 Windsurf統合設定

### 1. 自動セットアップ
```bash
codex-cli windsurf --setup
```

### 2. 手動設定

`.windsurf/settings.json`ファイルを編集：

```json
{
  "codex-cli": {
    "enabled": true,
    "commands": {
      "generate": "codex-cli generate",
      "init": "codex-cli init"
    },
    "shortcuts": {
      "ctrl+shift+g": "codex-cli generate"
    }
  }
}
```

## 📁 プロジェクト構造

```
project/
├── bin/
│   └── codex-cli.js          # メインCLIファイル
├── .windsurf/
│   └── settings.json         # Windsurf設定
├── .codex-config.json        # Codex設定
├── .codex-config.template.json # 設定テンプレート
├── .env                      # 環境変数
├── package.json              # Node.js設定
└── README.md                 # このファイル
```

## 🎯 機能

### ✅ 実装済み
- [x] CLI基本構造
- [x] 設定ファイル管理
- [x] Windsurf統合設定
- [x] コマンドライン引数処理
- [x] 環境変数管理

### 🚧 開発中
- [ ] OpenAI API統合
- [ ] リアルタイムコード生成
- [ ] コード説明機能
- [ ] リファクタリング機能
- [ ] エラー修正機能

## 🔑 API Key設定

1. [OpenAI Platform](https://platform.openai.com/)でAPI Keyを取得
2. `codex-cli init`コマンドを実行
3. API Keyを入力

## 🐛 トラブルシューティング

### よくある問題

#### 1. API Keyエラー
```bash
# 設定を再初期化
codex-cli init
```

#### 2. Windsurf統合が動作しない
```bash
# 統合状態を確認
codex-cli windsurf --status

# 再セットアップ
codex-cli windsurf --setup
```

#### 3. 依存関係エラー
```bash
# 依存関係を再インストール
npm install
```

## 📝 使用例

### JavaScript関数生成
```bash
codex-cli generate -p "配列をソートするJavaScript関数" -f "./utils/sort.js" -l javascript
```

### Python クラス生成
```bash
codex-cli generate -p "ユーザー管理のためのPythonクラス" -f "./models/user.py" -l python
```

## 🤝 貢献

1. このリポジトリをフォーク
2. 機能ブランチを作成 (`git checkout -b feature/amazing-feature`)
3. 変更をコミット (`git commit -m 'Add amazing feature'`)
4. ブランチにプッシュ (`git push origin feature/amazing-feature`)
5. プルリクエストを作成

## 📄 ライセンス

MIT License - 詳細は[LICENSE](LICENSE)ファイルを参照

## 🆘 サポート

問題や質問がある場合は、[Issues](https://github.com/your-repo/codex-cli-windsurf/issues)で報告してください。

---

**注意**: このツールを使用するにはOpenAI API Keyが必要です。API使用料金については[OpenAI Pricing](https://openai.com/pricing)を確認してください。
