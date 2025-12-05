# Ubuntu ターミナル入力問題 解決ガイド

Ubuntuターミナルに何も入力できない場合の解決方法を説明します。

## 症状の確認

### 症状1: カーソルが表示されない
- **原因**: ターミナルがアクティブでない
- **解決**: ウィンドウをクリックしてアクティブにする

### 症状2: カーソルは見えるが入力できない
- **原因**: プロセスが応答していない
- **解決**: Ctrl+C を押してプロセスを中断

### 症状3: 初期設定画面で止まっている
- **原因**: インストールが完了していない
- **解決**: しばらく待つか、再インストール

## 解決方法

### 方法1: 基本的な操作

1. **ウィンドウをアクティブにする**
   ```
   - Ubuntuウィンドウをクリック
   - Alt+Tab でウィンドウを切り替え
   ```

2. **キーボード入力をテスト**
   ```
   - Enter キーを押す
   - 文字キーを押してみる
   - Ctrl+C を押してみる
   ```

### 方法2: WSLの再起動

**管理者権限のPowerShell**で実行：

```powershell
# 1. WSLを完全にシャットダウン
wsl --shutdown

# 2. WSLの状態を確認
wsl --list --verbose

# 3. Ubuntuを再起動
wsl -d Ubuntu
```

### 方法3: Ubuntuの再起動

**スタートメニューから**：
1. Ubuntuウィンドウを閉じる
2. スタートメニューで「Ubuntu」を検索
3. 「Ubuntu」をクリックして起動

### 方法4: ターミナル設定のリセット

**管理者権限のPowerShell**で実行：

```powershell
# Ubuntuを終了
wsl --terminate Ubuntu

# Ubuntuを再起動
wsl -d Ubuntu
```

### 方法5: 新しいターミナルセッション

**既存のUbuntuが動いている場合**：

```powershell
# 新しいWSLセッションを開始
wsl -d Ubuntu
```

## 完全な再インストール（最終手段）

### 手順1: 現在のUbuntuを削除

**管理者権限のPowerShell**で実行：

```powershell
# Ubuntuを停止
wsl --terminate Ubuntu

# Ubuntuをアンインストール（データも削除されます）
wsl --unregister Ubuntu
```

### 手順2: Ubuntuを再インストール

```powershell
# Ubuntuを再インストール
wsl --install -d Ubuntu
```

または

1. Microsoft Store を開く
2. 「Ubuntu」で検索
3. 「Ubuntu 22.04 LTS」をインストール
4. インストール後起動

### 手順3: 初期設定

1. Ubuntuが起動したら、ユーザー名を入力
2. パスワードを設定（入力時は表示されません）
3. パスワードを再入力して確認

## トラブルシューティング

### 問題: 「Installing, this may take a few minutes...」で止まる
**解決**:
- 10-15分待ってみる
- インターネット接続を確認
- ウイルス対策ソフトを一時的に無効にする

### 問題: エラーメッセージが表示される
**解決**:
- エラーメッセージをメモする
- WSLを再起動する
- 必要に応じて再インストール

### 問題: 日本語入力ができない
**解決**:
```bash
# 日本語環境をインストール
sudo apt update
sudo apt install language-pack-ja
```

## 動作確認

正常に動作している場合：

```bash
# プロンプトが表示される
username@computername:~$

# コマンドが実行できる
ls
pwd
echo "Hello World"
```

## Claude Code セットアップの続行

Ubuntuが正常に動作したら：

```bash
# プロジェクトディレクトリに移動
cd /mnt/c/Users/yoona/rennai_w/test3

# セットアップスクリプトを実行
chmod +x setup_claude_code.sh
./setup_claude_code.sh

# 環境変数を反映
source ~/.bashrc

# Claude Codeを起動
claude
```
