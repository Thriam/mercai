from pathlib import Path
from pypdf import PdfReader


class PDFExtractor:
    def extract(self, file_path: str) -> dict:
        pdf_path = Path(file_path)

        if not pdf_path.exists():
            raise FileNotFoundError(f"PDF file not found: {file_path}")

        reader = PdfReader(str(pdf_path))
        pages = []

        for index, page in enumerate(reader.pages, start=1):
            text = page.extract_text() or ""
            pages.append(
                {
                    "page_number": index,
                    "text": text,
                }
            )

        return {
            "source": pdf_path.name,
            "pages": pages,
        }