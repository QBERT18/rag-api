from .base import BaseParser


class TextParser(BaseParser):
    extension = ".txt"

    def extract_text(self, raw: bytes) -> str:
        return raw.decode("utf-8")
