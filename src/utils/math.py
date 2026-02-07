from __future__ import annotations

from typing import List
from ..models.types import LineItem


def compute_subtotal(items: List[LineItem]) -> float:
    return sum(i.qty * i.unit_price for i in items)


def nearly_equal(a: float, b: float, eps: float = 0.01) -> bool:
    return abs(a - b) <= eps
