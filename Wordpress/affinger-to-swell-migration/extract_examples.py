#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import re
from pathlib import Path
from collections import defaultdict

def extract_full_shortcode_examples(content, target_shortcodes):
    """完全なショートコード（属性含む）を抽出"""
    examples = defaultdict(list)

    # 自己完結型: [shortcode attr="value"]
    # 閉じタグ型: [shortcode attr="value"]content[/shortcode]
    for shortcode in target_shortcodes:
        # パターン1: 自己完結型
        pattern1 = re.escape(f'[{shortcode}') + r'[^\]]*?\]'
        matches1 = re.findall(pattern1, content)

        # パターン2: 閉じタグ型（最初の100文字まで）
        pattern2 = re.escape(f'[{shortcode}') + r'[^\]]*?\].*?\[/' + re.escape(shortcode) + r'\]'
        matches2 = re.findall(pattern2, content, re.DOTALL)

        for match in matches1:
            if len(examples[shortcode]) < 3:  # 最大3例まで
                examples[shortcode].append(match[:200])  # 200文字まで

        for match in matches2:
            if len(examples[shortcode]) < 3:
                # コンテンツが長い場合は省略
                if len(match) > 200:
                    examples[shortcode].append(match[:200] + '...')
                else:
                    examples[shortcode].append(match)

    return examples

def main():
    base_dir = Path("/mnt/c/Users/yoona/99.Project/Wordpress/Wordpress記事")

    # トップ10のショートコード
    target_shortcodes = [
        'st-card',
        'st-mybox',
        'st-midasibox',
        'st-mybutton',
        'caption',
        'st-minihukidashi',
        'st-kaiwa1',
        'st-kaiwa5',
    ]

    examples = defaultdict(list)

    for md_file in base_dir.rglob("*.md"):
        if len([s for s in target_shortcodes if len(examples[s]) < 3]) == 0:
            break  # すべて3例収集済み

        try:
            with open(md_file, 'r', encoding='utf-8') as f:
                content = f.read()
                file_examples = extract_full_shortcode_examples(content, target_shortcodes)

                for shortcode, exs in file_examples.items():
                    if len(examples[shortcode]) < 3:
                        examples[shortcode].extend(exs[:3 - len(examples[shortcode])])
        except Exception as e:
            pass

    print("=" * 80)
    print("主要ショートコードの使用例")
    print("=" * 80)
    print()

    for shortcode in target_shortcodes:
        if shortcode in examples and examples[shortcode]:
            print(f"【{shortcode}】")
            print("-" * 80)
            for i, example in enumerate(examples[shortcode][:3], 1):
                print(f"例{i}:")
                print(example)
                print()
            print()

if __name__ == "__main__":
    main()
