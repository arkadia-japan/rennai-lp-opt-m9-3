"""
Pytest設定ファイル
共通のフィクスチャを定義
"""
import pytest
from pathlib import Path
import tempfile
import shutil


@pytest.fixture
def temp_dir():
    """一時ディレクトリを作成するフィクスチャ"""
    temp_path = Path(tempfile.mkdtemp())
    yield temp_path
    # テスト後にクリーンアップ
    shutil.rmtree(temp_path, ignore_errors=True)


@pytest.fixture
def sample_japanese_text():
    """日本語サンプルテキスト"""
    return """
    ■第一章　幸せとは何か

    人々は幸せを求めて生きている。
    しかし、幸せの定義は人それぞれである。

    【第二章】人生の意味

    人生に意味はあるのだろうか。
    この問いは古代から続いている。

    5

    次のページへ続く
    """


@pytest.fixture
def sample_english_text():
    """英語サンプルテキスト"""
    return """
    Chapter 1: Introduction

    This is a sample text for test-
    ing purposes.

    SUMMARY

    The main points are listed below.

    Page 2
    """


@pytest.fixture
def sample_mixed_text():
    """日英混在サンプルテキスト"""
    return """
    ■Introduction 序章

    This document contains both English and Japanese (日本語).

    Test テスト 123
    """
