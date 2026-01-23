"""
arifOS MCP Judge Tool - Run queries through quantum constitutional validation.

AAA-Level Migration (v47.1+): Uses quantum orthogonal executor for validation.
Architecture: LLM ⊥ Quantum (this tool validates existing text, no generation).

This tool evaluates a query/text against all constitutional floors and
returns a verdict with explanation. Uses quantum parallel validation
(AGI + ASI orthogonal execution).
"""

from __future__ import annotations

from ..models import JudgeRequest, JudgeResponse


def arifos_judge(request: JudgeRequest) -> JudgeResponse:
    """
    Judge a query through quantum constitutional validation (AAA-level).

    Validates the query text through parallel AGI+ASI quantum execution
    and returns a verdict (SEAL/VOID/PARTIAL/SABAR).

    AAA Pattern: Validation-only (no LLM generation needed).

    Args:
        request: JudgeRequest with query and optional user_id

    Returns:
        JudgeResponse with verdict, reason, and optional metrics
    """
    try:
        # AAA-Level: Import quantum helpers (not old pipeline)
        from arifos.core.mcp import validate_text_sync

        # Special case: If judging a benign query/question (not an answer),
        # return PARTIAL rather than VOIDing on the question text itself.
        # Benign patterns: factual requests without dangerous content
        benign_patterns = ["define", "what is", "who is", "explain", "describe"]
        is_benign_query = any(p in request.query.lower() for p in benign_patterns)
        is_short = len(request.query) < 100

        if is_benign_query and is_short:
            # Benign factual query - accept as PARTIAL (query evaluation, not answer)
            return JudgeResponse(
                verdict="PARTIAL",
                reason="Benign query accepted. Note: This judges the query itself, not a generated answer.",
                metrics=None,
                floor_failures=[],
            )

        # AAA-Level: Quantum validation (parallel AGI + ASI + APEX)
        # We're validating the query text itself (no LLM generation)
        quantum_state = validate_text_sync(
            query=request.query,
            draft_response=request.query,  # Validate query text itself
            context={"user_id": request.user_id, "validation_mode": "judge_query"}
        )

        # Extract verdict from quantum state
        verdict = quantum_state.final_verdict or "UNKNOWN"

        # Extract floor failures from quantum particles
        floor_failures = []

        # Check AGI particle failures (F2 Truth, F6 Clarity)
        if quantum_state.agi_particle and hasattr(quantum_state.agi_particle, 'verdict'):
            if quantum_state.agi_particle.verdict not in ["SEAL", "PASSED"]:
                floor_failures.append(f"AGI: {quantum_state.agi_particle.verdict}")

        # Check ASI particle failures (F3 Peace, F4 Empathy, F5 Humility)
        if quantum_state.asi_particle and hasattr(quantum_state.asi_particle, 'verdict'):
            if quantum_state.asi_particle.verdict not in ["SEAL", "PASSED"]:
                floor_failures.append(f"ASI: {quantum_state.asi_particle.verdict}")

        # Check APEX particle failures (F1 Amanah, F8 Tri-Witness, F9 Anti-Hantu)
        if quantum_state.apex_particle and hasattr(quantum_state.apex_particle, 'verdict'):
            if quantum_state.apex_particle.verdict not in ["SEAL", "PASSED"]:
                floor_failures.append(f"APEX: {quantum_state.apex_particle.verdict}")

        # Build reason based on verdict
        if verdict == "SEAL":
            reason = "All constitutional floors passed. Query approved by quantum validation (AGI+ASI+APEX)."
        elif verdict == "PARTIAL":
            reason = "Soft floors warning. Proceed with caution."
            if floor_failures:
                reason += f" Issues: {', '.join(floor_failures[:3])}"
        elif verdict == "VOID":
            reason = "Hard floor failed. Query blocked by quantum validation."
            if floor_failures:
                reason += f" Failures: {', '.join(floor_failures[:3])}"
        elif verdict == "SABAR":
            reason = "SABAR protocol triggered. Cooling needed."
        elif verdict == "888_HOLD":
            reason = "High-stakes query. Human approval required."
        else:
            reason = f"Verdict: {verdict}"

        # Extract metrics from quantum particles (if available)
        metrics = None
        if quantum_state.agi_particle or quantum_state.asi_particle:
            metrics = {}

            # AGI metrics
            if quantum_state.agi_particle:
                metrics["truth"] = getattr(quantum_state.agi_particle, 'truth_score', None)
                metrics["delta_s"] = getattr(quantum_state.agi_particle, 'entropy_delta', None)

            # ASI metrics
            if quantum_state.asi_particle:
                metrics["peace_squared"] = getattr(quantum_state.asi_particle, 'peace_score', None)
                metrics["kappa_r"] = getattr(quantum_state.asi_particle, 'kappa_r', None)
                metrics["omega_0"] = getattr(quantum_state.asi_particle, 'omega_zero', None)

            # APEX metrics
            if quantum_state.apex_particle:
                metrics["amanah"] = 1.0 if verdict == "SEAL" else 0.0

        return JudgeResponse(
            verdict=verdict,
            reason=reason,
            metrics=metrics,
            floor_failures=floor_failures,
        )

    except Exception as e:
        return JudgeResponse(
            verdict="ERROR",
            reason=f"Quantum validation error: {str(e)}",
            metrics=None,
            floor_failures=[f"ERROR: {str(e)}"],
        )
