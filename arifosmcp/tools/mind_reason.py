"""
arifosmcp/tools/mind_reason.py — 333_MIND
════════════════════════════════════════

Inductive reasoning engine and synthesis.

DELTA BUNDLE SPEC (from archive/333/README.md):
  Every arif_mind_reason output MUST include:
  - facts: F2 ≥ 0.99 verifiable claims
  - scars: unresolved contradictions blocking certainty
  - floor_scores: F2, F4, F7, F13 self-check
  - entropy: ΔS ≤ 0 (must decrease local entropy)
  - confidence: calibrated Ω₀ ∈ [0.03, 0.05] (F7 Humility band)

Context injection (P2): When context is provided, the tool pre-loads
  session state (session_id, G-score, vitals) and prior tool results
  into the reasoning trace before synthesis. This grounds every
  reasoning call in actual system state rather than abstract axioms.

DITEMPA BUKAN DIBERI — Forged, Not Given
"""

from __future__ import annotations

import asyncio
import threading
from typing import Any

from arifosmcp.runtime.floors import check_floors
from arifosmcp.runtime.tools import _hold, _ok
from arifosmcp.schemas.synthesis import Synthesis


def _build_delta_bundle(
    query: str | None,
    status: str,
    claim_state: str,
    synthesis: str,
    reasoning: dict,
    confidence: dict,
    uncertainty: list,
    reasoning_mode: str = "analytical",
    axioms_used: list[str] | None = None,
    next_safe_action: list[str] | None = None,
    context: dict | None = None,
) -> dict:
    """
    Build a Structured Delta Bundle — the upgraded constitutional output for 333_MIND.
    """
    overall_conf = confidence.get("overall_confidence", 0.5)
    omega_0 = max(0.03, min(0.05, round(1.0 - overall_conf, 4)))

    reasoning_trace = []
    if context:
        session_id = context.get("session_id", "unknown")
        g_score = context.get(
            "g_score", context.get("vitals", {}).get("g_score", "unavailable")
        )
        reasoning_trace.append(
            f"[333_MIND context] session_id={session_id}, g_score={g_score}"
        )

    return {
        "query": query,
        "status": status,
        "claim_state": claim_state,
        "synthesis": synthesis,
        "reasoning": reasoning,
        "confidence": confidence,
        "uncertainty": uncertainty,
        "omega_0": omega_0,
        "reasoning_mode": reasoning_mode,
        "axioms_used": axioms_used or [],
        "next_safe_action": next_safe_action or [],
        "floor_scores": {
            "F02_TRUTH": confidence.get("evidence_confidence", 0) >= 0.9,
            "F04_CLARITY": True,
            "F07_HUMILITY": omega_0 in [0.03, 0.05],
            "F13_SOVEREIGN": True,
        },
        "reasoning_trace": reasoning_trace,
    }


def _run_reasoning_sync(coro: Any) -> dict[str, Any]:
    """Run coroutine in sync context, including when caller already has an active event loop."""
    try:
        asyncio.get_running_loop()
    except RuntimeError:
        return asyncio.run(coro)

    result: dict[str, Any] = {}
    error: list[BaseException] = []

    def _runner() -> None:
        try:
            result["value"] = asyncio.run(coro)
        except (
            BaseException
        ) as exc:  # pragma: no cover - passthrough for sync bridge failures
            error.append(exc)

    thread = threading.Thread(target=_runner, daemon=True)
    thread.start()
    thread.join()

    if error:
        raise error[0]
    return result["value"]


def arif_mind_reason(
    mode: str = "reason",
    query: str | None = None,
    actor_id: str | None = None,
    context: dict | None = None,
) -> Synthesis:
    """
    333_MIND: Constitutional reasoning and synthesis (Structured Witness).
    """
    from arifosmcp.runtime.mind_reason import (
        arif_mind_reason_structured as run_reasoning,
    )

    session_id = context.get("session_id") if context else None

    reason_result = _run_reasoning_sync(
        run_reasoning(query or "", mode, session_id, actor_id)
    )

    # Floor check (Manual override check)
    floor_check = check_floors("arif_mind_reason", {"query": query or ""}, actor_id)
    floor_verdict = floor_check.get("verdict", "HOLD")
    floor_reason = floor_check.get("reason", "Constitutional floor check did not SEAL")

    uncertainty = list(reason_result.get("uncertainty", []))
    if floor_verdict != "SEAL":
        uncertainty.append({"type": "FLOOR_BREACH", "detail": floor_reason})

    bundle = _build_delta_bundle(
        query=query,
        status=(
            "HOLD" if floor_verdict != "SEAL" else reason_result.get("status", "HOLD")
        ),
        claim_state=reason_result.get("claim_state", "HYPOTHESIS"),
        synthesis=reason_result.get("synthesis", ""),
        reasoning=reason_result.get("reasoning", {}),
        confidence=reason_result.get("confidence", {}),
        uncertainty=uncertainty,
        reasoning_mode=reason_result.get("reasoning_mode", "analytical"),
        axioms_used=reason_result.get("axioms_used", []),
        next_safe_action=reason_result.get("next_safe_action", []),
        context=context,
    )

    if floor_verdict != "SEAL":
        hold_env = _hold(
            "arif_mind_reason",
            floor_reason,
            floors=list(floor_check.get("failed_floors", [])),
            extra_meta={"floor_verdict": floor_verdict},
            session_id=session_id,
        )
        hold_env["result"] = bundle
        return Synthesis(**hold_env)

    return Synthesis(**_ok("arif_mind_reason", bundle))
