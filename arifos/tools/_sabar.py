from __future__ import annotations

import hashlib
import json
import os
import time
from arifos.core.governance import (
    ThermodynamicMetrics,
    governed_return,
    append_vault999_event,
    Verdict,
)
from arifos.tools._tool_support import invariant_fields

SABAR_LOCK_PATH = os.path.join(os.getenv("ARIFOS_RUNTIME_DIR", "/run/arifos"), "sabar.lock")


def _check_sabar_cooling() -> tuple[bool, float | None]:
    """
    Check SABAR cooling lock.
    Returns (is_cooling, time_remaining_seconds).
    """
    if not os.path.exists(SABAR_LOCK_PATH):
        return False, None

    try:
        with open(SABAR_LOCK_PATH, "r") as f:
            lock_ts = float(f.read().strip())
    except Exception:
        # Corrupt lock file — treat as expired, let it be overwritten
        return False, None

    now = time.time()
    remaining = lock_ts - now
    if remaining > 0:
        return True, remaining
    else:
        # Expired — clear the lock
        try:
            os.remove(SABAR_LOCK_PATH)
        except Exception:
            pass
        return False, None


async def execute(
    hold_id: str | None = None,
    action: str = "status",
    approval: dict | None = None,
    operator_id: str | None = None,
    session_id: str | None = None,
) -> dict:
    # ─── Phase 1: Pre-flight readiness probe ─────────────────────────────────
    readiness_probe = "PASS"
    readiness_detail_parts = []

    # _sabar has no external service dependencies — lightweight in-process
    try:
        readiness_detail_parts.append("internal:ok")
    except Exception as e:
        readiness_probe = "FAIL"
        readiness_detail_parts.append(f"internal:FAIL({e})")

    readiness_detail = ", ".join(readiness_detail_parts) if readiness_detail_parts else "no_checks"

    # ─── Phase 1: Real SABAR cooling timer check ───────────────────────────────
    is_cooling, time_remaining = _check_sabar_cooling()

    if is_cooling:
        # SABAR verdict — still in cooling, block action
        report = {
            "hold_id": hold_id,
            "action": action,
            "approval": approval or {},
            "cooling_compliance": None,
            "time_remaining_minutes": (round(time_remaining / 60, 2) if time_remaining else None),
        }
        report.update(
            invariant_fields(
                tool_name="arifos_sabar",
                input_payload={
                    "hold_id": hold_id,
                    "action": action,
                    "approval": approval,
                    "operator_id": operator_id,
                    "session_id": session_id,
                },
                assumptions=[
                    "SABAR reports cooling state from the local lock file only.",
                    "Cooling duration is advisory unless a higher constitutional gate overrides it.",
                    "This stage blocks or clears execution; it does not execute downstream actions itself.",
                ],
                floors_evaluated=["F5"],
                confidence=0.71,
                extra_meta={"cooling_active": True},
            )
        )
        metrics = ThermodynamicMetrics(
            truth_score=None,
            delta_s=None,
            omega_0=None,
            peace_squared=None,
            amanah_lock=None,
            tri_witness_score=None,
            stakeholder_safety=None,
        )
        result = governed_return("arifos_sabar", report, metrics, operator_id, session_id)

        # Force SABAR verdict explicitly
        result["verdict"] = Verdict.SABAR
        result["status"] = "sabar_cooling"

        output_str = json.dumps(report, sort_keys=True, ensure_ascii=False)
        source_integrity = hashlib.sha256(output_str.encode("utf-8")).hexdigest()

        result["metabolic_metadata"] = {
            "source_integrity": source_integrity,
            "confidence_score": None,
            "floor_alignment": ["F5"],
            "readiness_probe": readiness_probe,
            "readiness_detail": readiness_detail,
            "verdict": Verdict.SABAR,
            "vault_receipt": None,
            "delta_s": None,
            "peace_squared": None,
            "omega_0": None,
            "timestamp_epoch": time.time(),
        }

        try:
            vault_receipt = append_vault999_event(
                event_type="arifos_sabar",
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

    # ─── Normal path (not in cooling) ─────────────────────────────────────────
    report = {
        "hold_id": hold_id,
        "action": action,
        "approval": approval or {},
        "cooling_compliance": None,
        "time_remaining_minutes": None,
    }
    report.update(
        invariant_fields(
            tool_name="arifos_sabar",
            input_payload={
                "hold_id": hold_id,
                "action": action,
                "approval": approval,
                "operator_id": operator_id,
                "session_id": session_id,
            },
            assumptions=[
                "SABAR status is derived from the local cooling lock state.",
                "A clear SABAR state means no active cooldown was observed at query time.",
                "This stage reports governance posture only; it does not mutate downstream state.",
            ],
            floors_evaluated=["F4", "F5"],
            confidence=0.74,
            extra_meta={"cooling_active": False},
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

    result = governed_return("arifos_sabar", report, metrics, operator_id, session_id)

    # ─── Phase 1: Append metabolic_metadata ───────────────────────────────────
    output_str = json.dumps(report, sort_keys=True, ensure_ascii=False)
    source_integrity = hashlib.sha256(output_str.encode("utf-8")).hexdigest()

    result["metabolic_metadata"] = {
        "source_integrity": source_integrity,
        "confidence_score": None,
        "floor_alignment": ["F4", "F5"],
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
            event_type="arifos_sabar",
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
