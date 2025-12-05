"""
cleaning.py のテスト
"""
import pytest
from cleaning import (
    normalize_whitespace,
    fix_hyphenated_words,
    detect_headings,
    mark_headings,
    remove_page_numbers,
    clean_text,
    remove_heading_markers
)


class TestNormalizeWhitespace:
    def test_multiple_spaces(self):
        text = "これは    複数の    空白です"
        result = normalize_whitespace(text)
        assert result == "これは 複数の 空白です"

    def test_multiple_newlines(self):
        text = "行1\n\n\n\n行2"
        result = normalize_whitespace(text)
        assert result == "行1\n\n行2"

    def test_line_whitespace(self):
        text = "  先頭空白  \n  末尾空白  "
        result = normalize_whitespace(text)
        assert result == "先頭空白\n末尾空白"


class TestFixHyphenatedWords:
    def test_english_hyphen(self):
        text = "exam-\nple"
        result = fix_hyphenated_words(text)
        assert result == "example"

    def test_multiple_hyphens(self):
        text = "intro-\nduction and conclu-\nsion"
        result = fix_hyphenated_words(text)
        assert result == "introduction and conclusion"

    def test_japanese_not_affected(self):
        text = "日本-\n語"
        result = fix_hyphenated_words(text)
        # 日本語は連結されない
        assert "日本-\n語" in result


class TestDetectHeadings:
    def test_bullet_heading(self):
        text = "■第一章\n本文です"
        headings = detect_headings(text)
        assert len(headings) == 1
        assert headings[0]["text"] == "■第一章"
        assert headings[0]["level"] == 1

    def test_bracket_heading(self):
        text = "【序章】\n本文です"
        headings = detect_headings(text)
        assert len(headings) == 1
        assert headings[0]["text"] == "【序章】"
        assert headings[0]["level"] == 1

    def test_chapter_heading(self):
        text = "第1章\n本文です"
        headings = detect_headings(text)
        assert len(headings) == 1
        assert headings[0]["level"] == 1

    def test_english_chapter(self):
        text = "Chapter 1\nBody text"
        headings = detect_headings(text)
        assert len(headings) == 1
        assert headings[0]["level"] == 1

    def test_uppercase_heading(self):
        text = "INTRODUCTION\nBody text"
        headings = detect_headings(text)
        assert len(headings) == 1
        assert headings[0]["level"] == 2

    def test_no_headings(self):
        text = "これは普通の本文です"
        headings = detect_headings(text)
        assert len(headings) == 0


class TestMarkHeadings:
    def test_mark_single_heading(self):
        text = "■見出し\n本文"
        result = mark_headings(text)
        assert "[H1]■見出し" in result

    def test_mark_multiple_headings(self):
        text = "■見出し1\n本文\n【見出し2】\n本文"
        result = mark_headings(text)
        assert "[H1]■見出し1" in result
        assert "[H1]【見出し2】" in result


class TestRemovePageNumbers:
    def test_single_digit(self):
        text = "本文\n5\n次のページ"
        result = remove_page_numbers(text)
        assert "5" not in result
        assert "本文" in result
        assert "次のページ" in result

    def test_hyphen_format(self):
        text = "本文\n- 5 -\n次のページ"
        result = remove_page_numbers(text)
        assert "- 5 -" not in result

    def test_page_word(self):
        text = "本文\nPage 10\n次のページ"
        result = remove_page_numbers(text)
        assert "Page 10" not in result

    def test_keep_normal_numbers(self):
        text = "2025年に発行された"
        result = remove_page_numbers(text)
        # 文中の数字は残る
        assert "2025" in result


class TestCleanText:
    def test_full_pipeline(self):
        text = "  ■見出し  \n\n\n本文です    テスト\n\n\n5\n\n次のページ  "
        result = clean_text(text)

        # 見出しマーカーが追加されている
        assert "[H1]" in result

        # 空白が正規化されている
        assert "    " not in result

        # 余分な改行が削除されている
        assert "\n\n\n" not in result

    def test_empty_text(self):
        result = clean_text("")
        assert result == ""

    def test_whitespace_only(self):
        result = clean_text("   \n\n   ")
        assert result == ""


class TestRemoveHeadingMarkers:
    def test_remove_h1_marker(self):
        text = "[H1]見出しテキスト"
        result = remove_heading_markers(text)
        assert result == "見出しテキスト"

    def test_remove_multiple_markers(self):
        text = "[H1]見出し1\n本文\n[H2]見出し2"
        result = remove_heading_markers(text)
        assert "[H1]" not in result
        assert "[H2]" not in result
        assert "見出し1" in result
        assert "見出し2" in result

    def test_no_markers(self):
        text = "普通のテキスト"
        result = remove_heading_markers(text)
        assert result == "普通のテキスト"
