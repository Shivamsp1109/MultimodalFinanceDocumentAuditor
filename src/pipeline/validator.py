from __future__ import annotations

import re
from datetime import date
from typing import Optional

from ..models.types import Invoice, ValidationFlags
from ..utils.dates import parse_date
from ..utils.math import compute_subtotal, nearly_equal
from ..utils.policy import Policy
from ..utils.vendors import VendorDB


class LogicalValidator:
    def __init__(self, high_unit_price_threshold: float = 10000.0):
        self.high_unit_price_threshold = high_unit_price_threshold

    def validate(
        self,
        invoice: Invoice,
        vendor_db: Optional[VendorDB] = None,
        policy: Optional[Policy] = None,
    ) -> ValidationFlags:
        flags = ValidationFlags()
        subtotal_calc = compute_subtotal(invoice.line_items)

        if not nearly_equal(subtotal_calc, invoice.subtotal):
            flags.subtotal_mismatch = True
        if not nearly_equal(invoice.subtotal + invoice.tax, invoice.total):
            flags.total_mismatch = True
        if any(item.unit_price > self.high_unit_price_threshold for item in invoice.line_items):
            flags.high_unit_price = True

        inv_date = parse_date(invoice.invoice_date)
        if inv_date and inv_date > date.today():
            flags.invoice_date_future = True

        if policy is not None:
            if policy.start_date and policy.end_date and inv_date:
                start = parse_date(policy.start_date)
                end = parse_date(policy.end_date)
                if start and end and not (start <= inv_date <= end):
                    flags.date_outside_contract = True

            if policy.allowed_tax_rate is not None and invoice.subtotal > 0:
                rate = (invoice.tax / invoice.subtotal) * 100.0
                if abs(rate - policy.allowed_tax_rate) > 1.0:
                    flags.tax_rate_unusual = True

        if vendor_db is not None:
            vendor = vendor_db.find_vendor(invoice.vendor_name)
            if vendor is None:
                flags.vendor_not_found = True
            if vendor is not None and vendor.gst_number:
                if not _valid_gst(str(vendor.gst_number)):
                    flags.gst_invalid = True
            if vendor_db.has_invoice_number(invoice.invoice_number):
                flags.duplicate_invoice = True

        return flags


GST_RE = re.compile(r"^[A-Z0-9]{6,15}$", re.IGNORECASE)


def _valid_gst(value: str) -> bool:
    return bool(GST_RE.match(value.strip()))
