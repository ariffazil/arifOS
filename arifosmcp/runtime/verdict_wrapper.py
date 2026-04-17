"""
arifosmcp/runtime/verdict_wrapper.py — Constitutional Verdict Forging

Utility to wrap tool results into the arifOS Verdict Envelope v1.0.
Ensures metrics (dS, Confidence) correctly map to canonical status codes.

DITEMPA BUKAN DIBERI — Forged, Not Given
"""

from __future__ import annotations

import time
from typing import Any

from arifosmcp.contracts.artifacts import Artifact
from arifosmcp.contracts.envelopes import ResponseEnvelope
from arifosmcp.contracts.verdicts import (
    ArtifactStatus,
    ContinuationStatus,
    ExecutionStatus,
    GovernanceStatus,
)
from arifosmcp.runtime.models import (
    CanonicalMetrics,
    PhilosophyState,
    RuntimeEnvelope,
    RuntimeStatus,
    VerdictCode,
)


def forge_verdict(
    tool_id: str,
    stage: str,
    payload: dict[str, Any],
    session_id: str | None = None,
    metrics: CanonicalMetrics | None = None,
    floors_checked: list[str] | None = None,
    override_code: VerdictCode | None = None,
    message: str | None = None,
    canonical_tool_name: str | None = None,
    philosophy: PhilosophyState | None = None
) -> RuntimeEnvelope:
    """
    Forge a standardized verdict envelope (v2.0) from raw tool output.
    Unified across STDIO, HTTPS, and SSE.
    """
    
    # ... existing metrics/logic ...
    metrics = metrics or CanonicalMetrics()
    ds = metrics.telemetry.ds
    conf = metrics.telemetry.confidence
    
    if philosophy:
        conf = min(conf, philosophy.confidence_cap)
        metrics.telemetry.confidence = conf
    
    # Determine Code & Reason
    if override_code:
        code = override_code
        reason = "JUDGE_OVERRIDE"
    elif ds > 0.1:
        code = VerdictCode.VOID
        reason = "ENTROPY_HIGH"
        message = message or f"F4 Violation: Entropy spike detected (dS={ds})."
    else:
        threshold = 0.7 
        if philosophy and philosophy.posture == "VOID":
            code = VerdictCode.VOID
            reason = "PHILOSOPHY_VOID"
        elif philosophy and philosophy.posture == "HOLD":
            code = VerdictCode.SABAR
            reason = "PHILOSOPHY_HOLD"
        elif conf < threshold:
            code = VerdictCode.SABAR
            reason = "LOW_CONFIDENCE"
        elif not payload or (isinstance(payload, dict) and not payload.get("data") and not payload):
            code = VerdictCode.PARTIAL
            reason = "DATA_INCOMPLETE"
        else:
            code = VerdictCode.SEAL
            reason = "OK_ALL_PASS"

    # 4. Determine status fields (Unified V2)
    exec_status = ExecutionStatus.SUCCESS if code != VerdictCode.VOID else ExecutionStatus.ERROR
    # Map VerdictCode to GovernanceStatus
    gov_status_map = {
        VerdictCode.SEAL: GovernanceStatus.APPROVED,
        VerdictCode.SABAR: GovernanceStatus.PAUSE,
        VerdictCode.PARTIAL: GovernanceStatus.PARTIAL,
        VerdictCode.VOID: GovernanceStatus.VOID
    }
    gov_status = gov_status_map.get(code, GovernanceStatus.PAUSE)
    
    # Continuation logic
    cont_allowed = (code == VerdictCode.SEAL)
    
    # Artifact state logic
    if stage == "999_VAULT":
        art_status = ArtifactStatus.SEALED if code == VerdictCode.SEAL else ArtifactStatus.REJECTED
    elif stage == "777_FORGE":
        art_status = ArtifactStatus.STAGED if code == VerdictCode.SEAL else ArtifactStatus.REJECTED
    else:
        art_status = ArtifactStatus.USABLE

    # 5. Build the V2.0.0 Unified Envelope
    # This matches the ResponseEnvelope contract used by all transports
    res_env = ResponseEnvelope(
        tool_name=canonical_tool_name or tool_id,
        execution_status=exec_status,
        governance_status=gov_status,
        artifact_status=art_status,
        continue_allowed=cont_allowed,
        primary_artifact=Artifact(
            type="reasoning" if stage == "333_MIND" else "generic",
            status=art_status,
            payload=payload,
            creator_id="arif", # Default to arif for now per CF-01
            session_id=session_id or "global",
            timestamp=time.time()
        ),
        diagnostics={
            "metrics": metrics.model_dump() if hasattr(metrics, "model_dump") else {},
            "floors_checked": floors_checked or ["F4", "F11"],
            "reason": reason,
            "message": message
        },
        timestamp=time.time()
    )

    # 6. Wrap in RuntimeEnvelope for FastMCP compatibility
    return RuntimeEnvelope(
        ok=(code in (VerdictCode.SEAL, VerdictCode.PARTIAL)),
        tool=tool_id,
        canonical_tool_name=canonical_tool_name or tool_id,
        stage=stage,
        session_id=session_id,
        verdict=code,
        
        # V2 Unified Data
        execution_status=exec_status,
        governance_status=gov_status,
        continuation_status=ContinuationStatus.READY if cont_allowed else ContinuationStatus.HOLD,
        artifact_state=art_status,
        
        payload=res_env.model_dump(),
        status=RuntimeStatus.SUCCESS if code != VerdictCode.VOID else RuntimeStatus.ERROR
    )
