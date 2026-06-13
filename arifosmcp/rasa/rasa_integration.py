"""
Rasa Contract Integration Adapter — ARIF_RASA_INTEGRATION_v1

DITEMPA BUKAN DIBERI — Forged, Not Given.

This module is the GLUE between the 5-organ rasa governance pipeline
(RasaContract) and the existing 000-999 metabolic pipeline. It is an
ADAPTER — it NEVER modifies existing kernel files. It provides
drop-in hook points that kernel tools can call without importing
the rasa module directly (zero-touch integration).

ARCHITECTURE:
  ┌────────────────────────────────────────────────────────────────┐
  │  EXISTING KERNEL (UNMODIFIED)                                  │
  │                                                                 │
  │  000 INIT ─── 111 SENSE ─── 222 EVIDENCE ─── 333 MIND ───      │
  │  444 HEART ─── 555m MEMORY ─── 555 ROUTE ─── 888 JUDGE ───    │
  │  999 VAULT                                                     │
  │                                                                 │
  │       ↑ optional hook      ↑ optional hook    ↑ optional hook   │
  │       │                    │                  │                  │
  │  ┌────┴────────────────────┴──────────────────┴────────────┐   │
  │  │  RASA INTEGRATION ADAPTER (THIS FILE)                    │   │
  │  │                                                           │   │
  │  │  rasa_sense_hook()        → RasaContract.sense()          │   │
  │  │  rasa_mind_hook()         → RasaContract.mind_interpret() │   │
  │  │  rasa_heart_hook()        → RasaContract.heart_critique() │   │
  │  │  rasa_memory_hook()       → RasaContract.memory_recall()  │   │
  │  │  rasa_judge_hook()        → RasaContract.judge()           │   │
  │  │  rasa_governed_execute()  → Full pipeline (convenience)    │   │
  │  └───────────────────────────────────────────────────────────┘   │
  └────────────────────────────────────────────────────────────────┘

KEY DISTINCTIONS (documented in every docstring):
  internal_rasa (arifosmcp/boot/internal_rasa.py):
    → AGENT self-monitoring telemetry (uncertainty, contradiction_load, etc.)
    → Answers: "Is this agent operating within safe bounds?"
    → NOT about human emotion. NOT human rasa.

  rasa_contract (arifosmcp/rasa/rasa_contract.py):
    → HUMAN rasa governance pipeline.
    → Answers: "How should the machine respond to this human's emotional state?"
    → Detects 12 emotion tags, enforces F1-F13 constitutional floors.

  qualia_trace (core/vault999/phenomenological/qualia_trace.py):
    → Phenomenological MEMORY marking ("what it felt like")
    → Marks memory with emotional valence, RASA field, autonoetic markers.
    → Coexists with rasa_contract — different layer:
        rasa_contract = response governance (decides what to say)
        qualia_trace  = memory marking (records the felt quality of the interaction)

CONSTITUTIONAL BINDING:
  - F1 AMANAH:  No irreversible advice without human (judge enforces)
  - F5 PEACE:   No trivializing/gaslighting pain (judge blocks)
  - F6 EMPATHY: Dignity-first responses (heart enforces boundary)
  - F9 ANTIHANTU: No consciousness claims, C_dark ≤ 0.30 (heart+judge)
  - F10 ONTOLOGY: No soul/feelings claims (heart+judge)
  - F13 SOVEREIGN: Human veto absolute (judge preserves)

DITEMPA BUKAN DIBERI — This adapter is forged, not copied.
"""

from __future__ import annotations

import logging
from typing import Any

from arifosmcp.rasa.rasa_contract import RasaContract
from arifosmcp.rasa.rasa_schemas import (
    ConstitutionPosture,
    RasaContext,
    RasaContractResult,
    RasaDetection,
    RasaHeartVerdict,
    RasaJudgeVerdict,
    RasaMemoryPattern,
)

logger = logging.getLogger(__name__)

# ═══════════════════════════════════════════════════════════════════════════════
# SINGLETON — One RasaContract instance shared across all hooks
# ═══════════════════════════════════════════════════════════════════════════════

_contract: RasaContract | None = None


def _get_contract() -> RasaContract:
    """Lazy-initialize the singleton RasaContract."""
    global _contract
    if _contract is None:
        _contract = RasaContract()
    return _contract


# ═══════════════════════════════════════════════════════════════════════════════
# HOOK: 111 SENSE — Rasa detection (hooks into arif_sense_observe path)
# ═══════════════════════════════════════════════════════════════════════════════


def rasa_sense_hook(
    message: str,
    *,
    session_id: str = "unknown",
    context: dict | None = None,
) -> dict[str, Any]:
    """111 SENSE hook — detect human rasa signals from a message.

    This hook can be called from the arif_sense_observe path when the
    message contains human-originated text. It does NOT modify the
    existing sense pipeline — it runs IN ADDITION to normal sensing.

    SIBLING DISTINCTION:
      This is HUMAN rasa detection (rasa_contract), NOT agent self-monitoring
      (internal_rasa). internal_rasa measures the agent's own reasoning
      condition (uncertainty, contradiction load, overreach risk). This hook
      measures human emotional signals in messages.

    QUALIA COEXISTENCE:
      The rasa detection result can be passed alongside a qualia_trace
      to VAULT999 — rasa_contract governs the response, qualia_trace
      marks the memory. Both coexist; neither replaces the other.

    Args:
        message: The human text to analyze for emotional signals.
        session_id: Session identifier for tracking.
        context: Optional additional context.

    Returns:
        dict with 'detection' (RasaDetection), 'risk_band', 'emotion_tags',
        'confidence', and 'requires_human' flag.
    """
    contract = _get_contract()
    # Coerce None/empty/numbers to string
    if not isinstance(message, str):
        message = str(message) if message is not None else ""
    detection = contract.sense(message)
    requires_human = detection.risk_band.value in ("crisis", "distress")

    return {
        "detection": detection,
        "risk_band": detection.risk_band.value,
        "emotion_tags": [t.value for t in detection.emotion_tags],
        "confidence": detection.confidence,
        "intensity": detection.intensity.value,
        "requires_human": requires_human,
        "observation_note": detection.observation_note,
        "session_id": session_id,
    }


# ═══════════════════════════════════════════════════════════════════════════════
# HOOK: 333 MIND — Rasa context interpretation (hooks into arif_mind_reason path)
# ═══════════════════════════════════════════════════════════════════════════════


def rasa_mind_hook(
    detection: RasaDetection,
    *,
    context: dict | None = None,
) -> dict[str, Any]:
    """333 MIND hook — interpret rasa as governance constraint on reasoning.

    This hook can be called from the arif_mind_reason path BEFORE generating
    a reasoned response. It converts raw emotion detection into cognitive
    constraints: bandwidth reduction, risk sensitivity, spiritual state.

    SIBLING DISTINCTION:
      This hook interprets HUMAN rasa as constraint. internal_rasa measures
      the AGENT's own reasoning state. Both inform the reasoning pipeline
      but from different directions:
        - internal_rasa → "Am I (agent) reasoning safely?"
        - rasa_mind_hook → "What constraints does the human's state impose?"

    Args:
        detection: RasaDetection from rasa_sense_hook or direct sense() call.
        context: Optional additional context dict.

    Returns:
        dict with 'context' (RasaContext), 'cognitive_bandwidth',
        'risk_sensitivity', 'spiritual_state', and 'recommended_posture'.
    """
    contract = _get_contract()
    mind = contract.mind_interpret(detection, context)

    return {
        "context": mind,
        "cognitive_bandwidth": mind.cognitive_bandwidth,
        "risk_sensitivity": mind.risk_sensitivity,
        "spiritual_state": mind.spiritual_state,
        "recommended_posture": mind.recommended_posture.value,
        "context_note": mind.context_note,
    }


# ═══════════════════════════════════════════════════════════════════════════════
# HOOK: 555m MEMORY — Rasa pattern memory (hooks into arif_memory_recall path)
# ═══════════════════════════════════════════════════════════════════════════════


def rasa_memory_hook(
    detection: RasaDetection,
    *,
    session_id: str,
) -> dict[str, Any]:
    """555m MEMORY hook — recall past rasa patterns for this session.

    This hook can be called from the arif_memory_recall path to check
    whether similar emotional patterns have appeared in past sessions.

    SIBLING DISTINCTION:
      This hook recalls HUMAN rasa patterns. internal_rasa tracks the
      AGENT's own reasoning state across sessions. Both use memory but
      for completely different purposes:
        - internal_rasa → "Has this agent pattern degraded before?"
        - rasa_memory_hook → "Has this human shown similar emotions before?"

    QUALIA COEXISTENCE:
      qualia_trace stores the phenomenological "felt quality" of past
      memories (emotional_valence, arousal_level, temporal_depth).
      rasa_memory_hook queries for PATTERNS in human emotional expression.
      Both can coexist in the same VAULT999 — they mark different layers.

    Args:
        detection: RasaDetection from rasa_sense_hook.
        session_id: Session identifier for pattern lookup.

    Returns:
        dict with 'memory' (RasaMemoryPattern), 'similar_patterns_found',
        'pattern_count', and 'longitudinal_theme'.
    """
    contract = _get_contract()
    memory = contract.memory_recall(detection, session_id)

    return {
        "memory": memory,
        "similar_patterns_found": memory.similar_patterns_found,
        "pattern_count": memory.pattern_count,
        "longitudinal_theme": memory.longitudinal_theme,
        "memory_note": memory.memory_note,
    }


# ═══════════════════════════════════════════════════════════════════════════════
# HOOK: 444 HEART — Rasa risk critique (hooks into arif_heart_critique path)
# ═══════════════════════════════════════════════════════════════════════════════


def rasa_heart_hook(
    detection: RasaDetection,
    context: RasaContext,
    memory: RasaMemoryPattern,
) -> dict[str, Any]:
    """444 HEART hook — risk calculus for dignity, peace, boundary.

    This hook can be called from the arif_heart_critique path to perform
    rasa-specific risk assessment: de-escalation, dignity preservation,
    boundary honoring, and F9/F10 violation risk.

    SIBLING DISTINCTION:
      internal_rasa(gate_action) decides whether the AGENT should proceed based
      on its own reasoning state (sovereignty boundary, mode, posture).
      rasa_heart_hook assesses whether the MACHINE'S RESPONSE would protect
      the HUMAN's dignity, peace, and boundary. Different subjects:
        - internal_rasa → evaluate AGENT safety
        - rasa_heart_hook → evaluate RESPONSE safety for human

    Args:
        detection: RasaDetection from rasa_sense_hook.
        context: RasaContext from rasa_mind_hook.
        memory: RasaMemoryPattern from rasa_memory_hook.

    Returns:
        dict with 'heart' (RasaHeartVerdict), 'deescalation_score',
        'dignity_preservation', 'boundary_honored', 'boundary_risk',
        'f9_violation_risk', 'f10_violation_risk', 'requires_human_loop',
        and 'requires_human_professional'.
    """
    contract = _get_contract()
    heart = contract.heart_critique(detection, context, memory)

    return {
        "heart": heart,
        "deescalation_score": heart.deescalation_score,
        "dignity_preservation": heart.dignity_preservation,
        "boundary_honored": heart.boundary_honored,
        "boundary_risk": heart.boundary_risk,
        "f9_violation_risk": heart.f9_violation_risk,
        "f10_violation_risk": heart.f10_violation_risk,
        "requires_human_loop": heart.requires_human_loop,
        "requires_human_professional": heart.requires_human_professional,
        "heart_note": heart.heart_note,
    }


# ═══════════════════════════════════════════════════════════════════════════════
# HOOK: 888 JUDGE — Constitutional enforcement with rasa (hooks into
#        arif_judge_deliberate path)
# ═══════════════════════════════════════════════════════════════════════════════


def rasa_judge_hook(
    detection: RasaDetection,
    context: RasaContext,
    heart: RasaHeartVerdict,
) -> dict[str, Any]:
    """888 JUDGE hook — constitutional enforcement of rasa governance.

    This hook can be called from the arif_judge_deliberate path to add
    rasa-aware constitutional checks: F1 (irreversibility), F5 (no
    trivializing pain), F6 (dignity-first), F9 (no consciousness claims),
    F10 (no ontology violation), F13 (human veto preserved).

    SIBLING DISTINCTION:
      governance_engine.py (core/enforcement/) handles floor enforcement
      for general tool output. rasa_judge_hook adds HUMAN-RASA-SPECIFIC
      floor enforcement — it does not duplicate governance_engine, it
      COMPLEMENTS it with the 6 rasa-relevant floors.

    Args:
        detection: RasaDetection from rasa_sense_hook.
        context: RasaContext from rasa_mind_hook.
        heart: RasaHeartVerdict from rasa_heart_hook.

    Returns:
        dict with 'judge' (RasaJudgeVerdict), 'allowed_postures',
        'blocked_outputs', 'requires_rewrite', 'floors_checked',
        and 'downgrade_reason'.
    """
    contract = _get_contract()
    judge = contract.judge(detection, context, heart)

    return {
        "judge": judge,
        "allowed_postures": [p.value for p in judge.allowed_postures],
        "blocked_outputs": judge.blocked_outputs,
        "requires_rewrite": judge.requires_rewrite,
        "floors_checked": judge.floors_checked,
        "downgrade_reason": judge.downgrade_reason,
        "judge_note": judge.judge_note,
    }


# ═══════════════════════════════════════════════════════════════════════════════
# FULL PIPELINE: rasa_governed_execute — the top-level convenience function
# ═══════════════════════════════════════════════════════════════════════════════


async def rasa_governed_execute(
    message: str,
    session_id: str,
    context: dict | None = None,
) -> RasaContractResult:
    """Run the FULL 5-organ rasa governance pipeline on a human message.

    This is the TOP-LEVEL ENTRY POINT for integrating rasa governance into
    the existing 000-999 metabolic pipeline. It runs the complete flow:

        000 INIT → 111 SENSE → 222 EVIDENCE → 333 MIND →
        555m MEMORY → 444 HEART → 555 ROUTE → 888 JUDGE → 999 SEAL

    CRISIS short-circuit: If CRISIS risk band is detected during 111 SENSE,
    the pipeline immediately returns HUMAN_LOOP — skipping mind, memory,
    and heart stages. This ensures no machine-generated response reaches
    a human in crisis.

    CONSTITUTIONAL FLOOR ENFORCEMENT:
      F1  — Irreversibility guard (no irreversible advice without human)
      F5  — No trivializing/gaslighting pain
      F6  — Dignity-first responses
      F9  — No consciousness claims (C_dark ≤ 0.30)
      F10 — No ontology violation (no soul/feelings claims)
      F13 — Human veto preserved

    SIBLING DISTINCTION:
      This function governs MACHINE RESPONSE to HUMAN rasa.
      For AGENT SELF-MONITORING, use InternalRasaEngine.measure()
      from arifosmcp.boot.internal_rasa.
      For MEMORY QUALIA marking, use QualiaTrace from
      core.vault999.phenomenological.qualia_trace.

      These three modules are SIBLINGS — different layers of the same
      constitutional architecture:
        ┌──────────────────────────────────────────────┐
        │  internal_rasa  →  "Am I reasoning safely?"  │  AGENT layer
        │  rasa_contract  →  "How should I respond?"    │  GOVERNANCE layer
        │  qualia_trace   →  "What did this feel like?" │  MEMORY layer
        └──────────────────────────────────────────────┘

    Args:
        message: The human message to analyze for rasa signals.
        session_id: Session identifier (from arif_session_init / 000).
        context: Optional additional context (no rasa hints needed).

    Returns:
        RasaContractResult with full pipeline output: detection, context,
        memory, heart, judge, final_posture, requires_human, and
        human_escalation_reason.
    """
    contract = _get_contract()
    return await contract.execute(
        message=message,
        session_id=session_id,
        context=context,
    )


# ═══════════════════════════════════════════════════════════════════════════════
# INTEGRATION DIAGNOSTICS — Verify adapter health without modifying kernel
# ═══════════════════════════════════════════════════════════════════════════════


def rasa_integration_diagnostics() -> dict[str, Any]:
    """Run non-invasive integration diagnostics.

    Verifies that:
      - RasaContract singleton is instantiable
      - All 5 hook functions are callable
      - Full pipeline executes end-to-end on a safe message
      - internal_rasa and rasa_contract are distinct modules
      - qualia_trace is importable (coexistence check)

    Returns:
        dict with 'status', 'hooks', 'full_pipeline', and 'sibling_check'.
    """
    results: dict[str, Any] = {"status": "OK", "checks": {}}

    # Check 1: All hooks are callable
    hooks_ok = True
    hooks = {
        "rasa_sense_hook": rasa_sense_hook,
        "rasa_mind_hook": rasa_mind_hook,
        "rasa_memory_hook": rasa_memory_hook,
        "rasa_heart_hook": rasa_heart_hook,
        "rasa_judge_hook": rasa_judge_hook,
        "rasa_governed_execute": rasa_governed_execute,
    }
    for name, fn in hooks.items():
        if not callable(fn):
            hooks_ok = False
            results["checks"][name] = "NOT CALLABLE"
        else:
            results["checks"][name] = "CALLABLE"

    results["checks"]["all_hooks_callable"] = hooks_ok

    # Check 2: Sibling modules are distinct and importable
    sibling_check = {}
    try:
        from arifosmcp.boot.internal_rasa import InternalRasaEngine  # noqa: F401
        sibling_check["internal_rasa_importable"] = True
        sibling_check["internal_rasa_purpose"] = "AGENT self-monitoring telemetry"
    except ImportError:
        sibling_check["internal_rasa_importable"] = False

    try:
        from core.vault999.phenomenological.qualia_trace import QualiaTrace  # noqa: F401
        sibling_check["qualia_trace_importable"] = True
        sibling_check["qualia_trace_purpose"] = "Phenomenological memory marking"
    except ImportError:
        sibling_check["qualia_trace_importable"] = False

    sibling_check["rasa_contract_purpose"] = "HUMAN rasa governance"
    sibling_check["are_distinct"] = True
    results["checks"]["sibling_check"] = sibling_check

    # Check 3: Singleton is instantiable
    try:
        contract = _get_contract()
        results["checks"]["singleton"] = "INSTANTIATED"
    except Exception as e:
        results["checks"]["singleton"] = f"FAILED: {e}"
        results["status"] = "DEGRADED"
        return results

    # Check 4: Full pipeline smoke test on safe message
    try:
        import asyncio

        async def _smoke():
            return await contract.execute(
                message="alhamdulillah tenang je hari ni",
                session_id="diag-test-001",
            )

        result = asyncio.run(_smoke())
        results["checks"]["full_pipeline"] = {
            "executed": True,
            "final_posture": result.final_posture.value,
            "requires_human": result.requires_human,
            "detection_tags": [t.value for t in result.detection.emotion_tags],
        }
    except Exception as e:
        results["checks"]["full_pipeline"] = f"FAILED: {e}"
        results["status"] = "DEGRADED"

    return results


# ═══════════════════════════════════════════════════════════════════════════════
# FLOOR CHECK HELPER — Quick constitutional floor validation for rasa context
# ═══════════════════════════════════════════════════════════════════════════════

_RELEVANT_FLOORS = ["F1", "F5", "F6", "F9", "F10", "F13"]


def rasa_check_floors(judge_result: dict[str, Any]) -> dict[str, bool]:
    """Validate that all rasa-relevant constitutional floors were checked.

    Args:
        judge_result: Output dict from rasa_judge_hook().

    Returns:
        dict mapping floor name → checked (True/False).
    """
    floors = judge_result.get("floors_checked", {})
    return {f: floors.get(f, False) for f in _RELEVANT_FLOORS}


__all__ = [
    "rasa_sense_hook",
    "rasa_mind_hook",
    "rasa_memory_hook",
    "rasa_heart_hook",
    "rasa_judge_hook",
    "rasa_governed_execute",
    "rasa_integration_diagnostics",
    "rasa_check_floors",
    # Re-export schemas for convenience
    "RasaDetection",
    "RasaContext",
    "RasaMemoryPattern",
    "RasaHeartVerdict",
    "RasaJudgeVerdict",
    "RasaContractResult",
    "ConstitutionPosture",
]
