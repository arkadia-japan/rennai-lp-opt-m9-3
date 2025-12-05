#!/bin/bash

# Claude Code セットアップスクリプト
echo "Claude Code セットアップを開始します..."

# 現在のNode.jsバージョンを確認
echo "現在のNode.jsバージョン:"
node -v
npm -v

# npmグローバル設定
echo "npmグローバル設定を行います..."
mkdir -p ~/.npm-global
npm config set prefix ~/.npm-global

# .bashrcにPATHを追加（重複チェック）
if ! grep -q "~/.npm-global/bin" ~/.bashrc; then
    echo 'export PATH=~/.npm-global/bin:$PATH' >> ~/.bashrc
    echo "PATHを.bashrcに追加しました"
else
    echo "PATHは既に設定済みです"
fi

# 設定を反映
source ~/.bashrc

# Claude Codeのインストール
echo "Claude Codeをインストールします..."
npm install -g @anthropic-ai/claude-code

# インストール確認
if command -v claude &> /dev/null; then
    echo "Claude Codeのインストールが完了しました！"
    echo "使用方法: プロジェクトディレクトリで 'claude' コマンドを実行してください"
else
    echo "インストールに問題があります。手動でPATHを確認してください："
    echo "export PATH=~/.npm-global/bin:\$PATH"
fi
