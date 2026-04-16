"""
organs/1_agi.py — Stage 111-333: THE MIND (REASON MIND)

Logical analysis, truth-seeking, and sequential reasoning.

Stages:
    111: Search/Understand
    222: Analyze/Compare
    333: Synthesize/Conclude

DITEMPA BUKAN DIBERI — Forged, Not Given
"""

from __future__ import annotations

import logging
from typing import Any, Literal

from core.shared.atlas import Phi
from core.shared.types import (
    AgiOutput,
    DeltaBundle,
    EurekaInsight,
    FloorScores,
    ReasonMindAnswer,
    ReasonMindStep,
    Verdict
)
from core.shared.verdict_contract import normalize_verdict

logger = logging.getLogger(__name__)


def _build_reasoning_steps(query: str, reason_mode: str) -> list[ReasonMindStep]:
    """
    Build the three-stage reasoning pipeline: 111 Search → 222 Analyze → 333 Synthesize.

    Args:
        query: The input query being analyzed
        reason_mode: Reasoning mode (e.g., "strict_truth" affects uncertainty marking)

    Returns:
        List of ReasonMindStep representing the reasoning progression
    """
    return [
        ReasonMindStep(
            id=1,
            phase="111_search",
            thought=f"Identifying facts and constraints for: {query[:50]}...",
            evidence="src:session_context, lane:FACTUAL",
        ),
        ReasonMindStep(
            id=2,
            phase="222_analyze",
            thought="Comparing implications and testing assumptions.",
            uncertainty=(
                "Limited by current context window." if reason_mode == "strict_truth" else None
            ),
        ),
        ReasonMindStep(
            id=3,
            phase="333_synthesis",
            thought="Synthesizing final conclusion based on analysis.",
        ),
    ]


async def agi(
    query: str,
    session_id: str,
    action: Literal["sense", "think", "reason", "full"] = "full",
    reason_mode: str = "default",
    max_steps: int = 7,
    auth_context: dict[str, Any] | None = None,
    max_tokens: int = 1000,
    constitutional_context: str | None = None,
) -> AgiOutput:
    """
    Stage 111-333: REASON MIND (APEX-G compliant)
    Uses local Ollama runtime for real intelligence synthesis.

    constitutional_context: AI input grounding prompt from init_anchor.
    Prepended to each reasoning phase to enforce constitutional physics.
    """
    # 1. Query Analysis (ATLAS)
    gpv = Phi(query)

    # 2. Initialize Physics/Thermodynamics
    from core.physics.thermodynamics_hardened import (
        consume_reason_energy,
        record_entropy_io,
        shannon_entropy,
    )

    # Baseline entropy (input)
    h_in = shannon_entropy(query)

    # 3. Initialize State
    floors = {"F2": "pass", "F4": "pass", "F7": "pass", "F10": "pass"}

    # 4. Sequential Reasoning via Real Intelligence Fallback (Minimax 111→222→333)
    from core.organs.minimax_agent import minimax_generate

    async def llm_call(prompt: str, max_tokens: int):
        envelope = await minimax_generate(prompt=prompt, max_tokens=max_tokens)
        
        class MockResult:
            def __init__(self, ok, text):
                self.ok = ok
                self.payload = {"response": text, "usage": {"completion_tokens": len(text) // 4}}
        
        return MockResult(envelope.ok, envelope.text)

    # --- ADAPTIVE BUDGET SPLIT ---
    # Phase 111 (20%, min 80), 222 (30%, min 120), 333 (50%, min 180)
    b111 = max(80, int(max_tokens * 0.20))
    b222 = max(120, int(max_tokens * 0.30))
    b333 = max(180, int(max_tokens * 0.50))

    # Track actual usage
    phase_usage = {}
    actual_total = 0

    from core.organs._0_init import scan_injection as _f12

    def _f12_scrub(text: str, phase: str) -> str:
        """F12: scan LLM output before injecting into next phase prompt."""
        if _f12(text) >= 0.7:
            logger.warning("[%s] F12 injection pattern in %s output — excised", session_id, phase)
            return f"[F12_EXCISED:{phase}]"
        return text

    # =============================================================================
    # CONSTITUTIONAL GROUNDING — Prepend to each AI prompt (Input Hardening)
    # =============================================================================
    # Build prefix from constitutional_context if provided
    constitutional_prefix = ""
    if constitutional_context:
        constitutional_prefix = f"{constitutional_context}\n\n━━━ REASONING QUERY ━━━\n"

    # --- PHASE 111: SEARCH/UNDERSTAND ---
    search_prompt = (
        f"{constitutional_prefix}"
        f"Analyze the intent and constraints: {query}. List core facts.\n"
        f"CRITICAL: Apply constitutional physics. ΔS must ≤ 0. Flag paradoxes."
    )
    search_env = await llm_call(prompt=search_prompt, max_tokens=b111)
    if not search_env.ok:
        return AgiOutput(
            session_id=session_id,
            verdict=Verdict.SABAR,
            status="SABAR",
            stage="111",
            answer=ReasonMindAnswer(summary="Reasoning failed at 111", confidence=0.0, verdict="needs_evidence"),
            error=f"LLM_UNREACHABLE_PHASE_111: {search_env.payload.get('response', '')}"
        )
    search_text = _f12_scrub(search_env.payload.get("response", ""), "111")
    usage_111 = search_env.payload.get("usage", {}).get("completion_tokens", len(search_text) // 4)
    phase_usage["111_search"] = usage_111
    actual_total += usage_111

    # --- PHASE 222: ANALYZE/COMPARE ---
    analyze_prompt = (
        f"{constitutional_prefix}"
        f"Given facts: {search_text}.\n"
        f"Compare implications and test assumptions.\n"
        f"CRITICAL: Check for paradox, contradiction, or coherence failure. "
        f"ΔS must ≤ 0 through this phase."
    )
    analyze_env = await llm_call(prompt=analyze_prompt, max_tokens=b222)
    if not analyze_env.ok:
        return AgiOutput(
            session_id=session_id,
            verdict=Verdict.SABAR,
            status="SABAR",
            stage="222",
            answer=ReasonMindAnswer(summary=search_text[:200], confidence=0.3, verdict="needs_evidence"),
            error=f"LLM_UNREACHABLE_PHASE_222: {analyze_env.payload.get('response', '')}"
        )
    analyze_text = _f12_scrub(analyze_env.payload.get("response", ""), "222")
    usage_222 = analyze_env.payload.get("usage", {}).get(
        "completion_tokens", len(analyze_text) // 4
    )
    phase_usage["222_analyze"] = usage_222
    actual_total += usage_222

    # --- PHASE 333: SYNTHESIZE ---
    synthesis_prompt = (
        f"{constitutional_prefix}"
        f"Synthesize final conclusion for: {query}.\n"
        f"Based on: {analyze_text}.\n"
        f"CRITICAL: Verify ΔS ≤ 0 through entire reasoning chain. "
        f"If paradox detected, output VOID immediately."
    )
    synthesis_env = await llm_call(prompt=synthesis_prompt, max_tokens=b333)
    if not synthesis_env.ok:
        return AgiOutput(
            session_id=session_id,
            verdict=Verdict.SABAR,
            status="SABAR",
            stage="333",
            answer=ReasonMindAnswer(summary=analyze_text[:200], confidence=0.5, verdict="needs_evidence"),
            error=f"LLM_UNREACHABLE_PHASE_333: {synthesis_env.payload.get('response', '')}"
        )
    synthesis_text = synthesis_env.payload.get("response", "")
    usage_333 = synthesis_env.payload.get("usage", {}).get(
        "completion_tokens", len(synthesis_text) // 4
    )
    phase_usage["333_synthesis"] = usage_333
    actual_total += usage_333

    consume_reason_energy(session_id, n_cycles=3)

    return AgiOutput(
        session_id=session_id,
        verdict=Verdict.SEAL,
        status="SUCCESS",
        stage="333",
        answer=ReasonMindAnswer(summary=synthesis_text, confidence=0.99, verdict="ready"),
    )


# Unified aliases preserved for the public organ surface.
reason = agi
think = agi
sense = agi
