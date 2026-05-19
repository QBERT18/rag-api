from abc import ABC, abstractmethod
from typing import TypedDict


WINDOW_LINES = 12
OVERLAP_LINES = 2


class Chunk(TypedDict):
    text: str
    line_start: int
    line_end: int


class BaseParser(ABC):
    extension: str

    @abstractmethod
    def extract_text(self, raw: bytes) -> str:
        """Format-specific: bytes -> plain text."""

    def chunk(self, text: str) -> list[Chunk]:
        lines = text.splitlines()
        if not lines:
            return []
        step = max(1, WINDOW_LINES - OVERLAP_LINES)
        chunks: list[Chunk] = []
        for start in range(0, len(lines), step):
            window = lines[start:start + WINDOW_LINES]
            body = "\n".join(window).strip()
            if not body:
                continue
            chunks.append({
                "text": body,
                "line_start": start + 1,
                "line_end": min(start + WINDOW_LINES, len(lines)),
            })
            if start + WINDOW_LINES >= len(lines):
                break
        return chunks

    def process(self, raw: bytes) -> list[Chunk]:
        return self.chunk(self.extract_text(raw))
