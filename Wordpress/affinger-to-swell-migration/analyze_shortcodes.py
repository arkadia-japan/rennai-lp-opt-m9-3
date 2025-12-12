#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import re
from collections import Counter
from pathlib import Path

def extract_shortcodes(content):
    """WordPressのショートコードを抽出"""
    # [shortcode] または [shortcode attr="value"] または [shortcode]content[/shortcode] のパターン
    pattern = r'\[([a-zA-Z0-9_-]+)(?:\s+[^\]]*?)?\]'
    matches = re.findall(pattern, content)
    return matches

def analyze_shortcode_purpose(shortcode_name):
    """ショートコード名から用途を推測"""
    purpose_map = {
        # ボックス・強調系
        'st-kaiwa': '吹き出し・会話',
        'st-mybox': 'マイボックス（装飾ボックス）',
        'st-minihukidashi': 'ミニ吹き出し',
        'st-midasibox': '見出しボックス',
        'st-square-checkbox': '四角チェックボックス',
        'st-point': 'ポイント強調',
        'st-cmemo': 'メモボックス',
        'st-memo': 'メモ',
        'st-alert': 'アラート・警告ボックス',
        'st-marumozi': '丸文字リスト',
        'st-flexbox': 'フレックスボックス（並列配置）',
        'st-card': 'カード',
        'st-card-ex': 'カード拡張',

        # ボタン系
        'st-mybutton': 'マイボタン',
        'st-mybutton-mini': 'ミニボタン',
        'st-button-url': 'ボタンリンク',

        # テキスト装飾系
        'st-kaiwa-hukidashi': '吹き出し',
        'st-text': 'テキスト装飾',
        'st-font': 'フォント装飾',
        'st-big': '大きい文字',
        'st-small': '小さい文字',
        'st-under': 'アンダーライン',
        'st-marker': 'マーカー',
        'st-strong': '太字強調',

        # レイアウト系
        'st-tab': 'タブ',
        'st-accordion': 'アコーディオン',
        'st-timeline': 'タイムライン',
        'st-step': 'ステップ',
        'st-column': 'カラム（列）',
        'st-row': '行',
        'st-div': 'ディビジョン（区画）',
        'st-section': 'セクション',

        # リスト系
        'st-list': 'リスト',
        'st-circle-list': '円形リスト',
        'st-check-list': 'チェックリスト',
        'st-number-list': '番号付きリスト',

        # その他
        'st-star': '星評価',
        'st-rank': 'ランキング',
        'st-label': 'ラベル',
        'st-badge': 'バッジ',
        'st-quote': '引用',
        'st-amp': 'AMP対応',
        'st-toc': '目次',
        'st-ad': '広告',
        'caption': '画像キャプション',
        'gallery': 'ギャラリー',
    }

    # 部分一致チェック
    name_lower = shortcode_name.lower()
    for key, value in purpose_map.items():
        if key in name_lower:
            return value

    # デフォルト
    if name_lower.startswith('st-'):
        return 'Affinger装飾要素'
    elif name_lower in ['p', 'div', 'span']:
        return 'HTML要素'
    else:
        return '不明・その他'

def main():
    base_dir = Path("/mnt/c/Users/yoona/99.Project/Wordpress/Wordpress記事")

    all_shortcodes = []
    file_count = 0

    # すべてのマークダウンファイルを探索
    for md_file in base_dir.rglob("*.md"):
        try:
            with open(md_file, 'r', encoding='utf-8') as f:
                content = f.read()
                shortcodes = extract_shortcodes(content)
                all_shortcodes.extend(shortcodes)
                file_count += 1
        except Exception as e:
            print(f"エラー: {md_file} - {e}")

    # カウントと集計
    shortcode_counter = Counter(all_shortcodes)

    print(f"=" * 80)
    print(f"Affinger4 ショートコード分析結果")
    print(f"=" * 80)
    print(f"分析ファイル数: {file_count}")
    print(f"ショートコード総数: {len(all_shortcodes)}")
    print(f"ユニークなショートコード数: {len(shortcode_counter)}")
    print(f"=" * 80)
    print()

    # 使用頻度順にソート
    print(f"{'順位':<6} {'ショートコード':<30} {'使用回数':<10} {'推測用途'}")
    print(f"-" * 80)

    for rank, (shortcode, count) in enumerate(shortcode_counter.most_common(), 1):
        purpose = analyze_shortcode_purpose(shortcode)
        print(f"{rank:<6} {shortcode:<30} {count:<10} {purpose}")

    print()
    print(f"=" * 80)

    # カテゴリ別集計
    category_counter = Counter()
    for shortcode, count in shortcode_counter.items():
        purpose = analyze_shortcode_purpose(shortcode)
        category_counter[purpose] += count

    print()
    print("【カテゴリ別集計】")
    print(f"-" * 80)
    for category, count in category_counter.most_common():
        print(f"{category:<30} {count:>10} 回")

if __name__ == "__main__":
    main()
