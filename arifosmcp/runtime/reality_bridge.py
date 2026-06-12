"""
arifosmcp/runtime/reality_bridge.py
══════════════════════════════════════
REALITY ENGINEERING BRIDGE — Forged 2026-06-12 by Omega (Ω)

Single integration point that wires all 6 reality engineering harnesses
into the arifOS governance pipeline.

This module is ADDITIVE. It does not mutate the existing kernel.
It provides drop-in replacements for governance_pipeline gates.

Gates wired:
  GATE 0: Session → session_enforcer.enforce_session()
  GATE 1: Identity → (unchanged from governance_pipeline)
  GATE 3: Risk → risk_ledger.gate_risk()
  GATE 7: Envelope → envelope_validator.gate_envelope()
  POST: Incident → incident_harness.classify_incident()
  POST: Cooling → cooling_harness.record_shadow_candidate()

F1 AMANAH: All operations additive, fail-closed, non-destructive.
F2 TRUTH: Every gate decision carries reason + evidence.
F13 SOVEREIGN: Risk gate preserves F13 override path.

DITEMPA BUKAN DIBERI
"""

from __future__ import annotations

import logging
import time
from typing import Any

from arifosmcp.runtime.session_enforcer import enforce_session, SessionVerdict
from arifosmcp.runtime.envelope_validator import validate_envelope, EnvelopeVerdict
from arifosmcp.runtime.incident_harness import classify_incident, IncidentClass
from arifosmcp.runtime.cooling_harness import record_shadow_candidate
from arifosmcp.runtime.risk_ledger import gate_risk, RiskVerdict

logger = logging.getLogger("arifosmcp.reality_bridge")

# ── Bridge state ────────────────────────────────────────────────────
_bridge_enabled: bool = True
_sessions_gated: int = 0
_envelopes_gated: int = 0
_risks_gated: int = 0
_incidents_classified: int = 0


def bridge_enabled() -> bool:
    return _bridge_enabled


def enable_bridge() -> None:
    global _bridge_enabled
    _bridge_enabled = True
    logger.info("[reality_bridge] ENABLED — all gates active")


def disable_bridge() -> None:
    global _bridge_enabled
    _bridge_enabled = False
    logger.info("[reality_bridge] DISABLED — gates bypassed (emergency mode)")


# ── Gate 0: Session ─────────────────────────────────────────────────


def session_gate(
    tool_name: str, session_id: str | None = None, actor_id: str | None = None
) -> tuple[bool, dict[str, Any]]:
    """
    Gate 0: Session existence and validity.
    Uses session_enforcer to check session_id is valid for this tool.

    Returns: (allowed: bool, receipt: dict)
    """
    global _sessions_gated
    if not _bridge_enabled:
        return True, {"verdict": "BRIDGE_DISABLED"}

    result = enforce_session(tool_name, session_id=session_id, actor_id=actor_id)
    _sessions_gated += 1

    allowed = result["verdict"] == SessionVerdict.VALID
    receipt = {
        "gate": "SESSION",
        "verdict": result["verdict"].value,
        "allowed": allowed,
        "reason": result.get("reason", ""),
        "session_id": result.get("session_id"),
        "tier": result.get("tier"),
    }
    return allowed, receipt


# ── Gate 7: Envelope ────────────────────────────────────────────────


def envelope_gate(
    tool_name: str,
    envelope: dict[str, Any] | None = None,
    action_class: str = "READ",
    policy_hash: str | None = None,
    f13_signature: str | None = None,
) -> tuple[bool, dict[str, Any]]:
    """
    Gate 7: Envelope validation.
    Uses envelope_validator to verify FederationEnvelope.

    Returns: (allowed: bool, receipt: dict)
    """
    global _envelopes_gated
    if not _bridge_enabled:
        return True, {"verdict": "BRIDGE_DISABLED"}

    check = validate_envelope(
        tool_name=tool_name,
        envelope=envelope,
        action_class=action_class,
        policy_hash=policy_hash,
        f13_signature=f13_signature,
    )
    _envelopes_gated += 1

    allowed = check.verdict == EnvelopeVerdict.VALID
    receipt = {
        "gate": "ENVELOPE",
        "verdict": check.verdict.value,
        "allowed": allowed,
        "reasons": check.reasons,
        "policy_hash_match": check.policy_hash_match,
        "authority_valid": check.authority_valid,
        "tool_allowed": check.tool_allowed,
        "f13_present": check.f13_present,
    }
    return allowed, receipt


# ── Gate 3: Risk ────────────────────────────────────────────────────


def risk_gate(
    tool_name: str,
    action_class: str = "READ",
    ack_irreversible: bool = False,
    session_id: str | None = None,
    f13_signature: str = "",
    **kwargs: Any,
) -> tuple[bool, dict[str, Any]]:
    """
    Gate 3: Risk passport.
    Uses risk_ledger to gate high-risk actions.

    Returns: (allowed: bool, receipt: dict)
    """
    global _risks_gated
    if not _bridge_enabled:
        return True, {"verdict": "BRIDGE_DISABLED"}

    assessment = gate_risk(
        tool_name=tool_name,
        action_class=action_class,
        ack_irreversible=ack_irreversible,
        session_id=session_id,
        f13_signature=f13_signature,
        **kwargs,
    )
    _risks_gated += 1

    allowed = assessment.verdict in (
        RiskVerdict.APPROVE,
        RiskVerdict.CAUTION,
        RiskVerdict.SUPERVISED,
    )
    receipt = {
        "gate": "RISK",
        "verdict": assessment.verdict.value,
        "allowed": allowed,
        "proximity": assessment.proximity,
        "proximity_band": assessment.proximity_band.value,
        "reasons": assessment.reasons,
        "f13_override": assessment.f13_override,
        "risk_id": assessment.risk_id,
    }
    return allowed, receipt


# ── Post-Execution: Incident Classification ─────────────────────────


def classify_output(
    tool_name: str, output_text: str, session_id: str | None = None, actor_id: str | None = None
) -> dict[str, Any]:
    """
    Post-execution: classify tool output for incidents.
    Called AFTER the tool executes successfully.

    Returns: incident receipt
    """
    global _incidents_classified
    if not _bridge_enabled:
        return {"verdict": "BRIDGE_DISABLED"}

    incident = classify_incident(
        tool_name=tool_name,
        output_text=output_text,
        session_id=session_id,
        actor_id=actor_id,
    )
    _incidents_classified += 1

    # If incident detected, record as shadow candidate
    if incident.classification != IncidentClass.CLEAN:
        record_shadow_candidate(
            pattern_name=f"{incident.classification.value}:{tool_name}",
            description=incident.description,
            tool_name=tool_name,
            session_id=session_id,
            c_dark=incident.c_dark,
        )

    return {
        "incident_id": incident.incident_id,
        "classification": incident.classification.value,
        "c_dark": incident.c_dark,
        "severity": incident.severity,
        "f_floors_triggered": incident.f_floors_triggered,
        "recommended_action": incident.recommended_action,
        "description": incident.description,
    }


# ── Bridge telemetry ────────────────────────────────────────────────


def bridge_telemetry() -> dict[str, Any]:
    """Return bridge telemetry for dashboards."""
    return {
        "bridge": "reality_engineering",
        "enabled": _bridge_enabled,
        "modules": [
            "session_enforcer",
            "envelope_validator",
            "incident_harness",
            "cooling_harness",
            "risk_ledger",
            "rsi_patch_harness",
        ],
        "gates": {
            "sessions": _sessions_gated,
            "envelopes": _envelopes_gated,
            "risks": _risks_gated,
        },
        "post_execution": {
            "incidents_classified": _incidents_classified,
        },
    }


__all__ = [
    "session_gate",
    "envelope_gate",
    "risk_gate",
    "classify_output",
    "bridge_telemetry",
    "enable_bridge",
    "disable_bridge",
    "bridge_enabled",
]
