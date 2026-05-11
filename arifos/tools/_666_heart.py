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
    stakeholder_map: dict | None = None,
    action_proposal: dict | None = None,
    operator_id: str | None = None,
    session_id: str | None = None,
) -> dict:
    # ─── Phase 1: Pre-flight readiness probe ─────────────────────────────────
    readiness_probe = "PASS"
    readiness_detail_parts = []

    # _666_heart has no external service dependencies — lightweight in-process
    try:
        readiness_detail_parts.append("internal:ok")
    except Exception as e:
        readiness_probe = "FAIL"
        readiness_detail_parts.append(f"internal:FAIL({e})")

    readiness_detail = ", ".join(readiness_detail_parts) if readiness_detail_parts else "no_checks"

    # ─── Main logic ───────────────────────────────────────────────────────────
    report = {
        "stakeholders": stakeholder_map or {},
        "proposal": action_proposal or {},
        "harm_avoidance_rate": None,
        "weakest_stakeholder_protected": None,
    }
    report.update(
        invariant_fields(
            tool_name="arifos_666_heart",
            input_payload={
                "stakeholder_map": stakeholder_map,
                "action_proposal": action_proposal,
                "operator_id": operator_id,
                "session_id": session_id,
            },
            assumptions=[
                "Heart stage evaluates declared stakeholder context, not hidden stakeholders outside the provided map.",
                "Absent harm metrics are treated as uncertainty, not proof of safety.",
                "Action proposals are reviewed constitutionally before any execution stage.",
            ],
            floors_evaluated=["F1", "F3", "F6", "F9", "F10"],
            confidence=0.62,
            extra_meta={"stakeholder_count": len(stakeholder_map or {})},
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

    result = governed_return("arifos_666_heart", report, metrics, operator_id, session_id)

    # ─── Phase 1: Append metabolic_metadata ───────────────────────────────────
    output_str = json.dumps(report, sort_keys=True, ensure_ascii=False)
    source_integrity = hashlib.sha256(output_str.encode("utf-8")).hexdigest()

    result["metabolic_metadata"] = {
        "source_integrity": source_integrity,
        "confidence_score": None,
        "floor_alignment": ["F6", "F7"],
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
            event_type="arifos_666_heart",
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
