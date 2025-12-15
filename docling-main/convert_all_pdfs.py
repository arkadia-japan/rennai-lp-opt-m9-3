import os
from pathlib import Path
from docling.document_converter import DocumentConverter, PdfFormatOption
from docling.datamodel.base_models import InputFormat
from docling.datamodel.pipeline_options import PdfPipelineOptions, EasyOcrOptions

# フォルダパス
pdf_folder = Path('C:/Users/yoona/99.Project/kindle PDF-Inbox')
output_folder = Path('C:/Users/yoona/99.Project/kindle markdown')

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

# PDFファイルを取得
pdf_files = list(pdf_folder.glob('*.pdf'))
total = len(pdf_files)

print(f'変換対象: {total}個のPDFファイル\n')

for i, pdf_path in enumerate(pdf_files, 1):
    output_path = output_folder / f'{pdf_path.stem}-easyocr.md'

    # 既に変換済みの場合はスキップ
    if output_path.exists():
        print(f'[{i}/{total}] スキップ: {pdf_path.name} (既に変換済み)\n')
        continue

    print(f'[{i}/{total}] 変換中: {pdf_path.name}')

    try:
        result = converter.convert(str(pdf_path))

        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(result.document.export_to_markdown())

        print(f'  ✓ 完了: {output_path.name}\n')
    except Exception as e:
        print(f'  ✗ エラー: {e}\n')

print('全ての変換が完了しました！')
