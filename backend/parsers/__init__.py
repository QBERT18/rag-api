import os

from .base import BaseParser
from .csv import CsvParser
from .docx import DocxParser
from .html import HtmlParser
from .json import JsonParser
from .markdown import MarkdownParser
from .pdf import PdfParser
from .text import TextParser

_REGISTRY: dict[str, type[BaseParser]] = {
    TextParser.extension: TextParser,
    MarkdownParser.extension: MarkdownParser,
    PdfParser.extension: PdfParser,
    DocxParser.extension: DocxParser,
    HtmlParser.extension: HtmlParser,
    ".htm": HtmlParser,
    CsvParser.extension: CsvParser,
    JsonParser.extension: JsonParser,
}


def get_parser(filename: str) -> BaseParser:
    ext = os.path.splitext(filename)[1].lower()
    cls = _REGISTRY.get(ext)
    if cls is None:
        raise ValueError(f"Unsupported extension: {ext}")
    return cls()


__all__ = [
    "BaseParser",
    "TextParser",
    "MarkdownParser",
    "PdfParser",
    "DocxParser",
    "HtmlParser",
    "CsvParser",
    "JsonParser",
    "get_parser",
]
