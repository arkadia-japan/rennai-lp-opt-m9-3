"""
メインアプリケーション
OCR → テキスト整形 → Google Docs/Drive作成のパイプライン
"""
import os
import sys
import json
import argparse
import time
from pathlib import Path
from datetime import datetime
from typing import List, Dict, Optional
from tqdm import tqdm
from loguru import logger
from dotenv import load_dotenv

# ローカルモジュール
from ocr import process_file
from cleaning import clean_text, extract_headings_for_docs, remove_heading_markers
from naming import generate_prefix, generate_filenames, make_unique_name, validate_filename
from docs_drive import GoogleAPIClient, DOCS_FOLDER_ID, PDF_FOLDER_ID, TXT_FOLDER_ID

load_dotenv()

# ディレクトリ設定
INPUT_DIR = Path('input')
OUTPUT_DIR = Path('output')
TMP_DIR = Path('tmp')
LOG_DIR = Path('logs')
STATE_FILE = TMP_DIR / 'state.json'

# ログ設定
LOG_LEVEL = os.getenv('LOG_LEVEL', 'INFO')
LOG_RETENTION_DAYS = int(os.getenv('LOG_RETENTION_DAYS', '30'))

# サポートされる拡張子
SUPPORTED_EXTENSIONS = ['.jpg', '.jpeg', '.png', '.tif', '.tiff', '.pdf']


def setup_logging():
    """ロギング設定"""
    logger.remove()  # デフォルトハンドラを削除

    # コンソール出力
    logger.add(
        sys.stderr,
        level=LOG_LEVEL,
        format="<green>{time:YYYY-MM-DD HH:mm:ss}</green> | <level>{level: <8}</level> | <level>{message}</level>"
    )

    # ファイル出力
    log_file = LOG_DIR / "app_{time:YYYY-MM-DD}.log"
    logger.add(
        str(log_file),
        level=LOG_LEVEL,
        format="{time:YYYY-MM-DD HH:mm:ss} | {level: <8} | {message}",
        rotation="00:00",  # 毎日ローテーション
        retention=f"{LOG_RETENTION_DAYS} days",
        encoding="utf-8"
    )

    logger.info("=== OCR to Google Docs アプリケーション起動 ===")


def save_state(state: Dict):
    """処理状態を保存"""
    try:
        with open(STATE_FILE, 'w', encoding='utf-8') as f:
            json.dump(state, f, ensure_ascii=False, indent=2)
    except Exception as e:
        logger.error(f"状態保存エラー: {e}")


def load_state() -> Dict:
    """処理状態を読み込み"""
    if STATE_FILE.exists():
        try:
            with open(STATE_FILE, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            logger.error(f"状態読み込みエラー: {e}")
    return {}


def get_input_files() -> List[Path]:
    """入力ディレクトリからファイルを取得"""
    files = []
    for ext in SUPPORTED_EXTENSIONS:
        files.extend(INPUT_DIR.glob(f'*{ext}'))
        files.extend(INPUT_DIR.glob(f'*{ext.upper()}'))

    files.sort()
    logger.info(f"入力ファイル: {len(files)} 個")
    return files


def process_single_file(file_path: Path, api_client: GoogleAPIClient, lang: str) -> bool:
    """
    単一ファイルを処理

    Args:
        file_path: 入力ファイルパス
        api_client: Google APIクライアント
        lang: OCR言語設定

    Returns:
        成功したらTrue
    """
    logger.info(f"\n{'='*60}")
    logger.info(f"処理開始: {file_path.name}")
    logger.info(f"{'='*60}")

    try:
        # 1. OCR処理
        logger.info("[ステップ 1/7] OCR処理...")
        ocr_text = process_file(file_path, lang)

        if not ocr_text or not ocr_text.strip():
            logger.warning(f"OCRでテキストが抽出できませんでした: {file_path.name}")
            return False

        logger.info(f"OCR完了: {len(ocr_text)} 文字")

        # 2. テキスト整形
        logger.info("[ステップ 2/7] テキスト整形...")
        cleaned_text = clean_text(ocr_text)

        if not cleaned_text:
            logger.warning("整形後のテキストが空です")
            return False

        # 3. ファイル名プレフィックス生成
        logger.info("[ステップ 3/7] ファイル名生成...")
        prefix = generate_prefix(cleaned_text, num_chars=10)

        # 重複チェック
        existing_files = api_client.search_files(prefix)
        if existing_files:
            logger.warning(f"Drive上に同名ファイルが存在: {existing_files}")
            prefix = make_unique_name(prefix, [f.split('.')[0] for f in existing_files])

        filenames = generate_filenames(prefix)
        logger.info(f"ファイル名: {filenames}")

        # 見出し情報抽出
        heading_info = extract_headings_for_docs(cleaned_text)

        # 見出しマーカー除去（本文用）
        clean_content = remove_heading_markers(cleaned_text)

        # 4. Googleドキュメント作成
        logger.info("[ステップ 4/7] Googleドキュメント作成...")
        doc_id = api_client.create_document(
            title=filenames['doc'],
            content=clean_content,
            heading_info=heading_info
        )

        if not doc_id:
            logger.error("ドキュメント作成に失敗")
            return False

        # ドキュメントをフォルダに移動
        if DOCS_FOLDER_ID:
            api_client.move_doc_to_folder(doc_id, DOCS_FOLDER_ID)

        # 5. PDF生成とアップロード
        logger.info("[ステップ 5/7] PDFエクスポート...")
        pdf_path = OUTPUT_DIR / filenames['pdf']
        if api_client.export_as_pdf(doc_id, pdf_path):
            logger.info("[ステップ 6/7] PDFをDriveにアップロード...")
            api_client.upload_file(pdf_path, PDF_FOLDER_ID, 'application/pdf')
        else:
            logger.error("PDFエクスポート失敗")
            return False

        # 6. TXT生成とアップロード
        logger.info("[ステップ 7/7] TXTファイル作成とアップロード...")
        txt_path = OUTPUT_DIR / filenames['txt']
        with open(txt_path, 'w', encoding='utf-8') as f:
            f.write(clean_content)

        api_client.upload_file(txt_path, TXT_FOLDER_ID, 'text/plain')

        logger.info(f"✓ すべての処理が完了: {file_path.name}")

        # 成功したら入力ファイルを削除
        try:
            file_path.unlink()
            logger.info(f"入力ファイルを削除: {file_path.name}")
        except Exception as e:
            logger.warning(f"入力ファイル削除エラー: {e}")

        return True

    except Exception as e:
        logger.error(f"処理エラー ({file_path.name}): {e}", exc_info=True)
        return False


def process_all_files(lang: str = 'jpn+eng', watch: bool = False):
    """
    すべてのファイルを処理

    Args:
        lang: OCR言語設定
        watch: フォルダ監視モード
    """
    # Google APIクライアント初期化
    try:
        api_client = GoogleAPIClient()
    except Exception as e:
        logger.error(f"Google API初期化エラー: {e}")
        logger.error("credentials.jsonが正しく配置されているか確認してください")
        sys.exit(1)

    # 状態読み込み
    state = load_state()
    processed_files = set(state.get('processed_files', []))

    while True:
        files = get_input_files()

        if not files:
            if watch:
                logger.info("新しいファイルを待機中... (Ctrl+C で終了)")
                time.sleep(5)
                continue
            else:
                logger.info("処理するファイルがありません")
                break

        # 未処理ファイルをフィルタ
        files_to_process = [f for f in files if str(f) not in processed_files]

        if not files_to_process:
            if watch:
                logger.info("新しいファイルを待機中... (Ctrl+C で終了)")
                time.sleep(5)
                continue
            else:
                logger.info("すべてのファイルは処理済みです")
                break

        logger.info(f"\n処理対象: {len(files_to_process)} ファイル")

        # プログレスバー付きで処理
        success_count = 0
        fail_count = 0

        for file_path in tqdm(files_to_process, desc="処理中"):
            success = process_single_file(file_path, api_client, lang)

            if success:
                success_count += 1
                processed_files.add(str(file_path))
                # 状態を保存
                save_state({'processed_files': list(processed_files)})
            else:
                fail_count += 1

        logger.info(f"\n{'='*60}")
        logger.info(f"処理完了: 成功 {success_count} / 失敗 {fail_count}")
        logger.info(f"{'='*60}\n")

        if not watch:
            break

        time.sleep(5)


def main():
    """メインエントリポイント"""
    parser = argparse.ArgumentParser(
        description='画像/PDFからOCRしてGoogle Docs/Driveに保存'
    )
    parser.add_argument(
        '--lang',
        default='jpn+eng',
        help='Tesseract言語設定 (デフォルト: jpn+eng)'
    )
    parser.add_argument(
        '--watch',
        action='store_true',
        help='フォルダ監視モード（常駐）'
    )
    parser.add_argument(
        '--dpi',
        type=int,
        default=300,
        help='PDF→画像変換時のDPI (デフォルト: 300)'
    )

    args = parser.parse_args()

    # DPI設定を環境変数に反映
    os.environ['OCR_DPI'] = str(args.dpi)

    # ディレクトリ作成
    for d in [INPUT_DIR, OUTPUT_DIR, TMP_DIR, LOG_DIR]:
        d.mkdir(exist_ok=True)

    # ログ設定
    setup_logging()

    # メイン処理
    try:
        process_all_files(lang=args.lang, watch=args.watch)
    except KeyboardInterrupt:
        logger.info("\n処理を中断しました")
        sys.exit(0)
    except Exception as e:
        logger.error(f"予期しないエラー: {e}", exc_info=True)
        sys.exit(1)


if __name__ == '__main__':
    main()
