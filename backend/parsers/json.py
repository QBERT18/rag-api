import json

from .base import BaseParser


class JsonParser(BaseParser):
    extension = ".json"

    def extract_text(self, raw: bytes) -> str:
        text = raw.decode("utf-8", errors="replace")
        data = json.loads(text)
        return json.dumps(data, indent=2, ensure_ascii=False)
