@echo off
echo ========================================
echo WSL 修復スクリプト
echo ========================================
echo.
echo このスクリプトは管理者権限で実行してください
echo.

REM 管理者権限チェック
net session >nul 2>&1
if %errorLevel% == 0 (
    echo 管理者権限で実行中...
) else (
    echo エラー: このスクリプトは管理者権限で実行してください
    echo 右クリック → "管理者として実行" を選択してください
    pause
    exit /b 1
)

echo.
echo 1. WSL機能を有効化しています...
dism.exe /online /enable-feature /featurename:Microsoft-Windows-Subsystem-Linux /all /norestart

echo.
echo 2. 仮想マシンプラットフォームを有効化しています...
dism.exe /online /enable-feature /featurename:VirtualMachinePlatform /all /norestart

echo.
echo 3. WSL2をデフォルトバージョンに設定しています...
wsl --set-default-version 2

echo.
echo 4. 既存のWSLをシャットダウンしています...
wsl --shutdown

echo.
echo ========================================
echo 修復処理完了
echo ========================================
echo.
echo 次の手順を実行してください:
echo.
echo 1. PCを再起動してください
echo 2. 再起動後、以下のコマンドを管理者権限のPowerShellで実行:
echo    wsl --install -d Ubuntu
echo.
echo 3. または Microsoft Store から Ubuntu をインストール
echo.
echo 4. Ubuntu を起動してユーザー設定を完了
echo.
echo 5. WSL内で以下を実行してClaude Codeをセットアップ:
echo    cd /mnt/c/Users/yoona/rennai_w/test3
echo    chmod +x setup_claude_code.sh
echo    ./setup_claude_code.sh
echo.
pause
