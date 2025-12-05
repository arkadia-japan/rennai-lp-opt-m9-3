@echo off
echo WSL インストール用バッチファイル
echo.
echo 管理者権限で実行してください
echo.

REM WSLの有効化
echo WSL機能を有効化中...
dism.exe /online /enable-feature /featurename:Microsoft-Windows-Subsystem-Linux /all /norestart

REM 仮想マシンプラットフォームの有効化
echo 仮想マシンプラットフォームを有効化中...
dism.exe /online /enable-feature /featurename:VirtualMachinePlatform /all /norestart

echo.
echo 再起動が必要です。再起動後に以下のコマンドを実行してください：
echo.
echo wsl --install Ubuntu
echo.
pause
