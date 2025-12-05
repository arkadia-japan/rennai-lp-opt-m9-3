"""
テキスト整形モジュール
OCR結果の本文を整形・正規化
"""
import re
from typing import List, Dict
from loguru import logger


def normalize_whitespace(text: str) -> str:
    """
    連続する空白・改行を正規化

    Args:
        text: 入力テキスト

    Returns:
        正規化されたテキスト
    """
    # 連続する空白を1つに
    text = re.sub(r'[ \t]+', ' ', text)

    # 3つ以上の連続改行を2つに
    text = re.sub(r'\n{3,}', '\n\n', text)

    # 行頭・行末の空白を削除
    lines = [line.strip() for line in text.split('\n')]
    text = '\n'.join(lines)

    return text


def fix_hyphenated_words(text: str) -> str:
    """
    行末のハイフン連結を修正（主に英単語対応）

    例: "exam-\nple" -> "example"

    Args:
        text: 入力テキスト

    Returns:
        修正されたテキスト
    """
    # 英数字+ハイフン+改行+英数字のパターンを連結
    # 日本語は基本的にハイフンで分割されないのでスキップ
    text = re.sub(r'([a-zA-Z])-\s*\n\s*([a-zA-Z])', r'\1\2', text)

    return text


def detect_headings(text: str) -> List[Dict[str, any]]:
    """
    見出しらしき行を検出

    検出ルール:
    - 全角記号（■、●、【】など）で始まる行
    - 全て大文字の短い行（英語）
    - 「第X章」「Chapter X」などのパターン

    Args:
        text: 入力テキスト

    Returns:
        見出し情報のリスト [{"line_num": int, "text": str, "level": int}, ...]
    """
    headings = []
    lines = text.split('\n')

    heading_patterns = [
        (r'^[■●◆▲◇△]', 1),  # 記号付き見出し → レベル1
        (r'^【.+】', 1),  # 【】付き見出し → レベル1
        (r'^第[0-9一二三四五六七八九十百千]+章', 1),  # 「第X章」 → レベル1
        (r'^Chapter\s+\d+', 1),  # "Chapter X" → レベル1
        (r'^[A-Z\s]{3,30}$', 2),  # 全て大文字の短い行 → レベル2
    ]

    for i, line in enumerate(lines):
        line = line.strip()
        if not line:
            continue

        for pattern, level in heading_patterns:
            if re.match(pattern, line):
                headings.append({
                    "line_num": i,
                    "text": line,
                    "level": level
                })
                break

    logger.info(f"検出された見出し: {len(headings)} 個")
    return headings


def mark_headings(text: str) -> str:
    """
    見出しに特殊マーカーを付与（後でDocs APIで整形するため）

    Args:
        text: 入力テキスト

    Returns:
        見出しマーク付きテキスト
    """
    headings = detect_headings(text)
    lines = text.split('\n')

    for heading_info in headings:
        line_num = heading_info["line_num"]
        level = heading_info["level"]

        # マーカー追加: [H1] または [H2]
        if line_num < len(lines):
            lines[line_num] = f"[H{level}]{lines[line_num]}"

    return '\n'.join(lines)


def remove_page_numbers(text: str) -> str:
    """
    ページ番号らしき行を削除

    Args:
        text: 入力テキスト

    Returns:
        ページ番号除去後のテキスト
    """
    lines = text.split('\n')
    filtered_lines = []

    for line in lines:
        line_stripped = line.strip()

        # 数字だけの行（ページ番号の可能性）
        if re.match(r'^\d+$', line_stripped):
            continue

        # "- X -" や "Page X" のパターン
        if re.match(r'^[-–—]\s*\d+\s*[-–—]$', line_stripped):
            continue
        if re.match(r'^Page\s+\d+$', line_stripped, re.IGNORECASE):
            continue

        filtered_lines.append(line)

    return '\n'.join(filtered_lines)


def clean_text(text: str, remove_page_nums: bool = True) -> str:
    """
    テキスト全体の整形パイプライン

    Args:
        text: 入力テキスト
        remove_page_nums: ページ番号を削除するか

    Returns:
        整形されたテキスト
    """
    if not text or not text.strip():
        return ""

    logger.info("テキスト整形を開始...")

    # 1. 空白・改行の正規化
    text = normalize_whitespace(text)

    # 2. ハイフン連結の修正
    text = fix_hyphenated_words(text)

    # 3. ページ番号の削除（オプション）
    if remove_page_nums:
        text = remove_page_numbers(text)

    # 4. 見出しマーカーの追加
    text = mark_headings(text)

    # 5. 最終的な空白正規化
    text = normalize_whitespace(text)

    logger.info(f"整形完了: {len(text)} 文字")
    return text


def extract_headings_for_docs(text: str) -> List[Dict[str, any]]:
    """
    Docs API用に見出し情報を抽出

    Args:
        text: [H1]/[H2]マーカー付きテキスト

    Returns:
        見出し情報リスト [{"index": int, "level": int, "text": str}, ...]
    """
    headings = []
    current_index = 0

    for line in text.split('\n'):
        # [H1]または[H2]マーカーを探す
        match = re.match(r'^\[H(\d)\](.+)$', line)
        if match:
            level = int(match.group(1))
            heading_text = match.group(2)
            headings.append({
                "index": current_index,
                "level": level,
                "text": heading_text
            })

        current_index += len(line) + 1  # +1 for newline

    return headings


def remove_heading_markers(text: str) -> str:
    """
    見出しマーカーを削除してクリーンなテキストに

    Args:
        text: [H1]/[H2]マーカー付きテキスト

    Returns:
        マーカー除去後のテキスト
    """
    return re.sub(r'^\[H\d\]', '', text, flags=re.MULTILINE)
