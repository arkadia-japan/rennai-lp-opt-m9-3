from docling.document_converter import DocumentConverter, PdfFormatOption
from docling.datamodel.base_models import InputFormat
from docling.datamodel.pipeline_options import PdfPipelineOptions, EasyOcrOptions

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

pdf_path = 'C:/Users/yoona/99.Project/kindle PDF-Inbox/セールスコピー大  見て、読んで、買ってもらえるコトバの作り方.pdf'
output_path = 'C:/Users/yoona/99.Project/kindle markdown/セールスコピー大-easyocr.md'

print('変換中...')
result = converter.convert(pdf_path)

with open(output_path, 'w', encoding='utf-8') as f:
    f.write(result.document.export_to_markdown())

print(f'変換完了: {output_path}')
