from __future__ import annotations

from dataclasses import dataclass
from typing import Optional

import pandas as pd


@dataclass
class VendorRecord:
    vendor_name: str
    gst_number: Optional[str] = None


class VendorDB:
    def __init__(self, csv_path: str) -> None:
        self.csv_path = csv_path
        self.df = pd.read_csv(csv_path)

    def find_vendor(self, name: str) -> Optional[VendorRecord]:
        if "vendor_name" not in self.df.columns:
            return None
        matches = self.df[self.df["vendor_name"].str.lower() == str(name).strip().lower()]
        if matches.empty:
            return None
        row = matches.iloc[0]
        gst = row.get("gst_number") if "gst_number" in self.df.columns else None
        return VendorRecord(vendor_name=row["vendor_name"], gst_number=gst)

    def has_invoice_number(self, invoice_number: str) -> bool:
        if "invoice_number" not in self.df.columns:
            return False
        return bool(
            (self.df["invoice_number"].astype(str).str.strip() == str(invoice_number).strip()).any()
        )
