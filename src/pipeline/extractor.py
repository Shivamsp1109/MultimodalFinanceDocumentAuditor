from __future__ import annotations

from typing import Any

from ..models.qwen_vl import QwenVL
from ..models.types import Invoice, LineItem
from ..utils.parse import extract_json_block


class StructuredExtractor:
    def __init__(self, model_name: str) -> None:
        self.model = QwenVL(model_name=model_name, max_new_tokens=512)

    def extract(self, image_path: str, raw_text: str) -> Invoice:
        prompt = (
            "Extract a JSON object with keys: "
            "invoice_number, vendor_name, invoice_date, "
            "line_items (name, qty, unit_price), subtotal, tax, total. "
            "Return only JSON."
        )
        output = self.model.generate(prompt=prompt, image_path=image_path)
        data = extract_json_block(output)
        items = [
            LineItem(
                name=item.get("name", ""),
                qty=float(item.get("qty", 0)),
                unit_price=float(item.get("unit_price", 0)),
            )
            for item in data.get("line_items", [])
        ]
        return Invoice(
            invoice_number=str(data.get("invoice_number", "")),
            vendor_name=str(data.get("vendor_name", "")),
            invoice_date=str(data.get("invoice_date", "")),
            line_items=items,
            subtotal=float(data.get("subtotal", 0)),
            tax=float(data.get("tax", 0)),
            total=float(data.get("total", 0)),
        )
