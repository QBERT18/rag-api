import csv
import io

from .base import BaseParser


class CsvParser(BaseParser):
    extension = ".csv"

    def extract_text(self, raw: bytes) -> str:
        text = raw.decode("utf-8", errors="replace")
        reader = csv.reader(io.StringIO(text))
        rows = list(reader)
        if not rows:
            return ""
        header, *data = rows
        out: list[str] = []
        for row in data:
            pairs = [
                f"{header[i]}: {row[i]}"
                for i in range(min(len(header), len(row)))
                if row[i].strip()
            ]
            if pairs:
                out.append("; ".join(pairs))
        return "\n\n".join(out)
