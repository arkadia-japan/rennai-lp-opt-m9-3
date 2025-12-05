"""
OCR処理モジュール
画像とPDFからテキストを抽出
"""
import os
from pathlib import Path
from typing import List, Tuple
import cv2
import numpy as np
from PIL import Image
import pytesseract
from pdf2image import convert_from_path
from loguru import logger
from dotenv import load_dotenv

load_dotenv()

# Tesseract実行ファイルのパス設定
TESSERACT_EXE = os.getenv('TESSERACT_EXE', r'C:\Program Files\Tesseract-OCR\tesseract.exe')
TESSERACT_LANG = os.getenv('TESSERACT_LANG', 'jpn+eng')
OCR_DPI = int(os.getenv('OCR_DPI', '300'))
MAX_IMAGE_SIZE = int(os.getenv('MAX_IMAGE_SIZE', '3000'))

if os.path.exists(TESSERACT_EXE):
    pytesseract.pytesseract.tesseract_cmd = TESSERACT_EXE
else:
    logger.warning(f"Tesseract executable not found at {TESSERACT_EXE}")


def preprocess_image(image: Image.Image) -> Image.Image:
    """
    画像の前処理（グレースケール化、二値化、ノイズ除去など）

    Args:
        image: PIL画像オブジェクト

    Returns:
        前処理済みのPIL画像
    """
    try:
        # PIL → OpenCV形式に変換
        img_array = np.array(image)

        # RGBの場合はBGRに変換
        if len(img_array.shape) == 3 and img_array.shape[2] == 3:
            img_array = cv2.cvtColor(img_array, cv2.COLOR_RGB2BGR)

        # グレースケール化
        if len(img_array.shape) == 3:
            gray = cv2.cvtColor(img_array, cv2.COLOR_BGR2GRAY)
        else:
            gray = img_array

        # ノイズ除去（メディアンフィルタ）
        denoised = cv2.medianBlur(gray, 3)

        # 二値化（適応的閾値処理）
        binary = cv2.adaptiveThreshold(
            denoised, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
            cv2.THRESH_BINARY, 11, 2
        )

        # 簡易的な傾き補正（必要に応じて）
        coords = np.column_stack(np.where(binary > 0))
        if len(coords) > 0:
            angle = cv2.minAreaRect(coords)[-1]
            if angle < -45:
                angle = 90 + angle
            if abs(angle) > 0.5 and abs(angle) < 5:  # 小さな傾きのみ補正
                (h, w) = binary.shape[:2]
                center = (w // 2, h // 2)
                M = cv2.getRotationMatrix2D(center, angle, 1.0)
                binary = cv2.warpAffine(binary, M, (w, h),
                                       flags=cv2.INTER_CUBIC,
                                       borderMode=cv2.BORDER_REPLICATE)

        # OpenCV → PIL形式に戻す
        processed_image = Image.fromarray(binary)
        return processed_image

    except Exception as e:
        logger.warning(f"前処理中にエラー: {e}. 元の画像を使用します。")
        return image


def resize_if_needed(image: Image.Image, max_size: int = MAX_IMAGE_SIZE) -> Image.Image:
    """
    画像が大きすぎる場合はリサイズ

    Args:
        image: PIL画像
        max_size: 長辺の最大サイズ

    Returns:
        リサイズ後の画像
    """
    width, height = image.size
    max_dim = max(width, height)

    if max_dim > max_size:
        scale = max_size / max_dim
        new_width = int(width * scale)
        new_height = int(height * scale)
        logger.info(f"画像をリサイズ: {width}x{height} -> {new_width}x{new_height}")
        return image.resize((new_width, new_height), Image.Resampling.LANCZOS)

    return image


def ocr_image(image_path: Path, lang: str = TESSERACT_LANG) -> str:
    """
    単一画像からOCRでテキストを抽出

    Args:
        image_path: 画像ファイルパス
        lang: Tesseract言語設定

    Returns:
        抽出されたテキスト
    """
    try:
        logger.info(f"OCR処理開始: {image_path.name}")

        # 画像読み込み
        image = Image.open(image_path)

        # リサイズ
        image = resize_if_needed(image)

        # 前処理
        processed_image = preprocess_image(image)

        # OCR実行
        custom_config = r'--oem 3 --psm 6'  # OEM 3=LSTM, PSM 6=単一ブロック
        text = pytesseract.image_to_string(
            processed_image,
            lang=lang,
            config=custom_config
        )

        if not text.strip():
            logger.warning(f"OCRでテキストが抽出できませんでした: {image_path.name}")
            return ""

        logger.info(f"OCR成功: {len(text)} 文字抽出")
        return text

    except Exception as e:
        logger.error(f"OCRエラー ({image_path.name}): {e}")
        return ""


def ocr_pdf(pdf_path: Path, lang: str = TESSERACT_LANG, dpi: int = OCR_DPI) -> Tuple[str, List[str]]:
    """
    PDFからOCRでテキストを抽出（ページごとに処理）

    Args:
        pdf_path: PDFファイルパス
        lang: Tesseract言語設定
        dpi: PDF→画像変換時のDPI

    Returns:
        (結合されたテキスト, ページごとのテキストリスト)
    """
    try:
        logger.info(f"PDF OCR処理開始: {pdf_path.name} (DPI: {dpi})")

        # PDFを画像に変換
        images = convert_from_path(str(pdf_path), dpi=dpi)
        logger.info(f"PDF変換完了: {len(images)} ページ")

        page_texts = []

        for i, image in enumerate(images, 1):
            logger.info(f"ページ {i}/{len(images)} を処理中...")

            # リサイズ
            image = resize_if_needed(image)

            # 前処理
            processed_image = preprocess_image(image)

            # OCR実行
            custom_config = r'--oem 3 --psm 6'
            text = pytesseract.image_to_string(
                processed_image,
                lang=lang,
                config=custom_config
            )

            page_texts.append(text)
            logger.info(f"ページ {i}: {len(text)} 文字抽出")

        # ページ区切りを挿入して結合
        combined_text = ""
        for i, text in enumerate(page_texts, 1):
            if i > 1:
                combined_text += f"\n\n--- Page {i} ---\n\n"
            combined_text += text

        logger.info(f"PDF OCR完了: 合計 {len(combined_text)} 文字")
        return combined_text, page_texts

    except Exception as e:
        logger.error(f"PDF OCRエラー ({pdf_path.name}): {e}")
        return "", []


def process_file(file_path: Path, lang: str = TESSERACT_LANG) -> str:
    """
    ファイル形式に応じてOCR処理を実行

    Args:
        file_path: 入力ファイルパス
        lang: Tesseract言語設定

    Returns:
        抽出されたテキスト
    """
    ext = file_path.suffix.lower()

    if ext == '.pdf':
        text, _ = ocr_pdf(file_path, lang)
        return text
    elif ext in ['.jpg', '.jpeg', '.png', '.tif', '.tiff']:
        return ocr_image(file_path, lang)
    else:
        logger.error(f"サポートされていないファイル形式: {ext}")
        return ""
