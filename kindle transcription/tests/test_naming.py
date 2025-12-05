"""
naming.py のテスト
"""
import pytest
from naming import (
    extract_first_chars,
    safe_slug,
    generate_prefix,
    make_unique_name,
    generate_filenames,
    validate_filename
)


class TestExtractFirstChars:
    def test_normal_text(self):
        text = "これはテストです"
        result = extract_first_chars(text, 5)
        assert result == "これはテスト"

    def test_with_whitespace(self):
        text = "  空白  あり  テキスト  "
        result = extract_first_chars(text, 5)
        assert result == "空白ありテキ"  # 空白除去される

    def test_with_newlines(self):
        text = "改行\n\nが\n含まれる"
        result = extract_first_chars(text, 5)
        assert result == "改行が含まれる"

    def test_with_heading_markers(self):
        text = "[H1]見出しテキスト"
        result = extract_first_chars(text, 5)
        assert result == "見出しテキス"

    def test_empty_text(self):
        result = extract_first_chars("", 10)
        assert result == ""

    def test_english_text(self):
        text = "Hello World Test"
        result = extract_first_chars(text, 10)
        assert result == "HelloWorld"


class TestSafeSlug:
    def test_normal_text(self):
        result = safe_slug("幸せから考える")
        assert result == "幸せから考える"

    def test_forbidden_chars(self):
        text = "ファイル/名:テスト"
        result = safe_slug(text)
        assert result == "ファイル-名-テスト"

    def test_all_forbidden_chars(self):
        text = r'test\/:*?"<>|file'
        result = safe_slug(text)
        assert result == "test-file"

    def test_consecutive_hyphens(self):
        text = "test---multiple---hyphens"
        result = safe_slug(text)
        assert result == "test-multiple-hyphens"

    def test_leading_trailing_hyphens(self):
        text = "---test---"
        result = safe_slug(text)
        assert result == "test"

    def test_max_length(self):
        text = "a" * 100
        result = safe_slug(text, max_length=10)
        assert len(result) == 10

    def test_empty_text(self):
        result = safe_slug("")
        assert result == ""


class TestGeneratePrefix:
    def test_normal_japanese(self):
        text = "幸せから考える哲学入門の本文です"
        result = generate_prefix(text, 10)
        assert result == "幸せから考える哲学入"

    def test_english_text(self):
        text = "Chapter 1: Introduction to Philosophy"
        result = generate_prefix(text, 10)
        assert result == "Chapter1In"

    def test_mixed_text(self):
        text = "Test テスト 混在"
        result = generate_prefix(text, 10)
        assert result == "Testテスト混"

    def test_empty_text(self):
        result = generate_prefix("")
        assert result.startswith("converted_")

    def test_whitespace_only(self):
        result = generate_prefix("   \n\n   ")
        assert result.startswith("converted_")

    def test_special_chars_only(self):
        text = "///:::**"
        result = generate_prefix(text, 10)
        # 全て除去されるのでタイムスタンプベース
        assert result.startswith("converted_")


class TestMakeUniqueName:
    def test_no_conflict(self):
        result = make_unique_name("test", [])
        assert result == "test"

    def test_one_conflict(self):
        result = make_unique_name("test", ["test"])
        assert result == "test_v2"

    def test_multiple_conflicts(self):
        existing = ["test", "test_v2", "test_v3"]
        result = make_unique_name("test", existing)
        assert result == "test_v4"

    def test_large_number_conflicts(self):
        existing = [f"test_v{i}" for i in range(2, 102)]
        existing.append("test")
        result = make_unique_name("test", existing)
        # 最大試行回数を超えたらタイムスタンプ追加
        assert result.startswith("test_")


class TestGenerateFilenames:
    def test_normal_prefix(self):
        result = generate_filenames("test_prefix")
        assert result["doc"] == "test_prefix_doc"
        assert result["pdf"] == "test_prefix.pdf"
        assert result["txt"] == "test_prefix.txt"

    def test_japanese_prefix(self):
        result = generate_filenames("テスト")
        assert result["doc"] == "テスト_doc"
        assert result["pdf"] == "テスト.pdf"
        assert result["txt"] == "テスト.txt"


class TestValidateFilename:
    def test_valid_filename(self):
        assert validate_filename("test.txt") == True
        assert validate_filename("テスト文書.pdf") == True

    def test_invalid_empty(self):
        assert validate_filename("") == False
        assert validate_filename("   ") == False

    def test_reserved_names(self):
        assert validate_filename("CON.txt") == False
        assert validate_filename("PRN.txt") == False
        assert validate_filename("AUX.pdf") == False
        assert validate_filename("NUL") == False
        assert validate_filename("COM1.txt") == False

    def test_forbidden_chars(self):
        assert validate_filename("test/file.txt") == False
        assert validate_filename("test:file.txt") == False
        assert validate_filename("test*file.txt") == False
        assert validate_filename('test"file.txt') == False

    def test_valid_with_hyphen(self):
        assert validate_filename("test-file.txt") == True
