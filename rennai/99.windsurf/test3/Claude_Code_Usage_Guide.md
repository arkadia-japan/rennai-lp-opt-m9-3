# Claude Code 使用ガイド - Windsurf以外での利用方法

Claude Codeは一度セットアップすれば、様々な環境で使用できます。

## 🖥️ 基本的な起動方法

### Windows環境

#### 方法1: WSLターミナルから
1. **WSLを起動**
   ```cmd
   wsl
   ```

2. **プロジェクトディレクトリに移動**
   ```bash
   cd /mnt/c/path/to/your/project
   ```

3. **Claude Codeを起動**
   ```bash
   claude
   ```

#### 方法2: Windows Terminal から
1. **Windows Terminal**を開く
2. **Ubuntu タブ**を選択
3. プロジェクトディレクトリに移動してClaude Codeを起動

#### 方法3: Ubuntu アプリから
1. スタートメニューから「**Ubuntu**」を起動
2. プロジェクトディレクトリに移動してClaude Codeを起動

## 📁 プロジェクトディレクトリの指定

### Windowsのフォルダにアクセス
```bash
# Cドライブのプロジェクト
cd /mnt/c/Users/username/Documents/my-project

# Dドライブのプロジェクト  
cd /mnt/d/projects/my-app
```

### WSL内のフォルダにアクセス
```bash
# ホームディレクトリ
cd ~

# WSL内の任意のディレクトリ
cd ~/projects/my-project
```

## 🚀 様々な開発環境での使用

### VS Code
1. **VS Code**でプロジェクトを開く
2. **ターミナル**を開く（Ctrl + `）
3. **WSL**に切り替え
4. `claude` コマンドを実行

### JetBrains IDE (IntelliJ, PyCharm等)
1. **Terminal**タブを開く
2. **WSL**を選択
3. プロジェクトディレクトリで `claude` を実行

### コマンドプロンプト/PowerShell
1. **WSL**に入る: `wsl`
2. プロジェクトディレクトリに移動
3. `claude` を実行

## 🔧 便利な使用パターン

### パターン1: 新しいプロジェクトを開始
```bash
# 新しいディレクトリを作成
mkdir /mnt/c/Users/yoona/projects/new-project
cd /mnt/c/Users/yoona/projects/new-project

# Claude Codeを起動
claude

# プロジェクトを初期化
/init
```

### パターン2: 既存プロジェクトで作業
```bash
# 既存プロジェクトに移動
cd /mnt/c/Users/yoona/existing-project

# Claude Codeを起動
claude

# 既存ファイルを分析
analyze package.json
```

### パターン3: 複数プロジェクトでの作業
```bash
# プロジェクト1
cd /mnt/c/Users/yoona/project1
claude
# 作業後 Ctrl+C で終了

# プロジェクト2
cd /mnt/c/Users/yoona/project2  
claude
```

## 📋 よく使うコマンド

### プロジェクト管理
```bash
/init          # プロジェクト初期化
/status        # 現在の状態確認
/help          # ヘルプ表示
```

### ファイル操作
```bash
analyze filename.js       # ファイル分析
refactor filename.py      # リファクタリング
review src/               # コードレビュー
```

### 開発支援
```bash
create a React component  # コンポーネント作成
fix this bug             # バグ修正
optimize this function   # 最適化
```

## 🎯 効率的な使い方

### 1. プロジェクトごとの設定
各プロジェクトで `/init` を実行してCLAUDE.mdファイルを作成

### 2. 作業の継続
Claude Codeは前回の会話を記憶するので、継続的な開発が可能

### 3. 複数ターミナル
複数のプロジェクトで同時にClaude Codeを使用可能

## ⚠️ 注意事項

### セキュリティ
- 機密情報を含むプロジェクトでは注意して使用
- Claude Codeは現在のディレクトリ内のファイルにアクセス可能

### パフォーマンス
- 大きなプロジェクトでは初回起動に時間がかかる場合がある
- インターネット接続が必要

### ライセンス
- Claude ProまたはMaxの契約が必要
- 使用量制限に注意

## 🔄 終了と再起動

### Claude Codeの終了
```bash
Ctrl + C  # または
/exit
```

### WSLの終了
```bash
exit
```

### 完全なシャットダウン（Windows側から）
```cmd
wsl --shutdown
```

## 🆘 トラブルシューティング

### Claude Codeが起動しない
```bash
# 環境変数を再読み込み
source ~/.bashrc

# パスを確認
echo $PATH

# Claude Codeの場所を確認
which claude
```

### 認証エラー
```bash
# Claude Codeを再起動して認証をやり直し
claude
```

### パフォーマンスの問題
```bash
# WSLを再起動
wsl --shutdown
wsl
```

これで、Windsurf以外の環境でもClaude Codeを効率的に使用できます！
