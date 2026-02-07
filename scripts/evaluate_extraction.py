from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any


def load_jsonl(path: Path) -> list[dict]:
    rows = []
    with path.open("r", encoding="utf-8") as f:
        for line in f:
            if line.strip():
                rows.append(json.loads(line))
    return rows


def parse_float(value: Any) -> float | None:
    if value is None:
        return None
    if isinstance(value, (int, float)):
        return float(value)
    if isinstance(value, str):
        v = value.replace(",", "").strip()
        if v == "":
            return None
        try:
            return float(v)
        except ValueError:
            return None
    return None


def normalize_text(value: Any) -> str:
    if value is None:
        return ""
    return str(value).strip().lower()


def gt_to_target_schema(gt: dict) -> dict:
    invoice = gt.get("invoice", {}) if isinstance(gt, dict) else {}
    items = gt.get("items", []) if isinstance(gt, dict) else []
    subtotal = gt.get("subtotal", {}) if isinstance(gt, dict) else {}

    line_items = []
    for item in items:
        desc = item.get("description", "")
        qty = parse_float(item.get("quantity"))
        total_price = parse_float(item.get("total_price"))
        unit_price = None
        if qty and total_price is not None and qty != 0:
            unit_price = total_price / qty
        line_items.append(
            {
                "name": desc,
                "qty": qty or 0.0,
                "unit_price": unit_price or 0.0,
                "total_price": total_price or 0.0,
            }
        )

    return {
        "invoice_number": invoice.get("invoice_number", ""),
        "vendor_name": invoice.get("seller_name", ""),
        "invoice_date": invoice.get("invoice_date", ""),
        "line_items": line_items,
        "subtotal": parse_float(subtotal.get("total")),
        "tax": parse_float(subtotal.get("tax")),
        "total": parse_float(subtotal.get("total")),
    }


def item_f1(gt_items: list[dict], pred_items: list[dict]) -> float:
    if not gt_items and not pred_items:
        return 1.0
    if not gt_items or not pred_items:
        return 0.0

    gt_set = set(normalize_text(i.get("name")) for i in gt_items)
    pred_set = set(normalize_text(i.get("name")) for i in pred_items)

    tp = len(gt_set & pred_set)
    fp = len(pred_set - gt_set)
    fn = len(gt_set - pred_set)

    if tp == 0:
        return 0.0
    precision = tp / (tp + fp)
    recall = tp / (tp + fn)
    if precision + recall == 0:
        return 0.0
    return 2 * precision * recall / (precision + recall)


def field_accuracy(gt: dict, pred: dict, field: str) -> float:
    if field not in gt:
        return 0.0
    gt_val = gt.get(field)
    pred_val = pred.get(field)

    if field in {"subtotal", "tax", "total"}:
        g = parse_float(gt_val)
        p = parse_float(pred_val)
        if g is None or p is None:
            return 0.0
        return 1.0 if abs(g - p) <= 0.01 else 0.0

    if field == "invoice_date":
        return 1.0 if normalize_text(gt_val) == normalize_text(pred_val) else 0.0

    return 1.0 if normalize_text(gt_val) == normalize_text(pred_val) else 0.0


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--ground_truth", required=True)
    parser.add_argument("--predictions", required=True)
    args = parser.parse_args()

    gt_rows = load_jsonl(Path(args.ground_truth))
    pred_rows = load_jsonl(Path(args.predictions))
    pred_map = {r["image_path"]: r for r in pred_rows if "image_path" in r}

    fields = ["invoice_number", "vendor_name", "invoice_date", "subtotal", "tax", "total"]
    totals = {f: 0.0 for f in fields}
    count = 0
    f1_total = 0.0

    for row in gt_rows:
        if not row.get("labeled"):
            continue
        img = row.get("image_path")
        if img not in pred_map:
            continue
        gt = gt_to_target_schema(row.get("json_data", {}))
        pred = pred_map[img].get("extracted_json", {})

        for f in fields:
            totals[f] += field_accuracy(gt, pred, f)
        f1_total += item_f1(gt.get("line_items", []), pred.get("line_items", []))
        count += 1

    if count == 0:
        raise SystemExit("No matching labeled rows found for evaluation.")

    print(f"Samples: {count}")
    for f in fields:
        print(f"{f}_accuracy: {totals[f] / count:.4f}")
    print(f"line_items_f1: {f1_total / count:.4f}")


if __name__ == "__main__":
    main()
