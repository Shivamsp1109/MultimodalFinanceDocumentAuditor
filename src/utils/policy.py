from __future__ import annotations

import re
from dataclasses import dataclass
from typing import Optional

from .dates import parse_date


@dataclass
class Policy:
    start_date: Optional[str] = None
    end_date: Optional[str] = None
    allowed_tax_rate: Optional[float] = None


DATE_RANGE_RE = re.compile(
    r"(?:effective|start|from)\s*[:\-]?\s*(?P<start>[^\\n]+?)\\s*(?:to|through|-)\s*(?P<end>[^\\n]+)",
    re.IGNORECASE,
)

TAX_RE = re.compile(r"(?:tax|gst|vat)\\s*rate\\s*[:\\-]?\\s*(?P<rate>\\d+(?:\\.\\d+)?)\\s*%", re.IGNORECASE)


def parse_policy(text: str) -> Policy:
    if not text:
        return Policy()

    start_date = None
    end_date = None
    allowed_tax_rate = None

    m = DATE_RANGE_RE.search(text)
    if m:
        start = parse_date(m.group("start").strip())
        end = parse_date(m.group("end").strip())
        start_date = start.isoformat() if start else None
        end_date = end.isoformat() if end else None

    m = TAX_RE.search(text)
    if m:
        try:
            allowed_tax_rate = float(m.group("rate"))
        except Exception:
            allowed_tax_rate = None

    return Policy(start_date=start_date, end_date=end_date, allowed_tax_rate=allowed_tax_rate)
