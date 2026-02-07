from __future__ import annotations

from typing import Optional

from datetime import date

from ..models.types import Invoice, ValidationFlags
from ..utils.dates import parse_date
from ..utils.policy import Policy
from ..utils.vendors import VendorDB


class ComplianceEngine:
    def evaluate(
        self,
        invoice: Invoice,
        policy: Optional[Policy],
        vendor_db: Optional[VendorDB],
        flags: Optional[ValidationFlags] = None,
    ) -> dict:
        answers = {}

        if policy and policy.start_date and policy.end_date:
            inv_date = parse_date(invoice.invoice_date)
            start = parse_date(policy.start_date)
            end = parse_date(policy.end_date)
            if inv_date and start and end:
                answers["invoice_within_contract_period"] = (
                    "yes" if start <= inv_date <= end else "no"
                )
            else:
                answers["invoice_within_contract_period"] = "unknown"
        else:
            answers["invoice_within_contract_period"] = "unknown"

        if vendor_db is None:
            answers["vendor_is_approved"] = "unknown"
        else:
            answers["vendor_is_approved"] = (
                "yes" if vendor_db.find_vendor(invoice.vendor_name) is not None else "no"
            )

        if flags is not None:
            answers["invoice_internally_consistent"] = (
                "yes" if not (flags.subtotal_mismatch or flags.total_mismatch) else "no"
            )
            answers["invoice_date_not_in_future"] = "no" if flags.invoice_date_future else "yes"

        if policy and policy.allowed_tax_rate is not None:
            if invoice.subtotal > 0:
                rate = (invoice.tax / invoice.subtotal) * 100.0
                answers["tax_rate_matches_policy"] = (
                    "yes" if abs(rate - policy.allowed_tax_rate) <= 1.0 else "no"
                )
            else:
                answers["tax_rate_matches_policy"] = "unknown"
        else:
            answers["tax_rate_matches_policy"] = "unknown"

        return answers
