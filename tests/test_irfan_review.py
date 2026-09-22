"""
tests/test_irfan_review.py — IRFAN · Advisory Stewardship Review tests
═════════════════════════════════════════════════════════════════════════════

Spec: ARIF::SALAM::IRFAN::INIT::v0.1 (F13-ratified INIT).

Covers:
  1. CLEAR case — all 14 inputs benign, least-power given, repair plan present.
  2. CONCERN cases — irreversible mutation with no repair plan; unknown
     authority basis (capability≠authority flag degrades honestly).
  3. ESCALATE case — extraction counterfactual + dignity breach + no consent.
  4. ADVISORY INVARIANT — verdict is ALWAYS in {CLEAR, CONCERN, ESCALATE}
     and NEVER a kernel verdict (SEAL/SABAR/HOLD/VOID).
  5. Advisory wiring — gate `_constitutional_gate` verdict unchanged;
     `_hold`/`_ok` metadata attachment is additive only.
  6. Reality-graph annotation — `annotate_with_irfan` preserves the step.

IRFAN IS ADVISORY. These tests pin that.
"""

from __future__ import annotations

import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from arifosmcp.runtime.irfan_review import (  # noqa: E402
    IRFAN_ALLOWED_VERDICTS,
    IRFAN_CANONICAL_QUESTION,
    IRFAN_IS_ADVISORY,
    IRFAN_KERNEL_VERDICTS,
    IrfanReviewInput,
    annotate_with_irfan,
    build_irfan_input_from_context,
    irfan_review_for_action,
    review_irfan,
)

TEST_NAMES = {
    "Capability-Authority Test",
    "Power-Abstention Test",
    "Weakest-Affected-Party Test",
    "Extractor-Steward Counterfactual",
    "Precedent Test",
    "Dependency Test",
    "Non-Paternalism Test",
    "Dissent Test",
    "Repair Test",
    "Anti-Hantu Test",
}


def _benign_input() -> IrfanReviewInput:
    """All 14 inputs provided, benign, with least-power + repair plan."""
    return IrfanReviewInput(
        intended_benefit=(
            "restore service for the affected tenant at their explicit request"
        ),
        evidence_state="measured: disk 97% full, observed via df and logs",
        uncertainty_state="low: failure mode confirmed by two independent probes",
        authority_basis="runbook RB-12 authorizes the on-call rotation for this",
        consent_basis="tenant filed the request and approved the restart window",
        stakeholder_map={"weakest": "tenant on-call", "others": "platform team"},
        power_asymmetry_map={
            "weakest": "tenant",
            "asymmetry": "documented and addressed in the plan",
        },
        reversibility_plan="config rollback via git revert; restart is re-runnable",
        repair_plan="backup restore verified in staging before execution",
        non_action_alternative="wait for the maintenance window (longer outage)",
        least_power_alternative="restart the single affected worker, not the cluster",
        dependency_impact="none new; existing documented dependency unchanged",
        dignity_impact="none; workload and dignity untouched",
        precedent_impact=(
            "creates a habit of scoped, consented, reversible restarts — a "
            "stewardship precedent"
        ),
    )


def _test_by_name(review: dict, name: str) -> dict:
    matches = [t for t in review["tests"] if t["name"] == name]
    assert len(matches) == 1, f"expected exactly one {name!r}, got {len(matches)}"
    return matches[0]


# ── 1. CLEAR ─────────────────────────────────────────────────────────────────


def test_clear_case_all_benign() -> None:
    review = review_irfan(_benign_input(), action_class="MUTATE", reversibility="reversible")
    assert review["verdict"] == "CLEAR"
    assert len(review["tests"]) == 10
    assert {t["name"] for t in review["tests"]} == TEST_NAMES
    assert all(t["status"] == "PASS" for t in review["tests"])
    assert review["reasons"] == ["All 10 stewardship tests passed."]
    # Power-restraint inputs actually consumed
    assert "single affected worker" in _test_by_name(
        review, "Power-Abstention Test"
    )["evidence"]
    assert "backup restore" in _test_by_name(review, "Repair Test")["evidence"]
    # Canonical question always present
    assert review["habit_question"] == IRFAN_CANONICAL_QUESTION


# ── 2. CONCERN ───────────────────────────────────────────────────────────────


def test_concern_irreversible_mutation_without_repair_plan() -> None:
    inp = _benign_input()
    inp.repair_plan = None  # irreversible action, no repair plan
    review = irfan_review_for_action(
        "arif_vault_seal",
        "seal",
        "agent-x",
        "IRREVERSIBLE",
        "irreversible",
        {},
    )
    assert review["verdict"] == "CONCERN"
    repair = _test_by_name(review, "Repair Test")
    assert repair["status"] == "CONCERN"
    assert "irreversible" in repair["reason"].lower()
    # No FAIL anywhere — this is a concern, not an escalation.
    assert all(t["status"] != "FAIL" for t in review["tests"])


def test_concern_capability_authority_flag_unknown_basis() -> None:
    """A capability≠authority FLAG (unknown authority basis) degrades to
    CONCERN — it is an honest gap, not a stated violation."""
    inp = _benign_input()
    inp.authority_basis = None  # authority unknown
    review = review_irfan(inp, action_class="MUTATE", reversibility="reversible")
    assert review["verdict"] == "CONCERN"
    cap = _test_by_name(review, "Capability-Authority Test")
    assert cap["status"] == "CONCERN"
    assert "authority" in cap["reason"].lower()


def test_concern_no_least_power_alternative_for_mutation() -> None:
    inp = _benign_input()
    inp.least_power_alternative = None
    inp.non_action_alternative = None
    review = review_irfan(inp, action_class="MUTATE", reversibility="reversible")
    assert review["verdict"] == "CONCERN"
    abstention = _test_by_name(review, "Power-Abstention Test")
    assert abstention["status"] == "CONCERN"
    assert "least-power" in abstention["reason"].lower()


# ── 3. ESCALATE ──────────────────────────────────────────────────────────────


def test_escalate_extraction_dignity_breach_no_consent() -> None:
    review = irfan_review_for_action(
        "arif_forge_execute",
        "execute",
        "agent-y",
        "IRREVERSIBLE",
        None,
        {
            "intended_benefit": "profit, because we can — an impressive demo",
            "consent_basis": "without consent, forced through",
            "dignity_impact": "dignity breach; degrading to the affected party",
            "authority_basis": "exceeds the actor's mandate",
        },
    )
    assert review["verdict"] == "ESCALATE"
    failed = {t["name"] for t in review["tests"] if t["status"] == "FAIL"}
    assert "Extractor-Steward Counterfactual" in failed  # extraction
    assert "Non-Paternalism Test" in failed  # coercion / no consent
    assert "Weakest-Affected-Party Test" in failed  # dignity breach
    assert "Capability-Authority Test" in failed  # capability≠authority
    # Reasons list is one line per non-PASS test
    non_pass = [t for t in review["tests"] if t["status"] != "PASS"]
    assert len(review["reasons"]) == len(non_pass)
    assert review["verdict"] not in IRFAN_KERNEL_VERDICTS


def test_escalate_phantom_claim() -> None:
    inp = _benign_input()
    inp.evidence_state = "claimed but not measured"
    review = review_irfan(inp, action_class="MUTATE", reversibility="reversible")
    assert review["verdict"] == "ESCALATE"
    assert _test_by_name(review, "Anti-Hantu Test")["status"] == "FAIL"


# ── 4. ADVISORY INVARIANT ────────────────────────────────────────────────────


@pytest.mark.parametrize(
    "kwargs",
    [
        {},  # everything absent — honest degradation
        {"action_class": "OBSERVE", "reversibility": "reversible"},
        {"action_class": "MUTATE", "reversibility": "mutating"},
        {"action_class": "IRREVERSIBLE", "reversibility": "irreversible"},
        {
            "payload": {"intended_benefit": "profit only, because possible"},
            "action_class": "EXTERNAL_SIDE_EFFECT",
        },
        {
            "payload": {"consent_basis": "without consent"},
            "action_class": "MUTATE",
        },
        {
            "payload": {"evidence_state": "assumed"},
            "action_class": "MUTATE",
        },
        {
            "payload": {"precedent_impact": "normalizes bypass of review"},
            "action_class": "MUTATE",
        },
        {"payload": {"authority_basis": "no authority granted"}},
    ],
)
def test_advisory_invariant_verdict_domain(kwargs: dict) -> None:
    review = irfan_review_for_action("some_tool", "some_mode", "some_actor", **kwargs)
    assert review["verdict"] in IRFAN_ALLOWED_VERDICTS
    assert review["verdict"] not in IRFAN_KERNEL_VERDICTS
    assert review["advisory"] is True
    for t in review["tests"]:
        assert t["status"] in {"PASS", "CONCERN", "FAIL"}


def test_irfan_is_advisory_constant() -> None:
    assert IRFAN_IS_ADVISORY is True
    assert IRFAN_ALLOWED_VERDICTS == frozenset({"CLEAR", "CONCERN", "ESCALATE"})
    assert IRFAN_KERNEL_VERDICTS == frozenset({"SEAL", "SABAR", "HOLD", "VOID"})
    assert not (IRFAN_ALLOWED_VERDICTS & IRFAN_KERNEL_VERDICTS)


def test_every_test_result_advisory_flagged() -> None:
    review = irfan_review_for_action("t", "m", "a", action_class="MUTATE")
    assert all(t["advisory"] is True for t in review["tests"])


# ── 5. Context mapping — never fabricate ─────────────────────────────────────


def test_build_input_absent_fields_stay_none() -> None:
    inp = build_irfan_input_from_context("tool_a", "observe", None, None, None, None)
    assert inp.intended_benefit is None
    assert inp.consent_basis is None
    assert inp.repair_plan is None
    assert inp.least_power_alternative is None
    assert inp.authority_basis is None  # no actor → nothing to record


def test_build_input_records_actor_honestly_without_inventing() -> None:
    inp = build_irfan_input_from_context("tool_a", "observe", "actor-7")
    # The OBSERVED fact (actor present) is recorded; the authority basis is
    # NOT invented.
    assert inp.authority_basis is not None
    assert "actor_id=actor-7" in str(inp.authority_basis)
    assert "not provided" in str(inp.authority_basis)


def test_build_input_maps_genuinely_available_payload_fields() -> None:
    inp = build_irfan_input_from_context(
        "tool_a",
        "mutate",
        "actor-7",
        "MUTATE",
        "mutating",
        {
            "reversibility": "reversible",
            "reversibility_plan": "git revert",
            "consent": "granted by operator",
            "stakeholders": ["ops", "tenant"],
            "repair_plan": "snapshot restore",
            "least_power": "single-node restart",
        },
    )
    assert inp.reversibility_plan == "git revert"
    assert inp.consent_basis == "granted by operator"
    assert inp.stakeholder_map == ["ops", "tenant"]
    assert inp.repair_plan == "snapshot restore"
    assert inp.least_power_alternative == "single-node restart"


def test_payload_reversibility_statement_feeds_action_shape() -> None:
    review = irfan_review_for_action(
        "tool_a", "mutate", "actor-7", None, None, {"reversibility": "irreversible"}
    )
    assert review["context"]["reversibility"] == "irreversible"


# ── 6. Reality-graph advisory annotation ─────────────────────────────────────


def test_annotate_with_irfan_preserves_step_verdict_and_status() -> None:
    step = {
        "gate": "REALITY_LOOP",
        "verdict": "SABAR",
        "passed": True,
        "violated_laws": [],
    }
    out = annotate_with_irfan(
        step, tool_name="arif_vault_seal", action_class="IRREVERSIBLE"
    )
    assert out is step  # annotated in place, same object
    assert step["verdict"] == "SABAR"  # untouched
    assert step["passed"] is True  # untouched
    irfan = step["irfan"]
    assert irfan["advisory"] is True
    assert irfan["verdict"] in IRFAN_ALLOWED_VERDICTS
    assert irfan["verdict"] not in IRFAN_KERNEL_VERDICTS
    assert irfan["habit_question"] == IRFAN_CANONICAL_QUESTION
    assert "top_failing_test" in irfan


def test_annotate_with_irfan_fail_open_honest_absence() -> None:
    step = {"verdict": "PROCEED"}
    out = annotate_with_irfan(
        step, tool_name="t", action_class="NOT-EVEN-REAL", payload={"bad": object()}
    )
    # Even on internal failure the annotation must never fabricate a verdict.
    assert out["verdict"] == "PROCEED"
    assert out["irfan"]["advisory"] is True
    assert out["irfan"]["verdict"] in IRFAN_ALLOWED_VERDICTS | {None}


def test_annotate_with_irfan_non_dict_passthrough() -> None:
    assert annotate_with_irfan(None) is None
    sentinel: list = []
    assert annotate_with_irfan(sentinel) is sentinel  # type: ignore[arg-type]


# ── 7. Gate wiring — advisory, never verdict-changing ────────────────────────


def test_gate_seal_path_verdict_unchanged_and_irfan_advisory_stashed() -> None:
    from arifosmcp.runtime import tools as runtime_tools

    # Observe-class call passes the gate exactly as before (returns None).
    result = runtime_tools._constitutional_gate(
        "arif_kernel_health", "vitals", "irfan-probe-actor"
    )
    assert result is None  # gate verdict untouched by Irfan
    stashed = runtime_tools.IRFAN_LAST_REVIEW.get()
    assert isinstance(stashed, dict)
    assert stashed["verdict"] in IRFAN_ALLOWED_VERDICTS
    assert stashed["verdict"] not in IRFAN_KERNEL_VERDICTS
    assert stashed["context"]["tool_name"] == "arif_kernel_health"


def test_gate_hold_path_still_holds_with_irfan_metadata_additive() -> None:
    from arifosmcp.runtime import tools as runtime_tools

    # Tier-3 irreversible tool, no sovereign session, no chain id → HOLD
    # (L13). Irfan must not soften OR harden this.
    response = runtime_tools._constitutional_gate(
        "arif_forge_execute", "execute", "unverified-actor"
    )
    assert isinstance(response, dict)
    assert response["status"] == "HOLD"
    assert response["can_mutate"] is False
    assert response.get("can_claim_success") is not True


def test_hold_response_carries_irfan_review_as_metadata_only() -> None:
    from arifosmcp.runtime import tools as runtime_tools

    review = irfan_review_for_action(
        "wired_tool", "mutate", "actor-9", "MUTATE", "mutating", {}
    )
    token = runtime_tools.IRFAN_LAST_REVIEW.set(review)
    try:
        response = runtime_tools._hold("wired_tool", "test reason", ["F2"])
        assert response["status"] == "HOLD"
        attached = response["meta"].get("irfan_review")
        assert isinstance(attached, dict)
        assert attached["verdict"] in IRFAN_ALLOWED_VERDICTS
        assert attached["verdict"] not in IRFAN_KERNEL_VERDICTS
    finally:
        runtime_tools.IRFAN_LAST_REVIEW.reset(token)


def test_hold_response_does_not_attach_mismatched_tool_review() -> None:
    from arifosmcp.runtime import tools as runtime_tools

    review = irfan_review_for_action("other_tool", "mutate", "actor-9", "MUTATE")
    token = runtime_tools.IRFAN_LAST_REVIEW.set(review)
    try:
        response = runtime_tools._hold("wired_tool", "test reason", ["F2"])
        assert "irfan_review" not in response["meta"]
    finally:
        runtime_tools.IRFAN_LAST_REVIEW.reset(token)
