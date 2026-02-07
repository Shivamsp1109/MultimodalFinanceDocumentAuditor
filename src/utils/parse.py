from __future__ import annotations

import ast
import json
from typing import Any


def extract_json_block(text: str) -> dict[str, Any]:
    start = text.find("{")
    end = text.rfind("}")
    if start == -1 or end == -1 or end <= start:
        raise ValueError("No JSON object found in model output.")
    block = text[start : end + 1]
    try:
        return json.loads(block)
    except json.JSONDecodeError:
        # Fallback: try Python literal (handles single quotes)
        try:
            obj = ast.literal_eval(block)
            if isinstance(obj, dict):
                return obj
        except Exception as exc:
            raise ValueError(f"Failed to parse JSON from model output: {exc}") from exc
        raise ValueError("Failed to parse JSON from model output.")
