import os
from pathlib import Path
from docling.document_converter import DocumentConverter, PdfFormatOption
from docling.datamodel.base_models import InputFormat
from docling.datamodel.pipeline_options import PdfPipelineOptions, EasyOcrOptions

# フォルダパス
pdf_folder = Path('C:/Users/yoona/99.Project/kindle PDF-Inbox')
output_folder = Path('C:/Users/yoona/99.Project/kindle markdown')

# 変換したいPDFファイルのリスト
target_files = [
    'ポチらせる文 術.pdf',
    '売れるコピーライティング単語帖 探しているフレーズが ず見つかる言葉のアイデア2000.pdf'
]

# OCR設定：EasyOCRを使用し、日本語を指定
ocr_options = EasyOcrOptions(
    lang=['ja', 'en']
)

pipeline_options = PdfPipelineOptions(
    ocr_options=ocr_options
)

converter = DocumentConverter(
    format_options={
        InputFormat.PDF: PdfFormatOption(pipeline_options=pipeline_options)
    }
)

# 出力フォルダが存在することを確認
output_folder.mkdir(parents=True, exist_ok=True)

total = len(target_files)
print(f'変換対象: {total}個のPDFファイル\n')

for i, filename in enumerate(target_files, 1):
    pdf_path = pdf_folder / filename

    if not pdf_path.exists():
        print(f'[{i}/{total}] ✗ ファイルが見つかりません: {filename}\n')
        continue

    output_path = output_folder / f'{pdf_path.stem}-easyocr.md'

    # 既に変換済みの場合はスキップ
    if output_path.exists():
        print(f'[{i}/{total}] スキップ: {filename} (既に変換済み)\n')
        continue

    print(f'[{i}/{total}] 変換中: {filename}')

    try:
        result = converter.convert(str(pdf_path))

        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(result.document.export_to_markdown())

        print(f'  ✓ 完了: {output_path.name}\n')
    except Exception as e:
        print(f'  ✗ エラー: {e}\n')

print('全ての変換が完了しました！')
