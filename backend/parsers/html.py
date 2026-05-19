from bs4 import BeautifulSoup

from .base import BaseParser


class HtmlParser(BaseParser):
    extension = ".html"

    def extract_text(self, raw: bytes) -> str:
        soup = BeautifulSoup(raw, "html.parser")
        for tag in soup(["script", "style", "noscript"]):
            tag.decompose()
        text = soup.get_text(separator="\n")
        lines = [ln.strip() for ln in text.splitlines()]
        out: list[str] = []
        prev_blank = False
        for ln in lines:
            if not ln:
                if prev_blank:
                    continue
                prev_blank = True
                out.append("")
            else:
                prev_blank = False
                out.append(ln)
        return "\n".join(out).strip()
