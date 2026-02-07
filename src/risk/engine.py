from __future__ import annotations

from ..models.types import RiskResult, ValidationFlags


class RiskEngine:
    def score(self, flags: ValidationFlags) -> RiskResult:
        score = 0
        if flags.subtotal_mismatch:
            score += 25
        if flags.total_mismatch:
            score += 25
        if flags.high_unit_price:
            score += 20
        if flags.gst_invalid:
            score += 10
        if flags.gst_mismatch:
            score += 10
        if flags.duplicate_invoice:
            score += 10
        if flags.date_outside_contract:
            score += 10
        if flags.vendor_not_found:
            score += 15
        if flags.invoice_date_future:
            score += 15
        if flags.tax_rate_unusual:
            score += 10

        if score >= 70:
            level = "high"
        elif score >= 40:
            level = "medium"
        else:
            level = "low"

        return RiskResult(
            risk_score=score,
            risk_level=level,
            justification="Rule-based risk scoring from validation flags.",
            confidence="medium",
        )
