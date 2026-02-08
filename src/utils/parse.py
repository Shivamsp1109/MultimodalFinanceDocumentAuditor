from __future__ import annotations

import ast
import json
from typing import Any, Optional


def _first_balanced_object(text: str) -> Optional[str]:
    start = text.find("{")
    if start == -1:
        return None
    depth = 0
    in_string = False
    escape = False
    for i in range(start, len(text)):
        ch = text[i]
        if in_string:
            if escape:
                escape = False
            elif ch == "\\":
                escape = True
            elif ch == '"':
                in_string = False
            continue
        if ch == '"':
            in_string = True
        elif ch == "{":
            depth += 1
        elif ch == "}":
            depth -= 1
            if depth == 0:
                return text[start : i + 1]
    return None


def extract_json_block(text: str) -> dict[str, Any]:
    block = _first_balanced_object(text)
    if not block:
        raise ValueError("No JSON object found in model output.")
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
