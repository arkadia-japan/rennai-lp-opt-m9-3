#!/bin/bash

# Claude Code セットアップスクリプト
# WSL環境でClaude Codeをセットアップするためのスクリプト

echo "=== Claude Code セットアップ開始 ==="

# Node.jsのバージョンを確認
echo "現在のNode.jsバージョンを確認中..."
if command -v node &> /dev/null; then
    NODE_VERSION=$(node -v)
    echo "Node.js バージョン: $NODE_VERSION"
    
    # Node.js 18以上かチェック
    NODE_MAJOR_VERSION=$(echo $NODE_VERSION | cut -d'.' -f1 | sed 's/v//')
    if [ "$NODE_MAJOR_VERSION" -lt 18 ]; then
        echo "Node.js 18以上が必要です。最新版をインストールします..."
        INSTALL_NODE=true
    else
        echo "Node.js バージョンは要件を満たしています。"
        INSTALL_NODE=false
    fi
else
    echo "Node.jsがインストールされていません。インストールします..."
    INSTALL_NODE=true
fi

# Node.jsのインストール（必要な場合）
if [ "$INSTALL_NODE" = true ]; then
    echo "Node.js 最新版をインストール中..."
    curl -fsSL https://deb.nodesource.com/setup_lts.x | sudo -E bash -
    sudo apt-get install -y nodejs
    
    echo "インストール後のNode.jsバージョン:"
    node -v
    npm -v
fi

# npmのグローバルインストール設定（セキュリティのため）
echo "npmのグローバルインストール設定を構成中..."

# 現在のグローバルパッケージをバックアップ
npm list -g --depth=0 > ~/npm-global-packages-backup.txt

# npmのグローバルディレクトリを設定
mkdir -p ~/.npm-global
npm config set prefix ~/.npm-global

# PATHに追加
if ! grep -q "export PATH=~/.npm-global/bin:\$PATH" ~/.bashrc; then
    echo 'export PATH=~/.npm-global/bin:$PATH' >> ~/.bashrc
    echo "PATHを~/.bashrcに追加しました"
fi

# 現在のセッションでPATHを更新
export PATH=~/.npm-global/bin:$PATH

echo "npm設定完了"

# Claude Codeのインストール
echo "Claude Codeをインストール中..."
npm install -g @anthropic-ai/claude-code

# インストール確認
if command -v claude &> /dev/null; then
    echo "✅ Claude Codeのインストールが完了しました！"
    echo ""
    echo "使用方法:"
    echo "1. プロジェクトディレクトリに移動: cd /path/to/your/project"
    echo "2. Claude Codeを起動: claude"
    echo ""
    echo "初回起動時は認証が必要です。Claude ProまたはMaxの契約が必要です。"
else
    echo "❌ Claude Codeのインストールに失敗しました"
    echo "~/.bashrcを再読み込みしてから再試行してください: source ~/.bashrc"
fi

echo "=== セットアップ完了 ==="
