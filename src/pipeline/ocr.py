from __future__ import annotations

from typing import List

_paddle_import_error = None
try:
    from paddleocr import PaddleOCR
except Exception as exc:  # pragma: no cover - optional dependency
    PaddleOCR = None
    _paddle_import_error = exc


class OcrEngine:
    def __init__(self, lang: str = "en", enabled: bool = True) -> None:
        self.enabled = enabled
        if not self.enabled:
            self.ocr = None
            return
        if PaddleOCR is None:
            raise RuntimeError(
                "PaddleOCR failed to import. Install deps with: pip install -r requirements-ml.txt\n"
                f"Import error: {_paddle_import_error}"
            )
        self.ocr = PaddleOCR(use_angle_cls=True, lang=lang)

    def extract_text(self, image_path: str) -> str:
        if not self.enabled or self.ocr is None:
            return ""
        result = self.ocr.ocr(image_path, cls=True)
        lines: List[str] = []
        for page in result:
            for line in page:
                lines.append(line[1][0])
        return "\n".join(lines)
