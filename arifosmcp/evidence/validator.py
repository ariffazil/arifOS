from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from hashlib import sha256
from typing import Any


class EvidenceLevel(str, Enum):
    L0 = "L0"
    L1 = "L1"
    L2 = "L2"
    L3 = "L3"
    L4 = "L4"
    L5 = "L5"
    L6 = "L6"


@dataclass(frozen=True)
class ValidationResult:
    valid: bool
    reason: str | None = None
    error: str | None = None


@dataclass(frozen=True)
class SufficiencyResult:
    verdict: str
    reason: str | None
    gap: int | None
    human_judgment_required: bool


def calculate_max_evidence_level(receipt: dict[str, Any] | None) -> EvidenceLevel:
    if not isinstance(receipt, dict):
        return EvidenceLevel.L0

    urls_ingested = int(receipt.get("urls_ingested", 0) or 0)
    independent = int(receipt.get("independent_sources_compared", 0) or 0)
    rendered = bool(receipt.get("rendered_inspection", False))
    pdf = bool(receipt.get("pdf_inspection", False))
    screenshot = bool(receipt.get("screenshot_inspection", False))
    deep_plan = bool(receipt.get("deep_research_plan_completed", False))
    contradiction = bool(receipt.get("contradiction_audit_completed", False))
    void_rep = bool(receipt.get("void_report_completed", False))

    max_level = EvidenceLevel.L0
    if receipt.get("query_sent") or int(receipt.get("results_returned", 0) or 0) >= 1:
        max_level = EvidenceLevel.L1
    if urls_ingested >= 1:
        max_level = EvidenceLevel.L2
    if independent >= 2:
        max_level = EvidenceLevel.L3
    if rendered or pdf or screenshot:
        max_level = EvidenceLevel.L4
    if deep_plan and contradiction and void_rep and max_level in (EvidenceLevel.L3, EvidenceLevel.L4):
        max_level = EvidenceLevel.L5

    return max_level


def validate_sufficiency(
    receipt: dict[str, Any] | None, claimed_level: str | None
) -> SufficiencyResult:
    if not receipt or not isinstance(receipt, dict):
        return SufficiencyResult("HOLD", "evidence_receipt_missing", None, True)

    risk_flags = receipt.get("risk_flags", [])
    if risk_flags:
        return SufficiencyResult(
            "VOID",
            f"external_instruction_detected: {risk_flags}",
            None,
            True,
        )

    proven_max = calculate_max_evidence_level(receipt)

    if claimed_level is None:
        return SufficiencyResult("SEAL", f"proven_max_level={proven_max.value}", 0, False)

    level_order = {level.value: index for index, level in enumerate(EvidenceLevel)}
    claimed_rank = level_order.get(str(claimed_level), 99)
    proven_rank = level_order.get(proven_max.value, 0)

    if claimed_rank == 99:
        return SufficiencyResult("HOLD", f"invalid_claimed_level:{claimed_level}", None, True)

    if claimed_rank > proven_rank:
        return SufficiencyResult(
            "HOLD",
            f"evidence_inflation: claimed_{claimed_level} but proven_max={proven_max.value}",
            claimed_rank - proven_rank,
            True,
        )

    return SufficiencyResult(
        "SEAL",
        f"claimed_{claimed_level} within proven_max={proven_max.value}",
        proven_rank - claimed_rank,
        False,
    )


def classify_void(receipt: dict[str, Any] | None) -> str:
    """Classify a receipt's void status."""
    if not receipt:
        return "VOID"
    risk_flags = receipt.get("risk_flags", [])
    if risk_flags:
        return "VOID"
    return "VALID"


def build_void_report(receipts: list[dict[str, Any]]) -> dict[str, Any]:
    receipts = receipts or []
    risk_flags: list[str] = []
    for receipt in receipts:
        risk_flags.extend([str(flag) for flag in receipt.get("risk_flags", [])])

    payload = {
        "status": "VOID",
        "verdict": "VOID",
        "receipts_audited": len(receipts),
        "risk_flags": sorted(set(risk_flags)),
        "human_judgment_required": bool(risk_flags) or len(receipts) == 0,
        "void_report_completed": True,
        "max_evidence_level": max(
            (calculate_max_evidence_level(r).value for r in receipts),
            default=EvidenceLevel.L0.value,
        ),
    }
    payload["void_id"] = f"void://{sha256(repr(payload).encode()).hexdigest()[:16]}"
    return payload
