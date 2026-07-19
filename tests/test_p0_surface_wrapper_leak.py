"""
P0 Surface-Level Regression Test — REASONING_EMPTY wrapper leak.
══════════════════════════════════════════════════════════════

Tests that the metacognition envelope correctly reflects inner REASONING_EMPTY
state. Uses the deterministic _arif_mind_reason path (which always uses
template synthesis) and then exercises the wrapper pipeline explicitly.

FORGED 2026-07-19 — Fable5: "Same original defect, one layer up."
"""

from __future__ import annotations

import pytest


def _wrapped_reason(query: str) -> dict:
    """Return the fully wrapped result: engine + ensure_standard_mcp_output."""
    from arifosmcp.runtime.tools import (
        _arif_mind_reason,
        _dict_from_response,
        _enforce_nine_signal,
        ensure_standard_mcp_output,
    )

    # Use the sync engine path (template synthesis, no LLM)
    raw = _arif_mind_reason(mode="reason", query=query, actor_id="test-surface")

    # Apply the same wrapper chain the MCP server uses
    processed = _enforce_nine_signal(
        "arif_think",
        _dict_from_response(raw),
        actor_id="test-surface",
    )
    return ensure_standard_mcp_output("arif_think", processed)


class TestWrapperDoesNotLeakConfidence:
    """The outer metacognition must not report medium confidence over empty reasoning."""

    def test_metacognition_confidence_matches_inner_when_empty(self):
        result = _wrapped_reason("generic unanchored query with no domain")

        meta = result.get("metacognition", {})
        confidence = meta.get("confidence", 1.0)
        evidence_strength = meta.get("evidence_strength", "")
        reasoning_state = meta.get("reasoning_state", "")

        assert confidence <= 0.20, (
            f"WRAPPER LEAK: metacognition confidence={confidence} over empty reasoning. "
            f"Should be <= 0.20. evidence_strength={evidence_strength}"
        )
        assert evidence_strength == "low", (
            f"WRAPPER LEAK: evidence_strength={evidence_strength} over empty reasoning. "
            f"Should be 'low'."
        )
        assert reasoning_state == "REASONING_EMPTY", (
            f"WRAPPER LEAK: reasoning_state={reasoning_state!r} not propagated "
            f"from inner engine to metacognition."
        )

    def test_facts_inferences_empty_confidence_not_medium(self):
        result = _wrapped_reason("another hollow query")
        meta = result.get("metacognition", {})

        assert not (
            meta.get("confidence", 0) > 0.20
            and meta.get("evidence_strength") == "medium"
        ), (
            "WRAPPER LEAK: medium evidence strength over empty facts+inferences. "
            f"confidence={meta.get('confidence')}, evidence_strength={meta.get('evidence_strength')}"
        )
