"""Constitutional tests — Explanatory-Class Gate (claim_kernel bridge).

Forged 2026-09-19. Covers the ONE wiring point:

    arifosmcp/runtime/v2_envelope.py::build_v2_envelope
        → _apply_mutation_justification_gate

Law under test (AAA/lib/claim_kernel):
    A NARRATIVE-class claim may be true, valuable and worth reading and still
    carry zero explanatory power. It may be PUBLISHED, but it may never be the
    SOLE JUSTIFICATION for a mutation. UNCLASSIFIED fails closed.

    CanMutate = AuthorityGranted AND ScopeMatches AND TargetPermitted
                AND BoundaryActive AND JustificationClassIn(ACTION_ELIGIBLE)

ADDITIVE invariants these tests pin (must not regress):
    * `_extract_can_mutate` semantics are frozen.
    * The gate is MONOTONE-DOWNWARD: it can deny, never grant.
    * F1-F13 verdict semantics are untouched (SEAL stays SEAL; only the
      mutation-authorisation flag is affected).

DITEMPA BUKAN DIBERI — Forged, Not Given.
"""

from __future__ import annotations

import inspect
from typing import Any

import pytest

from arifosmcp.core import claim_class_gate as ccg
from arifosmcp.core import epistemic_state as epi
from arifosmcp.runtime.v2_envelope import (
    _extract_can_mutate,
    build_v2_envelope,
)

# ── fixtures / helpers ──────────────────────────────────────────────────────

NARRATIVE_TEXT = "Melayu itu bangsa yang hebat dan terpilih"
MEASURED_TEXT = "Financing growth fell to 4.6% baseline: 2024 = 14.1%"


def _judge_response(
    verdict: str = "SEAL", authority: str = "FULL", **result_extra: Any
) -> dict[str, Any]:
    result: dict[str, Any] = {"verdict": verdict}
    result.update(result_extra)
    return {"session": {"authority": authority}, "result": result}


# ── 1. claim_kernel is actually reachable (the gate must not be a no-op) ────


def test_claim_kernel_is_reachable():
    status = ccg.kernel_status()
    assert status["kernel_available"] is True, status
    assert status["schema"] == "claim_kernel/v1"
    assert "MEASURED" in status["claim_classes"]
    assert "NARRATIVE" in status["claim_classes"]
    assert set(status["action_eligible_classes"]) == {"MEASURED", "MECHANISM", "PATTERN"}


# ── 2. vocabulary is imported, never redeclared ────────────────────────────


def test_vocabulary_is_not_redeclared():
    """The gate must not carry a second copy of the taxonomy."""
    src = inspect.getsource(ccg)
    assert "CLAIM_CLASSES = (" not in src, "gate re-declared the class vocabulary"
    assert "ACTION_ELIGIBLE_CLASSES = (" not in src, "gate re-declared eligibility"


# ── 3. fail-closed behaviour of the gate itself ────────────────────────────


def test_undeclared_class_fails_closed():
    verdict = ccg.evaluate(MEASURED_TEXT, None)
    assert verdict["allowed_for_mutation"] is False
    assert verdict["declared"] == "UNCLASSIFIED"
    assert verdict["reasons"], "a denial must state a reason"


def test_narrative_is_denied_by_name():
    verdict = ccg.evaluate(NARRATIVE_TEXT, "NARRATIVE")
    assert verdict["allowed_for_mutation"] is False
    assert any("NARRATIVE" in r for r in verdict["reasons"])


def test_measured_is_eligible():
    verdict = ccg.evaluate(MEASURED_TEXT, "MEASURED")
    assert verdict["allowed_for_mutation"] is True
    assert verdict["reasons"] == []


def test_mechanism_is_eligible():
    verdict = ccg.evaluate(
        "Literasi universal ditetapkan pada 70M; insentif berubah", "MECHANISM"
    )
    assert verdict["allowed_for_mutation"] is True


def test_class_mismatch_is_denied():
    """Declaring MECHANISM over a measurement is an overclaim the lint catches."""
    verdict = ccg.evaluate(MEASURED_TEXT, "MECHANISM")
    assert verdict["allowed_for_mutation"] is False


def test_unknown_class_is_coerced_and_denied():
    verdict = ccg.evaluate("something", "TOTALLY_MADE_UP")
    assert verdict["allowed_for_mutation"] is False


def test_gate_never_raises_on_junk():
    for junk in ("", None, "   ", "\x00\xff", "a" * 50000):
        verdict = ccg.evaluate(junk, "MECHANISM")
        assert isinstance(verdict, dict)
        assert "allowed_for_mutation" in verdict


def test_gate_fails_closed_when_kernel_unreachable(monkeypatch):
    """An unverifiable justification is not a verified one."""
    monkeypatch.setattr(ccg, "KERNEL_AVAILABLE", False)
    monkeypatch.setattr(ccg, "KERNEL_ERROR", "simulated import failure")
    monkeypatch.setattr(ccg, "_action_eligible", None)
    verdict = ccg.evaluate(MEASURED_TEXT, "MEASURED")
    assert verdict["allowed_for_mutation"] is False
    assert any("UNAVAILABLE" in r for r in verdict["reasons"])


# ── 4. the choke point: _extract_can_mutate semantics are FROZEN ───────────


def test_base_can_mutate_semantics_unchanged():
    assert _extract_can_mutate("PROCEED", "FULL") is True
    assert _extract_can_mutate("PROCEED", "LIMITED_MUTATE") is True
    assert _extract_can_mutate("PROCEED", "OBSERVE_ONLY") is False
    assert _extract_can_mutate("HOLD", "FULL") is False
    assert _extract_can_mutate("DENY", "FULL") is False
    assert _extract_can_mutate("VOID", "FULL") is False


# ── 5. envelope integration — the missing term in CanMutate ───────────────


def test_envelope_denies_mutation_without_claim_class():
    env = build_v2_envelope("arif_judge", _judge_response())
    assert env["can_mutate"] is False
    assert env["claim_class"] == "UNCLASSIFIED"
    assert env["mutation_justification"]["allowed"] is False
    assert env["mutation_justification"]["reasons"]


def test_envelope_denies_narrative_justification():
    env = build_v2_envelope(
        "arif_judge",
        _judge_response(claim_class="NARRATIVE", candidate=NARRATIVE_TEXT),
    )
    assert env["can_mutate"] is False
    assert env["claim_class"] == "NARRATIVE"
    assert env["mutation_justification"]["allowed"] is False


def test_envelope_allows_measured_justification():
    env = build_v2_envelope(
        "arif_judge",
        _judge_response(claim_class="MEASURED", candidate=MEASURED_TEXT),
    )
    assert env["can_mutate"] is True
    assert env["claim_class"] == "MEASURED"
    assert env["mutation_justification"]["allowed"] is True


def test_envelope_allows_mechanism_declared_in_evidence():
    """Declaration carried in evidence (arif_judge evidence path) is honoured."""
    env = build_v2_envelope(
        "arif_judge",
        _judge_response(
            claim_class="MECHANISM",
            evidence={"claim_class": "MECHANISM"},
            candidate="insentif berubah kerana pathway yang membawa hasil",
        ),
    )
    assert env["can_mutate"] is True
    assert env["claim_class"] == "MECHANISM"


def test_gate_is_monotone_downward_never_grants():
    """An eligible claim class must NOT manufacture authority."""
    env = build_v2_envelope(
        "arif_judge",
        _judge_response(
            authority="OBSERVE_ONLY", claim_class="MEASURED", candidate=MEASURED_TEXT
        ),
    )
    assert env["can_mutate"] is False

    env_hold = build_v2_envelope(
        "arif_judge",
        _judge_response(verdict="HOLD", claim_class="MEASURED", candidate=MEASURED_TEXT),
    )
    assert env_hold["can_mutate"] is False


def test_denial_survives_a_handler_preset_can_mutate_true():
    """A handler that pre-set can_mutate=True cannot bypass the gate."""
    response = _judge_response()
    response["can_mutate"] = True
    env = build_v2_envelope("arif_judge", response)
    assert env["can_mutate"] is False


def test_verdict_semantics_untouched_by_the_gate():
    """F1-F13: the gate never rewrites the verdict, only mutation authority."""
    env = build_v2_envelope(
        "arif_judge",
        _judge_response(claim_class="NARRATIVE", candidate=NARRATIVE_TEXT),
    )
    internal = env.get("verdict") or (env.get("result") or {}).get("verdict")
    assert internal == "SEAL"
    assert env["can_mutate"] is False


def test_pinned_meta_claim_text_wins_over_candidate():
    """One text, one answer.

    arif_judge pins the EXACT justification text it evaluated into
    meta.claim_text. The envelope must evaluate that same string, not
    re-derive one from a lower-priority field — otherwise the judge and the
    envelope can return two different answers for the same verdict.
    """
    response = {
        "session": {"authority": "FULL"},
        "meta": {"claim_class": "MEASURED", "claim_text": MEASURED_TEXT},
        # A different, non-eligible narrative string sits lower in the search order.
        "result": {"verdict": "SEAL", "candidate": NARRATIVE_TEXT},
    }
    env = build_v2_envelope("arif_judge", response)
    assert env["mutation_justification"]["text_source"] == "response.meta.claim_text"
    assert env["claim_class"] == "MEASURED"
    assert env["can_mutate"] is True


# ── 6. the axis lives INSIDE epistemic_state, beside reality_class ────────


def test_claim_class_lives_beside_reality_class():
    session_id = "constitutional-test-session-claim-axis"
    epi.set_epistemic_state(session_id, {epi.AXIS_REALITY_CLASS: "OBSERVED"})

    epi.record_claim_class(session_id, "MEASURED", claim_text=MEASURED_TEXT)

    # axis 2 set...
    assert epi.get_claim_class(session_id) == "MEASURED"
    # ...and axis 1 survived the merge (this is why it is one record, not two)
    assert epi.get_reality_class(session_id) == "OBSERVED"
    assert epi.snapshot_epistemic_axes(session_id)["claim_class"] == "MEASURED"


def test_epistemic_record_never_raises_on_bad_input():
    assert epi.record_claim_class(None, "MEASURED") is None
    assert epi.record_claim_class("", "MEASURED") is None
    assert epi.get_claim_class(None) is None
    assert epi.get_claim_class("no-such-session") is None


def test_envelope_reads_the_session_claim_axis():
    """Out-of-band declaration (session axis) is honoured by the envelope."""
    session_id = "constitutional-test-session-envelope-axis"
    epi.record_claim_class(session_id, "MEASURED", claim_text=MEASURED_TEXT)
    response = _judge_response(candidate=MEASURED_TEXT)
    response["session_id"] = session_id
    env = build_v2_envelope("arif_judge", response)
    assert env["claim_class"] == "MEASURED"
    assert env["can_mutate"] is True


# ── 7. the judge declares the axis (signature contract) ───────────────────


def test_arif_judge_accepts_claim_class_declaration():
    from arifosmcp.tools.judge import arif_judge

    params = inspect.signature(arif_judge).parameters
    assert "claim_class" in params, "arif_judge must accept a declared claim_class"
    assert "claim_text" in params
    assert params["claim_class"].default is None, "declaration must stay optional"


# ── 8. B2 — one receipt, one class (coherence under unknown vocabulary) ──────
# Defect pinned (e-a26871f2, observed 2026-09-20): the receipt echoed the raw
# caller input in `class` (OBSERVATION) while claim_kernel had silently coerced
# it to UNCLASSIFIED — so `class=OBSERVATION, agree=true` sat above reasons
# reading "class=UNCLASSIFIED is not action-eligible". Two truths, one receipt.


def test_receipt_class_never_contradicts_its_own_reasons():
    verdict = ccg.evaluate("observation only, no measure", "OBSERVATION")
    # audit truth preserved: what the caller actually declared stays visible
    assert verdict["declared"] == "OBSERVATION"
    # the kernel's class wins in the field reasons quote
    assert verdict["class"] == "UNCLASSIFIED"
    # the coercion is stated, not smoothed over
    assert any("OBSERVATION" in r for r in verdict["reasons"])
    # every reason of the form class=X must agree with the receipt's class
    for reason in verdict["reasons"]:
        if reason.startswith("class="):
            assert f"class={verdict['class']}" in reason, reason


def test_declared_and_class_agree_for_in_vocabulary_classes():
    for cls, text in (("MEASURED", MEASURED_TEXT), ("NARRATIVE", NARRATIVE_TEXT)):
        verdict = ccg.evaluate(text, cls)
        assert verdict["class"] == cls
        assert verdict["declared"] == cls


def test_deny_shape_always_carries_class():
    """The fail-closed path must publish the same field the judge quotes."""
    import inspect as _inspect

    src = _inspect.getsource(ccg._deny)
    assert '"class": declared' in src


if __name__ == "__main__":  # pragma: no cover
    raise SystemExit(pytest.main([__file__, "-v"]))
