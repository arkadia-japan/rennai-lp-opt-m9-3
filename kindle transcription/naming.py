"""
ファイル名生成モジュール
OCR結果の先頭10文字からファイル名プレフィックスを生成
"""
import re
from datetime import datetime
from loguru import logger


def extract_first_chars(text: str, num_chars: int = 10) -> str:
    """
    テキストの先頭N文字を抽出（空白・改行を除く）

    Args:
        text: 入力テキスト
        num_chars: 抽出する文字数

    Returns:
        先頭N文字
    """
    if not text or not text.strip():
        return ""

    # 空白・改行を除去
    cleaned = re.sub(r'\s+', '', text)

    # 見出しマーカーを除去（[H1]など）
    cleaned = re.sub(r'\[H\d\]', '', cleaned)

    # 先頭N文字を取得
    first_chars = cleaned[:num_chars]

    return first_chars


def safe_slug(text: str, max_length: int = 50) -> str:
    """
    ファイル名に使えない文字を安全な文字に置換

    Args:
        text: 入力テキスト
        max_length: 最大長

    Returns:
        ファイル名として安全な文字列
    """
    if not text or not text.strip():
        return ""

    # Windowsファイル名で使えない文字: \ / : * ? " < > |
    # これらを - に置換
    slug = text
    forbidden_chars = r'[\\/:*?"<>|]'
    slug = re.sub(forbidden_chars, '-', slug)

    # 連続するハイフンを1つに
    slug = re.sub(r'-+', '-', slug)

    # 先頭・末尾のハイフンを除去
    slug = slug.strip('-')

    # 最大長に切り詰め
    if len(slug) > max_length:
        slug = slug[:max_length].rstrip('-')

    return slug


def generate_prefix(text: str, num_chars: int = 10) -> str:
    """
    テキストからファイル名プレフィックスを生成

    Args:
        text: OCR結果のテキスト
        num_chars: 先頭から抽出する文字数

    Returns:
        ファイル名プレフィックス（空の場合はタイムスタンプベース）
    """
    # 先頭N文字を抽出
    first_chars = extract_first_chars(text, num_chars)

    # 安全なスラッグに変換
    prefix = safe_slug(first_chars)

    # 空の場合はタイムスタンプを使用
    if not prefix:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        prefix = f"converted_{timestamp}"
        logger.warning(f"先頭文字が無効なため、タイムスタンプベースのプレフィックスを使用: {prefix}")
    else:
        logger.info(f"生成されたプレフィックス: {prefix}")

    return prefix


def make_unique_name(base_name: str, existing_names: list, max_attempts: int = 100) -> str:
    """
    既存の名前と重複しないユニークな名前を生成

    Args:
        base_name: ベースとなる名前
        existing_names: 既存の名前リスト
        max_attempts: 最大試行回数

    Returns:
        ユニークな名前（_v2, _v3...を付与）
    """
    if base_name not in existing_names:
        return base_name

    for i in range(2, max_attempts + 2):
        candidate = f"{base_name}_v{i}"
        if candidate not in existing_names:
            logger.info(f"重複回避: {base_name} -> {candidate}")
            return candidate

    # 最終手段としてタイムスタンプ追加
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S%f")
    unique_name = f"{base_name}_{timestamp}"
    logger.warning(f"最大試行回数を超過。タイムスタンプを追加: {unique_name}")
    return unique_name


def generate_filenames(prefix: str) -> dict:
    """
    各ファイル形式のファイル名を生成

    Args:
        prefix: ファイル名プレフィックス

    Returns:
        ファイル名の辞書 {"doc": str, "pdf": str, "txt": str}
    """
    return {
        "doc": f"{prefix}_doc",
        "pdf": f"{prefix}.pdf",
        "txt": f"{prefix}.txt"
    }


def validate_filename(filename: str) -> bool:
    """
    ファイル名が有効かチェック

    Args:
        filename: ファイル名

    Returns:
        有効ならTrue
    """
    if not filename or not filename.strip():
        return False

    # Windowsで予約されている名前
    reserved_names = [
        'CON', 'PRN', 'AUX', 'NUL',
        'COM1', 'COM2', 'COM3', 'COM4', 'COM5', 'COM6', 'COM7', 'COM8', 'COM9',
        'LPT1', 'LPT2', 'LPT3', 'LPT4', 'LPT5', 'LPT6', 'LPT7', 'LPT8', 'LPT9'
    ]

    # 拡張子を除いた名前を取得
    name_without_ext = filename.rsplit('.', 1)[0].upper()

    if name_without_ext in reserved_names:
        logger.error(f"予約されたファイル名: {filename}")
        return False

    # 使えない文字が含まれていないかチェック
    forbidden_chars = r'[\\/:*?"<>|]'
    if re.search(forbidden_chars, filename):
        logger.error(f"使えない文字が含まれています: {filename}")
        return False

    return True
