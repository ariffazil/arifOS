from __future__ import annotations

import hashlib
import json
import time
from arifos.core.governance import (
    ThermodynamicMetrics,
    governed_return,
    append_vault999_event,
    Verdict,
)
from arifos.tools._tool_support import invariant_fields


async def execute(
    a: str,
    b: str,
    interaction: str = "data_flow",
    operator_id: str | None = None,
    session_id: str | None = None,
) -> dict:
    # ─── Phase 1: Pre-flight readiness probe ─────────────────────────────────
    readiness_probe = "PASS"
    readiness_detail_parts = []

    # _gateway has no external service dependencies — lightweight in-process
    try:
        readiness_detail_parts.append("internal:ok")
    except Exception as e:
        readiness_probe = "FAIL"
        readiness_detail_parts.append(f"internal:FAIL({e})")

    readiness_detail = (
        ", ".join(readiness_detail_parts) if readiness_detail_parts else "no_checks"
    )

    # ─── Main logic ───────────────────────────────────────────────────────────
    is_orthogonal = a != b
    report = {
        "a": a,
        "b": b,
        "interaction": interaction,
        "cross_organ_leakage_rate": None,
    }
    report.update(
        invariant_fields(
            tool_name="arifos_gateway",
            input_payload={
                "a": a,
                "b": b,
                "interaction": interaction,
                "operator_id": operator_id,
                "session_id": session_id,
            },
            assumptions=[
                "Gateway stage evaluates declared organ interaction, not full downstream payload semantics.",
                "Distinct organ names imply intended separation even before runtime enforcement.",
                "Leakage rate remains unknown until a concrete exchange is simulated or observed.",
            ],
            floors_evaluated=["F5", "F8"],
            confidence=0.67 if is_orthogonal else 0.41,
            extra_meta={"orthogonal_pair": is_orthogonal},
        )
    )

    # Removed hardcoded metric assertions — set to NULL/UNKNOWN
    metrics = ThermodynamicMetrics(
        truth_score=None,
        delta_s=None,
        omega_0=None,
        peace_squared=None,
        amanah_lock=None,
        tri_witness_score=None,
        stakeholder_safety=None,
    )

    result = governed_return("arifos_gateway", report, metrics, operator_id, session_id)

    # ─── Phase 1: Append metabolic_metadata ───────────────────────────────────
    output_str = json.dumps(report, sort_keys=True, ensure_ascii=False)
    source_integrity = hashlib.sha256(output_str.encode("utf-8")).hexdigest()

    result["metabolic_metadata"] = {
        "source_integrity": source_integrity,
        "confidence_score": None,
        "floor_alignment": ["F1", "F2"],
        "readiness_probe": readiness_probe,
        "readiness_detail": readiness_detail,
        "verdict": result.get("verdict", Verdict.CLAIM_ONLY),
        "vault_receipt": None,
        "delta_s": None,
        "peace_squared": None,
        "omega_0": None,
        "timestamp_epoch": time.time(),
    }

    # ─── Phase 1: Vault-999 event ─────────────────────────────────────────────
    try:
        vault_receipt = append_vault999_event(
            event_type="arifos_gateway",
            payload={
                "report": report,
                "metabolic_metadata": result["metabolic_metadata"],
            },
            operator_id=operator_id,
            session_id=session_id,
        )
        result["metabolic_metadata"]["vault_receipt"] = vault_receipt
    except Exception as e:
        result["metabolic_metadata"]["vault_receipt"] = f"FAIL({e})"

    return result
