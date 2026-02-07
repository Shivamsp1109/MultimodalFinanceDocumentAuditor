from __future__ import annotations

import json
from typing import Any


def extract_json_block(text: str) -> dict[str, Any]:
    start = text.find("{")
    end = text.rfind("}")
    if start == -1 or end == -1 or end <= start:
        raise ValueError("No JSON object found in model output.")
    block = text[start : end + 1]
    return json.loads(block)
