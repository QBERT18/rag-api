import re

from .text import TextParser


class MarkdownParser(TextParser):
    extension = ".md"

    _MD_PATTERNS = [
        (re.compile(r"^#{1,6}\s+", re.MULTILINE), ""),
        (re.compile(r"\*\*(.+?)\*\*"), r"\1"),
        (re.compile(r"\*(.+?)\*"), r"\1"),
        (re.compile(r"`([^`]+)`"), r"\1"),
        (re.compile(r"^[-*+]\s+", re.MULTILINE), ""),
        (re.compile(r"\[([^\]]+)\]\([^)]+\)"), r"\1"),
    ]

    def extract_text(self, raw: bytes) -> str:
        text = super().extract_text(raw)
        for pat, repl in self._MD_PATTERNS:
            text = pat.sub(repl, text)
        return text
