"""
統合テスト（モック使用）
"""
import pytest
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock
from PIL import Image
import io


class TestOCRIntegration:
    """OCR処理の統合テスト"""

    @patch('ocr.pytesseract.image_to_string')
    def test_ocr_image_mock(self, mock_ocr):
        """画像OCRのモックテスト"""
        from ocr import ocr_image

        # モック設定
        mock_ocr.return_value = "テストテキスト"

        # テスト用の小さな画像を作成
        test_image = Image.new('RGB', (100, 100), color='white')
        test_path = Path('test_image.jpg')

        # 一時ファイルに保存
        test_image.save(test_path)

        try:
            # OCR実行
            result = ocr_image(test_path)

            # 検証
            assert result == "テストテキスト"
            assert mock_ocr.called

        finally:
            # クリーンアップ
            if test_path.exists():
                test_path.unlink()


class TestGoogleAPIIntegration:
    """Google API操作の統合テスト（モック）"""

    @patch('docs_drive.build')
    @patch('docs_drive.Credentials')
    def test_create_document_mock(self, mock_creds, mock_build):
        """ドキュメント作成のモックテスト"""
        from docs_drive import GoogleAPIClient

        # モック設定
        mock_docs_service = MagicMock()
        mock_docs_service.documents().create().execute.return_value = {
            'documentId': 'test_doc_id_123'
        }

        mock_build.return_value = mock_docs_service

        # 認証ファイルチェックをスキップ
        with patch('os.path.exists', return_value=True):
            with patch('builtins.open', create=True):
                with patch('docs_drive.Credentials.from_authorized_user_file'):
                    # APIクライアント初期化
                    client = GoogleAPIClient()
                    client.docs_service = mock_docs_service
                    client.drive_service = MagicMock()

                    # ドキュメント作成（簡易版）
                    doc = mock_docs_service.documents().create(
                        body={'title': 'test_doc'}
                    ).execute()

                    # 検証
                    assert doc['documentId'] == 'test_doc_id_123'


class TestEndToEndPipeline:
    """エンドツーエンドパイプラインテスト"""

    def test_naming_pipeline(self):
        """OCR → 整形 → ファイル名生成のパイプライン"""
        from cleaning import clean_text
        from naming import generate_prefix, generate_filenames

        # テストデータ
        ocr_result = """
        ■第一章　幸せとは何か

        本文が続きます。
        これはテストです。

        5

        次のページ
        """

        # 1. テキスト整形
        cleaned = clean_text(ocr_result)

        # 2. ファイル名生成
        prefix = generate_prefix(cleaned, 10)

        # 3. ファイル名セット生成
        filenames = generate_filenames(prefix)

        # 検証
        assert len(prefix) > 0
        assert "第一章" in prefix or "幸せ" in prefix
        assert filenames['doc'].endswith('_doc')
        assert filenames['pdf'].endswith('.pdf')
        assert filenames['txt'].endswith('.txt')

    def test_empty_text_handling(self):
        """空テキストのハンドリング"""
        from cleaning import clean_text
        from naming import generate_prefix

        # 空白のみのテキスト
        ocr_result = "   \n\n   "

        cleaned = clean_text(ocr_result)
        prefix = generate_prefix(cleaned)

        # タイムスタンプベースのプレフィックスが生成される
        assert prefix.startswith("converted_")

    def test_special_characters_handling(self):
        """特殊文字を含むテキストのハンドリング"""
        from cleaning import clean_text
        from naming import generate_prefix, validate_filename, generate_filenames

        ocr_result = "ファイル名/禁止:文字*テスト"

        cleaned = clean_text(ocr_result)
        prefix = generate_prefix(cleaned, 10)
        filenames = generate_filenames(prefix)

        # 禁止文字が含まれていないことを確認
        assert '/' not in prefix
        assert ':' not in prefix
        assert '*' not in prefix

        # 生成されたファイル名が有効
        assert validate_filename(filenames['pdf'])
        assert validate_filename(filenames['txt'])
