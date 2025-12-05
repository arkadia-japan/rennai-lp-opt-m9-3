# Claude Code セットアップガイド (Windows + WSL)

このガイドでは、WindowsでWSLを使用してClaude Codeをセットアップする手順を説明します。

## 前提条件

- Windows 10 バージョン 2004以降 または Windows 11
- Claude Pro または Claude Max の契約

## 手順

### 1. WSLのインストール

1. **管理者権限**でPowerShellまたはコマンドプロンプトを開きます
2. 以下のコマンドを実行します：

```powershell
wsl --install
```

3. 再起動を求められた場合は再起動します
4. 再起動後、Ubuntuが自動的に起動し、ユーザー名とパスワードの設定を求められます

### 2. WSLの起動確認

```bash
wsl
```

でWSLに入れることを確認します。

### 3. セットアップスクリプトの実行

WSL内で以下のコマンドを実行します：

```bash
# Windows側のファイルにアクセス
cd /mnt/c/Users/yoona/rennai_w/test3

# スクリプトに実行権限を付与
chmod +x setup_claude_code.sh

# セットアップスクリプトを実行
./setup_claude_code.sh
```

### 4. 環境変数の反映

スクリプト実行後、以下のコマンドで環境変数を反映します：

```bash
source ~/.bashrc
```

### 5. Claude Codeの起動

プロジェクトディレクトリに移動してClaude Codeを起動します：

```bash
cd /path/to/your/project
claude
```

## 初回起動時の設定

1. **カラーテーマの選択**: お好みのカラーテーマを選択（colorblind-friendlyが推奨）
2. **課金プランの選択**: Claude ProまたはMaxを選択
3. **認証**: ブラウザで認証を行い、表示されたコードをClaude Codeに入力

## トラブルシューティング

### Node.jsのバージョンエラー

Claude CodeはNode.js 18.0.0以上が必要です。エラーが出た場合は以下を実行：

```bash
curl -fsSL https://deb.nodesource.com/setup_lts.x | sudo -E bash -
sudo apt-get install -y nodejs
```

### パーミッションエラー

`sudo`を使わずにnpmのグローバルインストールを設定：

```bash
mkdir -p ~/.npm-global
npm config set prefix ~/.npm-global
echo 'export PATH=~/.npm-global/bin:$PATH' >> ~/.bashrc
source ~/.bashrc
```

### WSLが起動しない場合

1. Windows機能の確認：
   - 「Windowsの機能の有効化または無効化」で「Windows Subsystem for Linux」が有効になっているか確認
   - 「仮想マシンプラットフォーム」も有効にする

2. WSL2の設定：
```powershell
wsl --set-default-version 2
```

## 使用方法

1. プロジェクトディレクトリで`claude`コマンドを実行
2. 初回は認証が必要
3. ディレクトリを信頼するかの確認が表示される
4. Claude Codeが起動し、コーディング支援が利用可能

## 注意事項

- Claude Codeは現在のディレクトリ内のファイルにアクセスできます
- 機密情報を含むディレクトリでは注意して使用してください
- インターネット接続が必要です

## 参考

- [Claude Code 公式ドキュメント](https://docs.anthropic.com/claude/docs/claude-code)
- [WSL インストールガイド](https://docs.microsoft.com/ja-jp/windows/wsl/install)
