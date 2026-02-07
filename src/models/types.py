from __future__ import annotations

from dataclasses import dataclass
from typing import List, Optional


@dataclass
class LineItem:
    name: str
    qty: float
    unit_price: float


@dataclass
class Invoice:
    invoice_number: str
    vendor_name: str
    invoice_date: str
    line_items: List[LineItem]
    subtotal: float
    tax: float
    total: float


@dataclass
class ValidationFlags:
    subtotal_mismatch: bool = False
    total_mismatch: bool = False
    date_outside_contract: bool = False
    duplicate_invoice: bool = False
    gst_invalid: bool = False
    gst_mismatch: bool = False
    high_unit_price: bool = False
    vendor_not_found: bool = False
    invoice_date_future: bool = False
    tax_rate_unusual: bool = False


@dataclass
class RiskResult:
    risk_score: int
    risk_level: str
    justification: str
    confidence: str


@dataclass
class AuditReport:
    invoice: Invoice
    flags: ValidationFlags
    risk: RiskResult
    vlm_risk: Optional[RiskResult] = None
    compliance: Optional[dict] = None
    raw_text: Optional[str] = None
