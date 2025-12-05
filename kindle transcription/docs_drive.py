"""
Google Docs/Drive APIラッパーモジュール
Googleドキュメント作成とDriveへのアップロード
"""
import os
import io
from pathlib import Path
from typing import Optional, List, Dict
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from googleapiclient.http import MediaFileUpload, MediaIoBaseDownload
from tenacity import retry, stop_after_attempt, wait_exponential, retry_if_exception_type
from loguru import logger
from dotenv import load_dotenv
import re

load_dotenv()

# OAuth2スコープ
SCOPES = [
    'https://www.googleapis.com/auth/documents',
    'https://www.googleapis.com/auth/drive.file'
]

# Google Driveフォルダ設定
DOCS_FOLDER_ID = os.getenv('DOCS_FOLDER_ID', '')
PDF_FOLDER_ID = os.getenv('PDF_FOLDER_ID', '')
TXT_FOLDER_ID = os.getenv('TXT_FOLDER_ID', '')

# 認証ファイルのパス
CREDENTIALS_FILE = 'secrets/credentials.json'
TOKEN_FILE = 'token.json'


class GoogleAPIClient:
    """Google Docs/Drive APIクライアント"""

    def __init__(self):
        self.creds = None
        self.docs_service = None
        self.drive_service = None
        self._authenticate()

    def _authenticate(self):
        """Google API認証"""
        # 既存トークンを読み込み
        if os.path.exists(TOKEN_FILE):
            self.creds = Credentials.from_authorized_user_file(TOKEN_FILE, SCOPES)

        # トークンが無効または存在しない場合は認証フロー実行
        if not self.creds or not self.creds.valid:
            if self.creds and self.creds.expired and self.creds.refresh_token:
                logger.info("トークンをリフレッシュ中...")
                self.creds.refresh(Request())
            else:
                if not os.path.exists(CREDENTIALS_FILE):
                    raise FileNotFoundError(
                        f"認証ファイルが見つかりません: {CREDENTIALS_FILE}\n"
                        "Google Cloud Consoleからcredentials.jsonをダウンロードし、"
                        "secrets/フォルダに配置してください。"
                    )

                logger.info("OAuth2認証フローを開始...")
                flow = InstalledAppFlow.from_client_secrets_file(CREDENTIALS_FILE, SCOPES)
                self.creds = flow.run_local_server(port=0)

            # トークンを保存
            with open(TOKEN_FILE, 'w') as token:
                token.write(self.creds.to_json())
            logger.info("認証完了。トークンを保存しました。")

        # APIサービスを構築
        self.docs_service = build('docs', 'v1', credentials=self.creds)
        self.drive_service = build('drive', 'v3', credentials=self.creds)
        logger.info("Google API接続完了")

    @retry(
        stop=stop_after_attempt(5),
        wait=wait_exponential(multiplier=1, min=2, max=60),
        retry=retry_if_exception_type(HttpError)
    )
    def create_document(self, title: str, content: str, heading_info: List[Dict] = None) -> str:
        """
        Googleドキュメントを作成

        Args:
            title: ドキュメントのタイトル
            content: 本文（見出しマーカー除去済み）
            heading_info: 見出し情報リスト

        Returns:
            作成されたドキュメントのID
        """
        try:
            logger.info(f"Googleドキュメント作成中: {title}")

            # ドキュメント作成
            doc = self.docs_service.documents().create(body={'title': title}).execute()
            doc_id = doc['documentId']
            logger.info(f"ドキュメントID: {doc_id}")

            # 本文を挿入（チャンク分割して処理）
            self._insert_content_chunked(doc_id, content, heading_info)

            logger.info(f"ドキュメント作成完了: {title}")
            return doc_id

        except HttpError as e:
            logger.error(f"ドキュメント作成エラー: {e}")
            raise

    def _insert_content_chunked(self, doc_id: str, content: str, heading_info: List[Dict] = None, chunk_size: int = 900000):
        """
        大きなテキストをチャンク分割して挿入（1MB制限対策）

        Args:
            doc_id: ドキュメントID
            content: 本文
            heading_info: 見出し情報
            chunk_size: 1チャンクあたりの最大バイト数
        """
        # バイト数でチャンク分割
        content_bytes = content.encode('utf-8')
        total_bytes = len(content_bytes)

        if total_bytes <= chunk_size:
            # 一度に挿入可能
            self._insert_text(doc_id, content, 1)
            if heading_info:
                self._apply_heading_styles(doc_id, heading_info)
            return

        # チャンク分割
        logger.info(f"大きなテキストをチャンク分割: {total_bytes} bytes")
        chunks = []
        current_pos = 0

        while current_pos < len(content):
            # chunk_size分を切り出し（文字境界で調整）
            end_pos = min(current_pos + chunk_size // 3, len(content))  # UTF-8を考慮して余裕を持たせる

            # 改行位置で調整（途中で文を切らない）
            if end_pos < len(content):
                newline_pos = content.rfind('\n', current_pos, end_pos)
                if newline_pos > current_pos:
                    end_pos = newline_pos + 1

            chunks.append(content[current_pos:end_pos])
            current_pos = end_pos

        logger.info(f"{len(chunks)} チャンクに分割")

        # チャンクごとに挿入
        current_index = 1
        for i, chunk in enumerate(chunks, 1):
            logger.info(f"チャンク {i}/{len(chunks)} を挿入中...")
            self._insert_text(doc_id, chunk, current_index)
            current_index += len(chunk)

        # 見出しスタイル適用
        if heading_info:
            self._apply_heading_styles(doc_id, heading_info)

    def _insert_text(self, doc_id: str, text: str, index: int = 1):
        """
        テキストをドキュメントに挿入

        Args:
            doc_id: ドキュメントID
            text: 挿入するテキスト
            index: 挿入位置
        """
        requests = [{
            'insertText': {
                'location': {'index': index},
                'text': text
            }
        }]

        self.docs_service.documents().batchUpdate(
            documentId=doc_id,
            body={'requests': requests}
        ).execute()

    def _apply_heading_styles(self, doc_id: str, heading_info: List[Dict]):
        """
        見出しスタイルを適用

        Args:
            doc_id: ドキュメントID
            heading_info: 見出し情報リスト [{"index": int, "level": int, "text": str}, ...]
        """
        if not heading_info:
            return

        logger.info(f"{len(heading_info)} 個の見出しスタイルを適用中...")

        requests = []
        for h in heading_info:
            index = h["index"]
            level = h["level"]
            text_length = len(h["text"])

            # 見出しスタイルを適用
            heading_style = 'HEADING_1' if level == 1 else 'HEADING_2'

            requests.append({
                'updateParagraphStyle': {
                    'range': {
                        'startIndex': index + 1,  # +1 for line start
                        'endIndex': index + text_length + 1
                    },
                    'paragraphStyle': {
                        'namedStyleType': heading_style
                    },
                    'fields': 'namedStyleType'
                }
            })

        # バッチ実行（一度に多すぎる場合は分割）
        batch_size = 100
        for i in range(0, len(requests), batch_size):
            batch_requests = requests[i:i + batch_size]
            self.docs_service.documents().batchUpdate(
                documentId=doc_id,
                body={'requests': batch_requests}
            ).execute()

    @retry(
        stop=stop_after_attempt(5),
        wait=wait_exponential(multiplier=1, min=2, max=60),
        retry=retry_if_exception_type(HttpError)
    )
    def export_as_pdf(self, doc_id: str, output_path: Path) -> bool:
        """
        ドキュメントをPDFとしてエクスポート

        Args:
            doc_id: ドキュメントID
            output_path: 保存先パス

        Returns:
            成功したらTrue
        """
        try:
            logger.info(f"PDFエクスポート中: {output_path.name}")

            request = self.drive_service.files().export_media(
                fileId=doc_id,
                mimeType='application/pdf'
            )

            with io.FileIO(str(output_path), 'wb') as fh:
                downloader = MediaIoBaseDownload(fh, request)
                done = False
                while not done:
                    status, done = downloader.next_chunk()
                    if status:
                        logger.info(f"ダウンロード進捗: {int(status.progress() * 100)}%")

            logger.info(f"PDFエクスポート完了: {output_path}")
            return True

        except HttpError as e:
            logger.error(f"PDFエクスポートエラー: {e}")
            return False

    @retry(
        stop=stop_after_attempt(5),
        wait=wait_exponential(multiplier=1, min=2, max=60),
        retry=retry_if_exception_type(HttpError)
    )
    def upload_file(self, file_path: Path, folder_id: str = None, mime_type: str = None) -> Optional[str]:
        """
        ファイルをGoogle Driveにアップロード

        Args:
            file_path: アップロードするファイルのパス
            folder_id: 保存先フォルダID（Noneならルート）
            mime_type: MIMEタイプ（自動判定も可）

        Returns:
            アップロードされたファイルのID
        """
        try:
            logger.info(f"Driveにアップロード中: {file_path.name}")

            file_metadata = {'name': file_path.name}
            if folder_id:
                file_metadata['parents'] = [folder_id]

            media = MediaFileUpload(str(file_path), mimetype=mime_type, resumable=True)

            file = self.drive_service.files().create(
                body=file_metadata,
                media_body=media,
                fields='id, webViewLink'
            ).execute()

            file_id = file.get('id')
            web_link = file.get('webViewLink')
            logger.info(f"アップロード完了: {web_link}")

            return file_id

        except HttpError as e:
            logger.error(f"アップロードエラー: {e}")
            return None

    def move_doc_to_folder(self, doc_id: str, folder_id: str) -> bool:
        """
        ドキュメントを指定フォルダに移動

        Args:
            doc_id: ドキュメントID
            folder_id: 移動先フォルダID

        Returns:
            成功したらTrue
        """
        try:
            if not folder_id:
                return True  # フォルダ指定なしの場合はスキップ

            # 現在の親を取得
            file = self.drive_service.files().get(
                fileId=doc_id,
                fields='parents'
            ).execute()

            previous_parents = ",".join(file.get('parents', []))

            # フォルダに移動
            self.drive_service.files().update(
                fileId=doc_id,
                addParents=folder_id,
                removeParents=previous_parents,
                fields='id, parents'
            ).execute()

            logger.info(f"ドキュメントをフォルダに移動: {folder_id}")
            return True

        except HttpError as e:
            logger.error(f"フォルダ移動エラー: {e}")
            return False

    def search_files(self, name_prefix: str) -> List[str]:
        """
        Drive上で指定プレフィックスを持つファイルを検索

        Args:
            name_prefix: ファイル名プレフィックス

        Returns:
            ファイル名のリスト
        """
        try:
            query = f"name contains '{name_prefix}' and trashed=false"
            results = self.drive_service.files().list(
                q=query,
                fields="files(name)"
            ).execute()

            files = results.get('files', [])
            return [f['name'] for f in files]

        except HttpError as e:
            logger.error(f"ファイル検索エラー: {e}")
            return []
