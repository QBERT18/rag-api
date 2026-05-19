from io import BytesIO

from pypdf import PdfReader

from .base import BaseParser


class PdfParser(BaseParser):
    extension = ".pdf"

    def extract_text(self, raw: bytes) -> str:
        reader = PdfReader(BytesIO(raw))
        return "\n\n".join(page.extract_text() or "" for page in reader.pages)
