# WSL トラブルシューティングガイド

WSLが `wsl` コマンドで起動しない場合の解決方法を説明します。

## 問題の診断

### 1. WSLの機能が有効になっているか確認

**管理者権限**でPowerShellを開き、以下のコマンドを実行：

```powershell
# WSL機能の確認
Get-WindowsOptionalFeature -Online -FeatureName Microsoft-Windows-Subsystem-Linux

# 仮想マシンプラットフォームの確認
Get-WindowsOptionalFeature -Online -FeatureName VirtualMachinePlatform
```

### 2. WSLのバージョン確認

```powershell
wsl --version
```

### 3. インストール済みディストリビューションの確認

```powershell
wsl --list --verbose
```

## 解決方法

### 方法1: WSL機能の有効化

**管理者権限**でPowerShellまたはコマンドプロンプトを開き、以下を実行：

```powershell
# WSL機能を有効化
dism.exe /online /enable-feature /featurename:Microsoft-Windows-Subsystem-Linux /all /norestart

# 仮想マシンプラットフォームを有効化（WSL2用）
dism.exe /online /enable-feature /featurename:VirtualMachinePlatform /all /norestart

# 再起動
shutdown /r /t 0
```

### 方法2: WSLの完全インストール

再起動後、**管理者権限**で以下を実行：

```powershell
# WSL2をデフォルトに設定
wsl --set-default-version 2

# Ubuntuをインストール
wsl --install -d Ubuntu
```

### 方法3: Microsoft Storeからインストール

1. Microsoft Storeを開く
2. "Ubuntu" または "WSL" で検索
3. Ubuntu 22.04 LTS をインストール
4. インストール後、スタートメニューから「Ubuntu」を起動

### 方法4: 手動でのWSLカーネル更新

1. [WSL2 Linux カーネル更新プログラム](https://wslstorestorage.blob.core.windows.net/wslblob/wsl_update_x64.msi) をダウンロード
2. ダウンロードしたファイルを実行してインストール
3. 再起動

## 初回セットアップ

WSLが正常にインストールされたら：

1. **Ubuntu を起動**（スタートメニューから「Ubuntu」を検索）
2. **ユーザー名とパスワードを設定**
3. **システムを更新**：
   ```bash
   sudo apt update && sudo apt upgrade -y
   ```

## WSLが起動しない場合の追加対処法

### BIOSでの仮想化有効化

1. PCを再起動してBIOS/UEFIに入る
2. 「Virtualization Technology」または「Intel VT-x」を有効にする
3. 保存して再起動

### Hyper-Vの確認

**管理者権限**でPowerShellで実行：

```powershell
# Hyper-Vが有効か確認
Get-WindowsOptionalFeature -Online -FeatureName Microsoft-Hyper-V-All

# 必要に応じてHyper-Vを有効化
Enable-WindowsOptionalFeature -Online -FeatureName Microsoft-Hyper-V -All
```

### WSLのリセット

問題が解決しない場合：

```powershell
# WSLをシャットダウン
wsl --shutdown

# 特定のディストリビューションをリセット
wsl --unregister Ubuntu

# 再インストール
wsl --install -d Ubuntu
```

## 動作確認

WSLが正常にインストールされたら：

```bash
# WSLに入る
wsl

# バージョン確認
cat /etc/os-release

# 基本コマンドテスト
ls -la
pwd
```

## Claude Code セットアップの続行

WSLが正常に動作するようになったら：

1. WSL内で以下を実行：
   ```bash
   cd /mnt/c/Users/yoona/rennai_w/test3
   chmod +x setup_claude_code.sh
   ./setup_claude_code.sh
   ```

2. 環境変数を反映：
   ```bash
   source ~/.bashrc
   ```

3. Claude Codeを起動：
   ```bash
   claude
   ```

## よくある問題

### 問題: "参照されたアセンブリが見つかりません"
**解決**: .NET Framework 3.5を有効にする

### 問題: WSLが非常に遅い
**解決**: WSL2を使用し、プロジェクトファイルをLinuxファイルシステム内に配置

### 問題: ファイルアクセス権限エラー
**解決**: `chmod +x filename` でファイルに実行権限を付与

## サポートリソース

- [Microsoft WSL ドキュメント](https://docs.microsoft.com/ja-jp/windows/wsl/)
- [WSL GitHub Issues](https://github.com/microsoft/WSL/issues)
- [Claude Code ドキュメント](https://docs.anthropic.com/claude/docs/claude-code)
