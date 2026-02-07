from __future__ import annotations

from datetime import date
from typing import Optional

from dateutil import parser


def parse_date(value: str) -> Optional[date]:
    if not value:
        return None
    try:
        return parser.parse(value, fuzzy=True).date()
    except Exception:
        return None
