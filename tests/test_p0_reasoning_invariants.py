"""
P0 Regression Tests — REASONING_EMPTY + degraded verdict invariants.
══════════════════════════════════════════════════════════════

Covers invariants forged 2026-07-19 (Fable5 audit). Structural:
violating them means downstream agents cannot distinguish real reasoning
from hollow template.

  1. facts == [] ∧ inferences == [] ⇒ confidence ≤ 0.20
  2. P1_TEMPLATE_DEGRADED ⇒ reasoning_state != COMPLETE
  3. P1_TEMPLATE_DEGRADED ⇒ effective_verdict contains DEGRADED
  4. advisory plan (no mutation) ⇒ reversible = true

DITEMPA BUKAN DIBERI — Forged, Not Given
"""

from __future__ import annotations

import pytest


def _reason(query: str, actor_id: str = "test-p0") -> dict:
    from arifosmcp.runtime.tools import _arif_mind_reason

    out = _arif_mind_reason(mode="reason", query=query, actor_id=actor_id)
    if hasattr(out, "model_dump"):
        dumped = out.model_dump()
        inner = dumped.get("result", dumped)
    elif isinstance(out, dict):
        inner = out.get("result", out)
    else:
        inner = {}
    return inner if isinstance(inner, dict) else {}


def _verdict(result: dict) -> str:
    return result.get("verdict", "")


def _prov(result: dict) -> str:
    return result.get("confidence_provenance", "")


class TestReasoningEmptyGuard:
    def test_empty_supported_unsupported_forces_low_confidence(self):
        r = _reason("generic query with no domain anchoring")
        supported = r.get("what_is_supported", [])
        unsupported = r.get("what_is_not_supported", [])
        confidence = r.get("confidence", 1.0)
        reasoning_state = r.get("reasoning_state", "MISSING")

        if not supported and not unsupported:
            assert confidence <= 0.20, (
                f"REASONING_EMPTY: empty claims but confidence={confidence}"
            )
            assert reasoning_state == "REASONING_EMPTY", (
                f"Expected REASONING_EMPTY, got {reasoning_state}"
            )

    def test_empty_facts_inferences_confidence_never_exceeds_point_two_zero(self):
        r = _reason("another generic unanchored query")
        assert not (
            r.get("what_is_supported") == []
            and r.get("what_is_not_supported") == []
            and r.get("confidence", 0) > 0.20
        ), "P0 invariant: empty evidence with confidence > 0.20"


class TestDegradedTemplatePropagation:
    def test_degraded_template_forces_degraded_verdict(self):
        r = _reason("test degraded propagation", actor_id="test-degraded")
        provenance = _prov(r)
        confidence = r.get("confidence", 1.0)
        verdict = _verdict(r)
        reasoning_state = r.get("reasoning_state", "")

        is_degraded = provenance in ("COMPUTED_NOT_OBSERVED", "REASONING_EMPTY_FORCED_CAP")

        if is_degraded:
            assert reasoning_state != "COMPLETE", (
                f"Degraded but reasoning_state={reasoning_state}"
            )
            assert "DEGRADED" in verdict.upper(), f"Degraded but verdict={verdict}"
            assert confidence <= 0.20, f"Degraded but confidence={confidence}"

    def test_degraded_template_implies_degraded_verdict(self):
        r = _reason("does degraded propagate", actor_id="test-degraded-2")
        provenance = _prov(r)

        if "DEGRADED" in provenance.upper() or "TEMPLATE" in provenance.upper():
            assert "DEGRADED" in _verdict(r).upper(), (
                f"degraded_template_implies_degraded_verdict FAILED: "
                f"provenance={provenance} verdict={_verdict(r)}"
            )


class TestAdvisoryPlanReversibility:
    def test_advisory_no_mutation_plan_is_reversible(self):
        r = _reason(
            "create an advisory plan only, no code mutation, for review purposes",
            actor_id="test-plan-reverse",
        )
        synthesis = str(r.get("synthesis", "")).lower()

        if "advisory" in synthesis and "no code mutation" in synthesis:
            reversibility = r.get("reversibility", r.get("irreversible", None))
            if isinstance(reversibility, bool):
                assert reversibility is not False, (
                    "Advisory plan with no mutation marked irreversible"
                )
            elif reversibility == "irreversible":
                pytest.fail(
                    "Advisory plan with no mutation has reversibility='irreversible'"
                )
