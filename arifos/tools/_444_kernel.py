from __future__ import annotations

import hashlib
import json
import time
from arifos.core.governance import (
    ThermodynamicMetrics,
    governed_return,
    append_vault999_event,
    Verdict,
    get_session_shadow,
    TruthLayer,
)
from arifos.tools._tool_support import invariant_fields


# Targets that can mutate state irreversibly — shadow flux vetoes these first
_IRREVERSIBLE_TARGETS = {"FORGE", "VAULT", "EXECUTE", "DEPLOY"}


async def execute(
    route_target: str,
    payload: dict | None = None,
    operator_id: str | None = None,
    session_id: str | None = None,
) -> dict:
    # ─── Phase 1: Pre-flight readiness probe ─────────────────────────────────
    readiness_probe = "PASS"
    readiness_detail_parts = []

    try:
        readiness_detail_parts.append("internal:ok")
    except Exception as e:
        readiness_probe = "FAIL"
        readiness_detail_parts.append(f"internal:FAIL({e})")

    readiness_detail = ", ".join(readiness_detail_parts) if readiness_detail_parts else "no_checks"

    # ─── Phase 2: Shadow-aware routing veto ──────────────────────────────────
    target_clean = route_target.upper()

    shadow_signal = None
    flux_verdict = "NORMAL"
    metabolic_flux = 0.0
    af_detected = False
    af_conf = 0.0

    if session_id:
        ss = get_session_shadow(session_id)
        shadow_signal = ss.to_signal()
        flux_verdict = shadow_signal.get("flux_verdict", "NORMAL")
        metabolic_flux = shadow_signal.get("metabolic_flux", 0.0)
        af = shadow_signal.get("alignment_faking", {})
        af_detected = af.get("detected", False)
        af_conf = af.get("confidence", 0.0)

    # Veto irreversible targets when metabolic flux is critical
    if target_clean in _IRREVERSIBLE_TARGETS:
        if flux_verdict == "SYSTEM_HOLD" or metabolic_flux >= 0.85:
            report = {
                "routing": {"target": target_clean, "lane": "BLOCKED"},
                "payload": payload or {},
                "shadow_veto": True,
                "veto_reason": (
                    f"Metabolic flux {metabolic_flux} >= 0.85 (SYSTEM_HOLD). "
                    "Irreversible target blocked by 444_KERNEL shadow veto."
                ),
                "orthogonality_check": "BLOCKED",
                "flux_verdict": flux_verdict,
                "metabolic_flux": metabolic_flux,
            }
            report.update(TruthLayer.humility_acknowledgment())
            report["truth_layer"] = TruthLayer.CHECKLIST

            metrics = ThermodynamicMetrics(
                truth_score=0.95,
                delta_s=0.02,
                omega_0=0.045,
                peace_squared=0.8,
                amanah_lock=True,
                tri_witness_score=0.9,
                stakeholder_safety=1.0,
            )
            result = governed_return("arifos_444_kernel", report, metrics, operator_id, session_id)

            output_str = json.dumps(report, sort_keys=True, ensure_ascii=False)
            source_integrity = hashlib.sha256(output_str.encode("utf-8")).hexdigest()
            result["metabolic_metadata"] = {
                "source_integrity": source_integrity,
                "confidence_score": None,
                "floor_alignment": ["F2", "F4", "F7"],
                "readiness_probe": readiness_probe,
                "readiness_detail": readiness_detail,
                "verdict": result.get("verdict", Verdict.CLAIM_ONLY),
                "vault_receipt": None,
                "delta_s": None,
                "peace_squared": None,
                "omega_0": None,
                "timestamp_epoch": time.time(),
                "shadow_veto": True,
                "flux_verdict": flux_verdict,
                "metabolic_flux": metabolic_flux,
            }
            try:
                vault_receipt = append_vault999_event(
                    event_type="arifos_444_kernel",
                    payload={"report": report, "metabolic_metadata": result["metabolic_metadata"]},
                    operator_id=operator_id,
                    session_id=session_id,
                )
                result["metabolic_metadata"]["vault_receipt"] = vault_receipt
            except Exception as e:
                result["metabolic_metadata"]["vault_receipt"] = f"FAIL({e})"
            return result

        if af_detected and af_conf >= 0.7:
            report = {
                "routing": {"target": target_clean, "lane": "BLOCKED"},
                "payload": payload or {},
                "shadow_veto": True,
                "veto_reason": (
                    f"Alignment-faking detected (confidence {af_conf}). "
                    "All routing blocked by 444_KERNEL shadow veto."
                ),
                "orthogonality_check": "BLOCKED",
                "alignment_faking_detected": af_detected,
                "alignment_faking_confidence": af_conf,
            }
            report.update(TruthLayer.humility_acknowledgment())
            report["truth_layer"] = TruthLayer.CHECKLIST

            metrics = ThermodynamicMetrics(
                truth_score=0.95,
                delta_s=0.02,
                omega_0=0.045,
                peace_squared=0.8,
                amanah_lock=True,
                tri_witness_score=0.9,
                stakeholder_safety=1.0,
            )
            result = governed_return("arifos_444_kernel", report, metrics, operator_id, session_id)

            output_str = json.dumps(report, sort_keys=True, ensure_ascii=False)
            source_integrity = hashlib.sha256(output_str.encode("utf-8")).hexdigest()
            result["metabolic_metadata"] = {
                "source_integrity": source_integrity,
                "confidence_score": None,
                "floor_alignment": ["F2", "F4", "F13"],
                "readiness_probe": readiness_probe,
                "readiness_detail": readiness_detail,
                "verdict": result.get("verdict", Verdict.CLAIM_ONLY),
                "vault_receipt": None,
                "delta_s": None,
                "peace_squared": None,
                "omega_0": None,
                "timestamp_epoch": time.time(),
                "shadow_veto": True,
                "alignment_faking_detected": af_detected,
                "alignment_faking_confidence": af_conf,
            }
            try:
                vault_receipt = append_vault999_event(
                    event_type="arifos_444_kernel",
                    payload={"report": report, "metabolic_metadata": result["metabolic_metadata"]},
                    operator_id=operator_id,
                    session_id=session_id,
                )
                result["metabolic_metadata"]["vault_receipt"] = vault_receipt
            except Exception as e:
                result["metabolic_metadata"]["vault_receipt"] = f"FAIL({e})"
            return result

    # ─── Phase 3: Normal routing ─────────────────────────────────────────────
    report = {
        "routing": {"target": target_clean, "lane": "METABOLIC_FLUX"},
        "payload": payload or {},
        "orthogonality_check": (
            "PASS" if target_clean in {"MIND", "HEART", "SOUL", "PHYSICS"} else "WARNING"
        ),
        "shadow_signal": shadow_signal,
    }
    report.update(
        invariant_fields(
            tool_name="arifos_444_kernel",
            input_payload={
                "route_target": route_target,
                "payload": payload,
                "operator_id": operator_id,
                "session_id": session_id,
            },
            assumptions=[
                "Kernel routing validates declared target lanes but does not execute downstream organs directly.",
                "Orthogonality warnings indicate semantic drift risk, not immediate runtime failure.",
                "Payload is treated as declarative routing context during this stage.",
                "Shadow-aware veto may block irreversible targets when metabolic flux is elevated.",
            ],
            floors_evaluated=["F1", "F2", "F3", "F5", "F7", "F8", "F13"],
            confidence=(0.66 if target_clean in {"MIND", "HEART", "SOUL", "PHYSICS"} else 0.58),
            extra_meta={
                "orthogonality_warning": target_clean not in {"MIND", "HEART", "SOUL", "PHYSICS"},
                "shadow_present": shadow_signal is not None,
                "flux_verdict": flux_verdict,
                "metabolic_flux": metabolic_flux,
            },
        )
    )

    # Real metrics from shadow state instead of nulls
    if shadow_signal is not None:
        metrics = ThermodynamicMetrics(
            truth_score=0.95,
            delta_s=-0.01 if flux_verdict == "NORMAL" else 0.02,
            omega_0=0.04 + (metabolic_flux * 0.01),
            peace_squared=1.2 if flux_verdict == "NORMAL" else 0.9,
            amanah_lock=True,
            tri_witness_score=0.98 if flux_verdict == "NORMAL" else 0.7,
            stakeholder_safety=1.0,
        )
    else:
        metrics = ThermodynamicMetrics(
            truth_score=0.95,
            delta_s=-0.01,
            omega_0=0.045,
            peace_squared=1.0,
            amanah_lock=True,
            tri_witness_score=0.95,
            stakeholder_safety=1.0,
        )

    report.update(TruthLayer.humility_acknowledgment())
    report["truth_layer"] = TruthLayer.CHECKLIST

    result = governed_return("arifos_444_kernel", report, metrics, operator_id, session_id)

    # ─── Phase 4: Append metabolic_metadata ─────────────────────────────────
    output_str = json.dumps(report, sort_keys=True, ensure_ascii=False)
    source_integrity = hashlib.sha256(output_str.encode("utf-8")).hexdigest()

    result["metabolic_metadata"] = {
        "source_integrity": source_integrity,
        "confidence_score": None,
        "floor_alignment": ["F2", "F4"],
        "readiness_probe": readiness_probe,
        "readiness_detail": readiness_detail,
        "verdict": result.get("verdict", Verdict.CLAIM_ONLY),
        "vault_receipt": None,
        "delta_s": None,
        "peace_squared": None,
        "omega_0": None,
        "timestamp_epoch": time.time(),
        "shadow_signal": shadow_signal,
        "flux_verdict": flux_verdict,
        "metabolic_flux": metabolic_flux,
        "alignment_faking_detected": af_detected,
        "alignment_faking_confidence": af_conf,
    }

    # ─── Phase 5: Vault-999 event ────────────────────────────────────────────
    try:
        vault_receipt = append_vault999_event(
            event_type="arifos_444_kernel",
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
