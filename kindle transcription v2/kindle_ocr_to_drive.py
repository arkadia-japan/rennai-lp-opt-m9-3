#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Kindle for PC 自動OCR & Google Drive アップロードツール

【事前準備】
1. 必要なライブラリをインストール:
   pip install pyautogui pytesseract Pillow google-api-python-client google-auth-oauthlib reportlab pywin32 numpy

2. Tesseract OCRをインストール:
   - Windows: https://github.com/UB-Mannheim/tesseract/wiki からインストーラーをダウンロード
   - インストール後、環境変数PATHに Tesseract のインストールパス (例: C:\\Program Files\\Tesseract-OCR) を追加
   - 日本語学習データ (jpn.traineddata) が必要:
     https://github.com/tesseract-ocr/tessdata から jpn.traineddata をダウンロードし、
     Tesseractのインストールフォルダ内の tessdata フォルダに配置

3. Google Cloud Platform での設定:
   - Google Cloud Console (https://console.cloud.google.com/) でプロジェクトを作成
   - Google Drive API と Google Docs API を有効化
   - OAuth 2.0 クライアントID (デスクトップアプリ) を作成
   - credentials.json をダウンロードし、このスクリプトと同じディレクトリに配置

【使用方法】
1. Kindle for PC を起動し、OCRしたい書籍の最初のページを表示
2. このスクリプトを実行
3. 初回実行時はブラウザでGoogleアカウントの認証を行う
4. 処理完了後、Google Driveの「Kindle_OCR_Files」フォルダに結果が保存される
"""

import os
import time
import re
import pyautogui
import pytesseract
from PIL import Image, ImageGrab, ImageEnhance, ImageFilter
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.lib.units import mm
import pickle
import win32gui
import win32ui
import win32con

# ========== 設定項目 ==========
# スクリーンショット保存用の一時フォルダ
TEMP_FOLDER = "kindle_screenshots_temp"

# ページ送り後の待機時間（秒）
PAGE_TURN_WAIT = 2.5

# スクリーンショット撮影時の待機時間（秒）
SCREENSHOT_WAIT = 0.5

# デバッグモード（Trueの場合、スクリーンショットを削除しない）
DEBUG_MODE = True

# Kindleウィンドウのタイトル（部分一致）
# Kindle for PCのウィンドウタイトルには「PC名 - 書籍名」という形式が使われます
# 書籍名で検出します（現在開いている書籍名に変更してください）
KINDLE_WINDOW_TITLE = "悪魔を出し抜け！"

# 除外するウィンドウタイトルのキーワード（これらを含むウィンドウは無視）
EXCLUDE_WINDOW_KEYWORDS = ["Windsurf", "Visual Studio", "Code", "Editor", "PowerShell", "cmd", "エクスプローラー", "Explorer", "chrome", "firefox", "edge", "Discord", "LINE"]

# Tesseract OCR の実行ファイルパス（必要に応じて変更）
# 例: pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'
pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'

# カスタムtessdataパスを設定
os.environ['TESSDATA_PREFIX'] = r'C:\Users\yoona\tessdata'

# Google Drive のフォルダ名
DRIVE_FOLDER_NAME = "Kindle_OCR_Files"

# Google API のスコープ
SCOPES = [
    'https://www.googleapis.com/auth/drive.file',
    'https://www.googleapis.com/auth/documents'
]

# PDF生成時の日本語フォント（Windows標準フォントを使用）
# 環境に応じて変更してください
JAPANESE_FONT_PATH = r'C:\Windows\Fonts\msgothic.ttc'  # MSゴシック
JAPANESE_FONT_NAME = 'MSGothic'

# ========== メイン処理 ==========

def get_google_credentials():
    """
    Google API の認証情報を取得
    初回実行時はブラウザで認証、以降は token.pickle を使用
    """
    creds = None

    # token.pickle が存在する場合は読み込み
    if os.path.exists('token.pickle'):
        with open('token.pickle', 'rb') as token:
            creds = pickle.load(token)

    # 認証情報が無効または存在しない場合
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            # トークンをリフレッシュ
            creds.refresh(Request())
        else:
            # 新規認証
            if not os.path.exists('credentials.json'):
                raise FileNotFoundError(
                    "credentials.json が見つかりません。\n"
                    "Google Cloud Console で OAuth 2.0 クライアントIDを作成し、\n"
                    "credentials.json をダウンロードしてこのスクリプトと同じディレクトリに配置してください。"
                )

            flow = InstalledAppFlow.from_client_secrets_file('credentials.json', SCOPES)
            creds = flow.run_local_server(port=0)

        # 認証情報を保存
        with open('token.pickle', 'wb') as token:
            pickle.dump(creds, token)

    return creds


def get_or_create_drive_folder(drive_service, folder_name):
    """
    Google Drive 上の指定フォルダを取得、存在しなければ作成
    """
    # フォルダを検索
    query = f"name='{folder_name}' and mimeType='application/vnd.google-apps.folder' and trashed=false"
    results = drive_service.files().list(q=query, spaces='drive', fields='files(id, name)').execute()
    folders = results.get('files', [])

    if folders:
        # 既存のフォルダを使用
        folder_id = folders[0]['id']
        print(f"既存のフォルダ '{folder_name}' を使用します (ID: {folder_id})")
    else:
        # 新規フォルダを作成
        folder_metadata = {
            'name': folder_name,
            'mimeType': 'application/vnd.google-apps.folder'
        }
        folder = drive_service.files().create(body=folder_metadata, fields='id').execute()
        folder_id = folder.get('id')
        print(f"フォルダ '{folder_name}' を作成しました (ID: {folder_id})")

    return folder_id


def sanitize_filename(text, max_length=50):
    """
    ファイル名として使用できない文字を置換し、長さを制限
    """
    # ファイル名に使用できない文字を置換
    text = re.sub(r'[\\/:*?"<>|]', '_', text)
    # 改行や空白を除去
    text = text.replace('\n', '').replace('\r', '').strip()
    # 空白を詰める
    text = re.sub(r'\s+', ' ', text)
    # 長さ制限
    if len(text) > max_length:
        text = text[:max_length]

    return text


def list_all_windows():
    """
    すべてのウィンドウをリストアップ（デバッグ用）
    """
    def callback(hwnd, windows):
        if win32gui.IsWindowVisible(hwnd):
            title = win32gui.GetWindowText(hwnd)
            if title:
                windows.append((hwnd, title))
        return True

    windows = []
    win32gui.EnumWindows(callback, windows)
    return windows


def get_kindle_window_rect():
    """
    Kindleウィンドウの位置とサイズを取得
    """
    def callback(hwnd, windows):
        if win32gui.IsWindowVisible(hwnd):
            title = win32gui.GetWindowText(hwnd)
            # Kindleを含むウィンドウを検出
            if KINDLE_WINDOW_TITLE.lower() in title.lower():
                # 除外キーワードをチェック
                is_excluded = any(keyword.lower() in title.lower() for keyword in EXCLUDE_WINDOW_KEYWORDS)
                if not is_excluded:
                    windows.append((hwnd, title))
        return True

    windows = []
    win32gui.EnumWindows(callback, windows)

    # デバッグ: 検索キーワードを含むすべてのウィンドウを表示
    print(f"\n【デバッグ】'{KINDLE_WINDOW_TITLE}'を含むウィンドウ一覧:")
    all_windows = list_all_windows()
    kindle_like_windows = [(hwnd, title) for hwnd, title in all_windows if KINDLE_WINDOW_TITLE.lower() in title.lower()]
    for hwnd, title in kindle_like_windows:
        is_excluded = any(keyword.lower() in title.lower() for keyword in EXCLUDE_WINDOW_KEYWORDS)
        status = "[除外]" if is_excluded else "[候補]"
        print(f"  {status} {title}")

    if not windows:
        # デバッグ: すべてのウィンドウを表示
        print("\n【デバッグ】すべてのウィンドウ一覧:")
        for hwnd, title in all_windows[:30]:  # 最初の30個を表示
            print(f"  - {title}")
        raise Exception(
            f"\n'{KINDLE_WINDOW_TITLE}' ウィンドウが見つかりません。\n"
            f"Kindle for PCを起動し、書籍を開いてください。\n"
            f"上記のウィンドウ一覧から正しいKindleウィンドウのタイトルを確認し、\n"
            f"スクリプトの KINDLE_WINDOW_TITLE 設定を変更してください。"
        )

    # 複数のKindleウィンドウがある場合は選択
    if len(windows) > 1:
        print("\n複数のKindleウィンドウが検出されました:")
        for i, (hwnd, title) in enumerate(windows, 1):
            print(f"  {i}. {title}")

        # 最初のウィンドウを使用（ユーザーが選択できるようにも可能）
        print(f"\n最初のウィンドウを使用します: '{windows[0][1]}'")
        hwnd, title = windows[0]
    else:
        hwnd, title = windows[0]

    print(f"\n検出したウィンドウ: '{title}'")
    rect = win32gui.GetWindowRect(hwnd)
    print(f"ウィンドウ位置: {rect}")

    # ウィンドウを前面に表示
    win32gui.SetForegroundWindow(hwnd)
    time.sleep(0.5)

    return rect  # (left, top, right, bottom)


def capture_window_screenshot(rect):
    """
    指定されたウィンドウ領域のスクリーンショットを撮影
    """
    left, top, right, bottom = rect
    width = right - left
    height = bottom - top

    # ウィンドウ領域のみをキャプチャ
    screenshot = ImageGrab.grab(bbox=(left, top, right, bottom))
    return screenshot


def crop_content_area(image, margin_percent=10):
    """
    画像の余白部分（UI要素など）をトリミング
    margin_percent: 各辺からトリミングする割合（%）
    """
    width, height = image.size
    margin_x = int(width * margin_percent / 100)
    margin_y = int(height * margin_percent / 100)

    # 上下左右の余白を削除
    cropped = image.crop((
        margin_x,           # left
        margin_y,           # top
        width - margin_x,   # right
        height - margin_y   # bottom
    ))

    return cropped


def is_dark_background(image):
    """
    画像が黒背景かどうかを判定
    """
    # グレースケール化
    gray = image.convert('L')
    # 平均輝度を計算
    import numpy as np
    avg_brightness = np.array(gray).mean()
    # 128以下なら黒背景と判定
    return avg_brightness < 128


def preprocess_image_for_ocr(image, enable_crop=True):
    """
    OCR精度向上のための画像前処理
    """
    # UIやメニューバーをトリミング
    if enable_crop:
        image = crop_content_area(image, margin_percent=8)

    # グレースケール化
    gray_image = image.convert('L')

    # 黒背景+白文字の場合は反転
    if is_dark_background(gray_image):
        print(f"      → 黒背景を検出、画像を反転します")
        from PIL import ImageOps
        gray_image = ImageOps.invert(gray_image)

    # 明るさを調整
    enhancer = ImageEnhance.Brightness(gray_image)
    processed = enhancer.enhance(1.1)

    # コントラストを強調
    enhancer = ImageEnhance.Contrast(processed)
    processed = enhancer.enhance(2.0)

    # シャープネスを強調
    enhancer = ImageEnhance.Sharpness(processed)
    processed = enhancer.enhance(1.8)

    # 二値化
    from PIL import ImageOps
    processed = ImageOps.autocontrast(processed, cutoff=2)

    return processed


def activate_window(hwnd):
    """
    指定したウィンドウを確実にアクティブ化
    """
    try:
        # ウィンドウを最前面に
        win32gui.ShowWindow(hwnd, win32con.SW_RESTORE)
        win32gui.SetForegroundWindow(hwnd)
        time.sleep(0.3)

        # クリックしてフォーカスを確実に
        rect = win32gui.GetWindowRect(hwnd)
        center_x = (rect[0] + rect[2]) // 2
        center_y = (rect[1] + rect[3]) // 2
        pyautogui.click(center_x, center_y)
        time.sleep(0.2)

        return True
    except Exception as e:
        print(f"警告: ウィンドウのアクティブ化に失敗: {e}")
        return False


def capture_kindle_screenshots():
    """
    Kindle for PC のスクリーンショットを自動撮影
    ページの終端を検出するまで繰り返す
    """
    # 一時フォルダを作成
    if not os.path.exists(TEMP_FOLDER):
        os.makedirs(TEMP_FOLDER)
        print(f"一時フォルダ '{TEMP_FOLDER}' を作成しました")

    print("\n【スクリーンショット撮影開始】")
    print("Kindle for PC のウィンドウを検出しています...")

    # Kindleウィンドウの位置を取得
    kindle_rect = get_kindle_window_rect()

    # ウィンドウハンドルを取得
    def get_hwnd_callback(hwnd, hwnds):
        if win32gui.IsWindowVisible(hwnd):
            title = win32gui.GetWindowText(hwnd)
            if KINDLE_WINDOW_TITLE.lower() in title.lower():
                is_excluded = any(keyword.lower() in title.lower() for keyword in EXCLUDE_WINDOW_KEYWORDS)
                if not is_excluded:
                    hwnds.append(hwnd)
        return True

    hwnds = []
    win32gui.EnumWindows(get_hwnd_callback, hwnds)
    kindle_hwnd = hwnds[0] if hwnds else None

    print(f"Kindleウィンドウを検出しました: {kindle_rect}")
    print("3秒後に撮影を開始します")
    time.sleep(3)

    screenshot_count = 0
    previous_image = None

    while True:
        # Kindleウィンドウを確実にアクティブ化
        if kindle_hwnd:
            activate_window(kindle_hwnd)

        screenshot_count += 1
        screenshot_path = os.path.join(TEMP_FOLDER, f"page_{screenshot_count:04d}.png")

        # スクリーンショットを撮影
        time.sleep(SCREENSHOT_WAIT)
        screenshot = capture_window_screenshot(kindle_rect)
        screenshot.save(screenshot_path)
        print(f"  ページ {screenshot_count} を撮影: {screenshot_path}")

        # 前回のスクリーンショットと比較（ページ終端の検出）
        if previous_image is not None:
            if images_are_identical(previous_image, screenshot):
                print(f"\n同一ページを検出しました。書籍の終端と判断します")
                # 最後の重複画像を削除
                os.remove(screenshot_path)
                screenshot_count -= 1
                break

        previous_image = screenshot

        # Kindleウィンドウを再度アクティブ化してからページ送り
        if kindle_hwnd:
            activate_window(kindle_hwnd)

        # ページ送り（右矢印キーを押下）
        pyautogui.press('right')
        print(f"  ページを送ります...")
        time.sleep(PAGE_TURN_WAIT)

    print(f"\n撮影完了: 合計 {screenshot_count} ページ")
    return screenshot_count


def images_are_identical(img1, img2, threshold=0.995):
    """
    2つの画像が同一かどうかを判定
    完全一致ではなく、高い類似度で判定（誤差を考慮）
    しきい値を高めに設定して、誤検出を防ぐ
    """
    # サイズが異なる場合は別の画像
    if img1.size != img2.size:
        return False

    # ピクセルごとに比較
    pixels1 = list(img1.getdata())
    pixels2 = list(img2.getdata())

    if len(pixels1) != len(pixels2):
        return False

    # 一致するピクセル数をカウント
    matching_pixels = sum(1 for p1, p2 in zip(pixels1, pixels2) if p1 == p2)
    similarity = matching_pixels / len(pixels1)

    print(f"    画像類似度: {similarity:.4f} (しきい値: {threshold})")

    return similarity >= threshold


def ocr_screenshots():
    """
    保存したスクリーンショットをOCR処理し、テキストを抽出
    """
    print("\n【OCR処理開始】")

    # スクリーンショットファイル一覧を取得（ページ順にソート）
    screenshot_files = sorted([
        f for f in os.listdir(TEMP_FOLDER) if f.endswith('.png')
    ])

    if not screenshot_files:
        raise FileNotFoundError(f"'{TEMP_FOLDER}' フォルダにスクリーンショットが見つかりません")

    # 各スクリーンショットをOCR処理
    all_text = []
    for i, filename in enumerate(screenshot_files, 1):
        filepath = os.path.join(TEMP_FOLDER, filename)
        print(f"  {i}/{len(screenshot_files)}: {filename} を処理中...")

        # 画像を読み込み
        image = Image.open(filepath)

        # 画像の前処理
        processed_image = preprocess_image_for_ocr(image)

        # 前処理済み画像を保存（デバッグ用）
        processed_path = os.path.join(TEMP_FOLDER, f"processed_{filename}")
        processed_image.save(processed_path)

        # Tesseract OCR で日本語テキストを抽出（最適化された設定）
        # PSM 3: 完全自動ページセグメンテーション（デフォルト）
        # PSM 6: 単一の均一なテキストブロックと仮定
        # OEM 3: デフォルト（LSTMとLegacyの両方を使用）
        custom_config = r'--oem 3 --psm 3'
        text = pytesseract.image_to_string(processed_image, lang='jpn', config=custom_config)

        # デバッグ: 抽出されたテキストの最初の100文字を表示
        preview = text[:100].replace('\n', ' ')
        print(f"    抽出文字数: {len(text)} 文字")
        print(f"    プレビュー: {preview}...")

        all_text.append(text)

    # すべてのテキストを結合
    combined_text = '\n'.join(all_text)
    print(f"\nOCR完了: 合計 {len(combined_text)} 文字を抽出")

    return combined_text


def generate_base_filename(text):
    """
    テキストの冒頭10文字（空白・改行除去）からファイル名を生成
    """
    # 改行やタブを除去
    clean_text = text.replace('\n', '').replace('\r', '').replace('\t', '').strip()

    # 空白を除去して最初の10文字を取得
    clean_text_no_space = clean_text.replace(' ', '')
    base_name = clean_text_no_space[:10]

    if not base_name:
        base_name = "kindle_book"

    # ファイル名として使用可能な形式に変換
    base_name = sanitize_filename(base_name)

    return base_name


def create_txt_file(text, base_filename):
    """
    TXTファイルを生成
    """
    txt_filename = f"{base_filename}.txt"
    txt_path = os.path.join(TEMP_FOLDER, txt_filename)

    with open(txt_path, 'w', encoding='utf-8') as f:
        f.write(text)

    print(f"TXTファイル作成: {txt_path}")
    return txt_path


def create_pdf_file(text, base_filename):
    """
    PDFファイルを生成（日本語フォント埋め込み）
    """
    pdf_filename = f"{base_filename}.pdf"
    pdf_path = os.path.join(TEMP_FOLDER, pdf_filename)

    # 日本語フォントを登録
    font_name = JAPANESE_FONT_NAME
    try:
        pdfmetrics.registerFont(TTFont(font_name, JAPANESE_FONT_PATH))
    except Exception as e:
        print(f"警告: 日本語フォントの登録に失敗しました: {e}")
        print(f"フォントパス '{JAPANESE_FONT_PATH}' を確認してください")
        # フォールバック: 標準フォントを使用（日本語は表示されない）
        font_name = 'Helvetica'

    # PDFを作成
    c = canvas.Canvas(pdf_path, pagesize=A4)
    width, height = A4

    # テキストを行ごとに分割
    lines = text.split('\n')

    # 1ページあたりの行数
    font_size = 10
    line_height = font_size * 1.5
    margin = 20 * mm
    lines_per_page = int((height - 2 * margin) / line_height)

    # ページごとに描画
    for page_start in range(0, len(lines), lines_per_page):
        page_lines = lines[page_start:page_start + lines_per_page]

        c.setFont(font_name, font_size)

        y_position = height - margin
        for line in page_lines:
            # 長い行は折り返し
            if c.stringWidth(line, font_name, font_size) > (width - 2 * margin):
                # 簡易的な折り返し処理
                words = list(line)
                current_line = ""
                for char in words:
                    if c.stringWidth(current_line + char, font_name, font_size) < (width - 2 * margin):
                        current_line += char
                    else:
                        c.drawString(margin, y_position, current_line)
                        y_position -= line_height
                        current_line = char
                if current_line:
                    c.drawString(margin, y_position, current_line)
                    y_position -= line_height
            else:
                c.drawString(margin, y_position, line)
                y_position -= line_height

        c.showPage()

    c.save()
    print(f"PDFファイル作成: {pdf_path}")
    return pdf_path


def upload_to_google_docs(text, base_filename, folder_id, creds):
    """
    Googleドキュメントを作成してアップロード
    """
    docs_service = build('docs', 'v1', credentials=creds)
    drive_service = build('drive', 'v3', credentials=creds)

    # 新しいGoogleドキュメントを作成
    doc_title = base_filename
    doc = docs_service.documents().create(body={'title': doc_title}).execute()
    doc_id = doc.get('documentId')

    print(f"Googleドキュメント作成: {doc_title} (ID: {doc_id})")

    # テキストを挿入
    requests = [
        {
            'insertText': {
                'location': {
                    'index': 1,
                },
                'text': text
            }
        }
    ]

    docs_service.documents().batchUpdate(
        documentId=doc_id,
        body={'requests': requests}
    ).execute()

    # 指定フォルダに移動
    file = drive_service.files().get(fileId=doc_id, fields='parents').execute()
    previous_parents = ",".join(file.get('parents'))

    drive_service.files().update(
        fileId=doc_id,
        addParents=folder_id,
        removeParents=previous_parents,
        fields='id, parents'
    ).execute()

    print(f"Googleドキュメントを '{DRIVE_FOLDER_NAME}' フォルダに移動しました")

    return doc_id


def upload_to_google_drive(file_path, folder_id, creds):
    """
    ファイルをGoogle Driveにアップロード
    """
    drive_service = build('drive', 'v3', credentials=creds)

    file_name = os.path.basename(file_path)
    file_metadata = {
        'name': file_name,
        'parents': [folder_id]
    }

    media = MediaFileUpload(file_path, resumable=True)
    file = drive_service.files().create(
        body=file_metadata,
        media_body=media,
        fields='id'
    ).execute()

    file_id = file.get('id')
    print(f"Google Driveにアップロード: {file_name} (ID: {file_id})")

    return file_id


def cleanup_temp_folder():
    """
    一時フォルダとその中のファイルを削除
    """
    if DEBUG_MODE:
        print(f"\n【デバッグモード】一時ファイルを残します: {TEMP_FOLDER}")
        print(f"  スクリーンショットとOCR結果を確認してください")
        return

    print(f"\n一時ファイルを削除中...")

    if os.path.exists(TEMP_FOLDER):
        for filename in os.listdir(TEMP_FOLDER):
            file_path = os.path.join(TEMP_FOLDER, filename)
            try:
                os.remove(file_path)
                print(f"  削除: {file_path}")
            except Exception as e:
                print(f"  削除失敗: {file_path} - {e}")

        try:
            os.rmdir(TEMP_FOLDER)
            print(f"一時フォルダ '{TEMP_FOLDER}' を削除しました")
        except Exception as e:
            print(f"一時フォルダの削除に失敗しました: {e}")


def main():
    """
    メイン処理
    """
    print("=" * 60)
    print("Kindle for PC 自動OCR & Google Drive アップロードツール")
    print("=" * 60)

    try:
        # 1. スクリーンショット撮影
        page_count = capture_kindle_screenshots()

        # 2. OCR処理
        extracted_text = ocr_screenshots()

        if not extracted_text.strip():
            print("エラー: テキストが抽出できませんでした")
            return

        # 3. ファイル名生成
        base_filename = generate_base_filename(extracted_text)
        print(f"\n基本ファイル名: {base_filename}")

        # 4. TXTファイル作成
        txt_path = create_txt_file(extracted_text, base_filename)

        # 5. PDFファイル作成
        pdf_path = create_pdf_file(extracted_text, base_filename)

        # 6. Google認証
        print("\n【Google認証】")
        creds = get_google_credentials()
        print("Google認証成功")

        # 7. Google Driveフォルダ取得/作成
        drive_service = build('drive', 'v3', credentials=creds)
        folder_id = get_or_create_drive_folder(drive_service, DRIVE_FOLDER_NAME)

        # 8. Googleドキュメント作成
        print("\n【Google Docsアップロード】")
        upload_to_google_docs(extracted_text, base_filename, folder_id, creds)

        # 9. PDF・TXTをGoogle Driveにアップロード
        print("\n【Google Driveアップロード】")
        upload_to_google_drive(pdf_path, folder_id, creds)
        upload_to_google_drive(txt_path, folder_id, creds)

        # 10. 一時ファイル削除
        cleanup_temp_folder()

        print("\n" + "=" * 60)
        print("すべての処理が正常に完了しました！")
        print(f"Google Driveの '{DRIVE_FOLDER_NAME}' フォルダを確認してください")
        print("=" * 60)

    except KeyboardInterrupt:
        print("\n\n処理が中断されました")
    except Exception as e:
        print(f"\n\nエラーが発生しました: {e}")
        import traceback
        traceback.print_exc()


if __name__ == '__main__':
    main()
