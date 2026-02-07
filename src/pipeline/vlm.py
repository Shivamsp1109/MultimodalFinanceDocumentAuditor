from __future__ import annotations

from typing import Any

from ..models.qwen_vl import QwenVL
from ..models.types import RiskResult
from ..utils.parse import extract_json_block


class VlmRiskAnalyzer:
    def __init__(self, model_name: str) -> None:
        self.model = QwenVL(model_name=model_name, max_new_tokens=256)

    def analyze(self, image_path: str, extracted_json: dict, flags: dict) -> RiskResult:
        prompt = (
            "Analyze this invoice for fraud risk. "
            "Return JSON with keys: risk_score (0-100), risk_level, "
            "justification, confidence. "
            f"Validation issues found: {flags}. "
            f"Extracted JSON: {extracted_json}. "
            "Return only JSON."
        )
        output = self.model.generate(prompt=prompt, image_path=image_path)
        data = extract_json_block(output)
        return RiskResult(
            risk_score=int(data.get("risk_score", 0)),
            risk_level=str(data.get("risk_level", "")),
            justification=str(data.get("justification", "")),
            confidence=str(data.get("confidence", "")),
        )
