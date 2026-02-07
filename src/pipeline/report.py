from __future__ import annotations

from ..models.types import AuditReport


def render_report(report: AuditReport) -> str:
    lines = []
    lines.append(f"Invoice: {report.invoice.invoice_number}")
    lines.append(f"Vendor: {report.invoice.vendor_name}")
    lines.append(f"Date: {report.invoice.invoice_date}")
    lines.append("Flags:")
    for k, v in report.flags.__dict__.items():
        if v:
            lines.append(f"- {k}")
    lines.append(f"Risk: {report.risk.risk_score} ({report.risk.risk_level})")
    lines.append(f"Justification: {report.risk.justification}")
    if report.vlm_risk is not None:
        lines.append(f"VLM Risk: {report.vlm_risk.risk_score} ({report.vlm_risk.risk_level})")
        lines.append(f"VLM Justification: {report.vlm_risk.justification}")
    if report.compliance is not None:
        lines.append("Compliance:")
        for k, v in report.compliance.items():
            lines.append(f"- {k}: {v}")
    return "\n".join(lines)
