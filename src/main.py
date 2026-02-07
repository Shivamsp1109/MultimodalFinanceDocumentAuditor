from __future__ import annotations

import json
from dataclasses import asdict
from pathlib import Path

from .pipeline.ocr import OcrEngine
from .pipeline.extractor import StructuredExtractor
from .pipeline.validator import LogicalValidator
from .pipeline.vlm import VlmRiskAnalyzer
from .pipeline.compliance import ComplianceEngine
from .risk.engine import RiskEngine
from .pipeline.report import render_report
from .models.types import AuditReport
from .utils.policy import parse_policy
from .utils.vendors import VendorDB


class Auditor:
    def __init__(self, model_name: str, use_vlm: bool = True, use_ocr: bool = True) -> None:
        self.ocr = OcrEngine(enabled=use_ocr)
        self.extractor = StructuredExtractor(model_name=model_name)
        self.validator = LogicalValidator()
        self.risk_engine = RiskEngine()
        self.vlm = VlmRiskAnalyzer(model_name=model_name) if use_vlm else None
        self.compliance = ComplianceEngine()

    def run(
        self,
        image_path: str,
        vendor_db: VendorDB | None = None,
        policy_text: str | None = None,
    ) -> AuditReport:
        raw_text = self.ocr.extract_text(image_path)
        invoice = self.extractor.extract(image_path=image_path, raw_text=raw_text)
        policy = parse_policy(policy_text or "")
        flags = self.validator.validate(invoice, vendor_db=vendor_db, policy=policy)
        risk = self.risk_engine.score(flags)
        vlm_risk = None
        if self.vlm is not None:
            vlm_risk = self.vlm.analyze(
                image_path=image_path, extracted_json=invoice.__dict__, flags=flags.__dict__
            )
        compliance = self.compliance.evaluate(
            invoice, policy=policy, vendor_db=vendor_db, flags=flags
        )
        return AuditReport(
            invoice=invoice,
            flags=flags,
            risk=risk,
            vlm_risk=vlm_risk,
            compliance=compliance,
            raw_text=raw_text,
        )


def main() -> None:
    import argparse

    parser = argparse.ArgumentParser()
    parser.add_argument("--input", required=True)
    parser.add_argument("--vendor_db", required=False)
    parser.add_argument("--contract_text", required=False)
    parser.add_argument("--model_name", default="Qwen/Qwen2-VL-2B-Instruct")
    parser.add_argument("--no_vlm", action="store_true")
    parser.add_argument("--no_ocr", action="store_true")
    parser.add_argument("--json_out", required=False)
    args = parser.parse_args()

    vendor_db = VendorDB(args.vendor_db) if args.vendor_db else None
    policy_text = None
    if args.contract_text:
        policy_text = Path(args.contract_text).read_text(encoding="utf-8")

    auditor = Auditor(
        model_name=args.model_name, use_vlm=not args.no_vlm, use_ocr=not args.no_ocr
    )
    report = auditor.run(args.input, vendor_db=vendor_db, policy_text=policy_text)
    print(render_report(report))

    if args.json_out:
        payload = asdict(report)
        with Path(args.json_out).open("w", encoding="utf-8") as f:
            json.dump(payload, f, ensure_ascii=False, indent=2)


if __name__ == "__main__":
    main()
