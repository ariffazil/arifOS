"""Phase 0 (2026-09-22, F13 + review disposition): decision-contract reconciliation.

Boundaries under test — PR 1 "judgment integrity" only:
  #1 payload-wide recursive walk (a two-field compare passes the exact
     contradictory payload it claims to detect),
  #2 next_safe_action derived from reconciled state (crack #2),
  #3 closed vocabulary: unknown and unratified layer tokens fail closed,
  #4 EPISTEMIC vetoes (unmeasured pass, provenance mismatch, channel break).

Authorization (anonymous actor, authority service, grants) is deliberately
OUT of this module's responsibility — tested separately below only as the
posture "the reconciler never enables authority".
Fixture is an immutable live capture; hash-pinned so the contradiction
cannot be simplified away later.
"""
from __future__ import annotations

import copy
import hashlib
import json
from pathlib import Path

from arifosmcp.runtime.verdict import (
    HOLD,
    REASON_HOLD,
    reconcile_decision_contract,
)

FIXTURE = (
    Path(__file__).resolve().parent.parent
    / "fixtures"
    / "phase0_judge_payload_20260922.json"
)
FIXTURE_SHA256 = "1fff9c7ab33aa3684970d2a400abae1e3e03c69d7940e709d8a2472fae9f1686"


def _load_fixture() -> dict:
    return json.loads(FIXTURE.read_text())


def _reconciled(payload: dict) -> dict:
    return reconcile_decision_contract(copy.deepcopy(payload))


# ── fixture integrity ───────────────────────────────────────────────────────

def test_fixture_is_immutable_hash_pinned():
    digest = hashlib.sha256(FIXTURE.read_bytes()).hexdigest()
    assert digest == FIXTURE_SHA256, (
        "The 2026-09-22 live payload must never be edited — it is the "
        "evidence the two-field reconcile failed."
    )


# ── #1: real payload — two fields agree, walker still catches it ────────────

def test_live_fixture_two_field_reconcile_would_pass_but_walker_flags():
    payload = _load_fixture()
    # Proof of F13 point #1: the naive compare agrees...
    assert payload["verdict"] == payload["effective_verdict"] == "HOLD"
    out = _reconciled(payload)
    # ...the walker does not.
    assert out["effective_verdict"] == HOLD
    rec = (out.get("meta") or {}).get("reconciliation") or {}
    assert rec.get("inconsistent") is True
    assert rec.get("reason") == "INCONSISTENT_VERDICT_STATE"
    assert "meta.kernel_intercept.decision" in rec.get("claims", {})
    # raw values preserved for audit (receipt carries raw + canonical)
    assert rec.get("raw_tokens", {}).get("meta.kernel_intercept.decision") == "ALLOW"
    # unratified layer token flagged on its own (ALLOW never silently = SEAL)
    assert any(f.startswith("NONCANONICAL_VERDICT_TOKEN") for f in rec.get("flags", []))
    assert any(
        f.startswith("VERDICT_FIELD_DIVERGENCE") for f in rec.get("flags", [])
    )
    assert any(
        f.startswith("EPISTEMIC_VERDICT_CHANNEL_INTEGRITY") for f in rec.get("flags", [])
    )
    assert any(str(r).startswith("INCONSISTENT_STATE") for r in out.get("reasons", []))
    assert out["reason_code"] == REASON_HOLD
    # originals preserved — the contradiction is evidence, not rewritten away
    assert out["meta"]["kernel_intercept"]["decision"] == "ALLOW"
    # supplied next_safe_action must NOT survive an inconsistent
    # reconciliation — fixture evidence: both the dict-form action and the
    # inner string read "Execute the capability..." on an authority-off HOLD.
    supplied = rec.get("supplied_next_safe_action", {})
    assert supplied["response.action"].startswith("Execute the capability")
    assert supplied["result"].startswith("Execute the capability")
    assert (
        out["next_safe_action"]["action"]
        == "Await input — effective_verdict=HOLD (reconciled)"
    )  # dict shape preserved, instruction derived
    assert (
        out["result"]["next_safe_action"]
        == "Await input — effective_verdict=HOLD (reconciled)"
    )


def test_live_fixture_is_idempotent():
    payload = _load_fixture()
    once = reconcile_decision_contract(copy.deepcopy(payload))
    twice = reconcile_decision_contract(copy.deepcopy(once))
    assert twice["effective_verdict"] == HOLD
    reasons = [r for r in twice.get("reasons", []) if str(r).startswith("INCONSISTENT_STATE")]
    assert len(reasons) == 1
    assert (twice.get("meta") or {}).get("reconciliation", {}).get("inconsistent") is True


# ── authorization posture: the reconciler NEVER enables authority ───────────
# (anonymous-actor authorization is a separate boundary — authority
#  service PR — this only pins the reconciler's own posture.)

def test_reconciler_never_enables_authority():
    for payload in (_load_fixture(), {"verdict": "SEAL", "effective_verdict": "SEAL"}):
        out = _reconciled(payload)
        rec = (out.get("meta") or {}).get("reconciliation")
        if rec is not None:
            assert rec["authority_enabled"] is False
            assert rec["execution_enabled"] is False
            assert rec["seal_eligible"] is False
    # on a flagged payload the envelope flags themselves are forced off
    out = _reconciled(_load_fixture())
    assert out["mutation_allowed"] is False
    assert out["seal_allowed"] is False


# ── #3: closed enum ─────────────────────────────────────────────────────────

def test_unknown_verdict_token_fails_closed_to_hold():
    out = _reconciled({"effective_verdict": "QUALIFY", "verdict": "QUALIFY"})
    assert out["effective_verdict"] == HOLD
    rec = out["meta"]["reconciliation"]
    assert any(f.startswith("UNKNOWN_VERDICT_TOKEN") for f in rec["flags"])


def test_unratified_layer_token_fails_closed_even_when_canonicals_agree():
    # ALLOW normalizes to SEAL — but layer vocabulary is unratified: a
    # kernel-intercept ALLOW must never silently certify a constitutional
    # SEAL (review 2026-09-22: heterogeneous non-identical values fail closed).
    out = _reconciled(
        {"verdict": "SEAL", "effective_verdict": "SEAL", "meta": {"gate": {"decision": "ALLOW"}}}
    )
    assert out["effective_verdict"] == HOLD
    flags = out["meta"]["reconciliation"]["flags"]
    assert any(f.startswith("NONCANONICAL_VERDICT_TOKEN") for f in flags)


def test_receipt_era_observe_alias_normalizes_not_flags():
    out = _reconciled({"verdict": "OBSERVE", "effective_verdict": "OBSERVE_ONLY"})
    assert "meta" not in out or "reconciliation" not in (out.get("meta") or {})
    assert out["effective_verdict"] == "OBSERVE_ONLY"


# ── divergence beyond the two headline fields ───────────────────────────────

def test_nested_verdict_conflict_forces_hold_and_preserves_originals():
    payload = {
        "verdict": "SEAL",
        "effective_verdict": "SEAL",
        "meta": {"judge_postcondition": {"verdict": "HOLD"}},
    }
    out = _reconciled(payload)
    assert out["effective_verdict"] == HOLD
    assert out["meta"]["judge_postcondition"]["verdict"] == "HOLD"  # preserved
    assert out["mutation_allowed"] is False and out["seal_allowed"] is False
    assert out["status"] == "completed" and out["execution_state"] == "AWAIT_INPUT"


def test_null_inner_value_is_not_a_claim_no_mass_hold():
    # schema-default nulls must never trigger the veto (bricking guard)
    payload = {
        "verdict": "HOLD",
        "effective_verdict": "HOLD",
        "result": {"effective_verdict": None, "sufficiency_verdict": None},
    }
    out = _reconciled(payload)
    assert "reconciliation" not in (out.get("meta") or {})
    assert out["effective_verdict"] == HOLD


def test_clean_payload_passes_through_with_honest_hold_reason():
    payload = {
        "verdict": "HOLD",
        "effective_verdict": "HOLD",
        "reasons": ["OBSERVE_ONLY — identity not verified"],
        "next_safe_action": "Aborted: action violates constitutional floors (F1/F9/F13).",
        "constitutional_check": {"hold_required": True, "hold_reason": "outer_verdict=HOLD"},
    }
    out = _reconciled(payload)
    assert "reconciliation" not in (out.get("meta") or {})
    # consistent + forbidden-free text is preserved verbatim (transitional —
    # KNOWN LIMITATION: full derive-always deferred, three existing kernel
    # contracts pin handler-authored text)
    assert out["next_safe_action"] == "Aborted: action violates constitutional floors (F1/F9/F13)."
    # honest hold_reason vocabulary replaces outer_verdict= naming
    assert out["constitutional_check"]["hold_reason"].startswith("effective_verdict=HOLD")


# ── combined contradiction: every detected issue asserted (review test B) ───

def test_synthetic_broken_payload_flags_every_issue():
    payload = {
        "verdict": "HOLD",
        "effective_verdict": "HOLD",
        "kernel_intercept": {"decision": "ALLOW"},
        "judge_postcondition": {"verdict": "SEAL"},
        "constitutional_check": {"floors_invoked": [], "floor_passed": True},
        "claim_class": "MEASURED",
        "data_mode": "derived",
        "seal_allowed": False,
        "next_safe_action": "seal the result",
    }
    out = _reconciled(payload)
    assert out["effective_verdict"] == HOLD
    rec = out["meta"]["reconciliation"]
    assert rec["inconsistent"] is True
    joined = " ".join(rec["flags"])
    assert "NONCANONICAL_VERDICT_TOKEN" in joined          # layer token ALLOW
    assert "VERDICT_FIELD_DIVERGENCE" in joined            # ALLOW/SEAL vs HOLD
    assert "EPISTEMIC_UNMEASURED_PASS" in joined           # no check ≠ pass
    assert "EPISTEMIC_LABEL_PROVENANCE_MISMATCH" in joined # MEASURED on derived
    assert rec["authority_enabled"] is False
    assert rec["execution_enabled"] is False
    # input action ignored; output derived; no forbidden transition terms
    assert out["next_safe_action"] != payload["next_safe_action"]
    for term in ("seal", "forge", "commit", "execute", "deploy", "send", "transfer"):
        assert term not in out["next_safe_action"].casefold()
    # supplied text kept for audit only
    assert rec["supplied_next_safe_action"]["response"] == "seal the result"


# ── #2: next_safe_action derivation (crack #2) ──────────────────────────────

def test_next_safe_action_may_not_point_at_seal_when_authority_off():
    payload = {
        "verdict": "HOLD",
        "effective_verdict": "HOLD",
        "seal_allowed": False,
        "next_safe_action": "Proceed to arif_judge SEAL with constitutional_chain_id.",
    }
    out = _reconciled(payload)
    text = out["next_safe_action"]
    assert "seal" not in text.lower()
    assert text  # still actionable, just lawful


def test_inner_next_safe_action_also_derived():
    payload = {
        "verdict": "HOLD",
        "effective_verdict": "HOLD",
        "seal_allowed": False,
        "result": {"next_safe_action": "Call forge_commit next."},
    }
    out = _reconciled(payload)
    assert "commit" not in out["result"]["next_safe_action"].lower()


# ── #4: EPISTEMIC vetoes ────────────────────────────────────────────────────

def test_unmeasured_floor_presented_as_passed_forces_hold():
    payload = {
        "verdict": "SEAL",
        "effective_verdict": "SEAL",
        "constitutional_check": {"floor_passed": True, "floors_invoked": []},
    }
    out = _reconciled(payload)
    assert out["effective_verdict"] == HOLD
    flags = out["meta"]["reconciliation"]["flags"]
    assert any(f.startswith("EPISTEMIC_UNMEASURED_PASS") for f in flags)


def test_measured_floor_with_evidence_passes():
    payload = {
        "verdict": "SEAL",
        "effective_verdict": "SEAL",
        "constitutional_check": {"floor_passed": True, "law_results": {"L1": "pass"}},
    }
    out = _reconciled(payload)
    assert out["effective_verdict"] == "SEAL"
    assert "reconciliation" not in (out.get("meta") or {})


def test_measured_claim_on_derived_data_forces_hold():
    payload = {
        "verdict": "SEAL",
        "effective_verdict": "SEAL",
        "result": {"claim_class": "MEASURED", "data_mode": "inferred"},
    }
    out = _reconciled(payload)
    assert out["effective_verdict"] == HOLD
    flags = out["meta"]["reconciliation"]["flags"]
    assert any(f.startswith("EPISTEMIC_LABEL_PROVENANCE_MISMATCH") for f in flags)


# ── plumbing ────────────────────────────────────────────────────────────────

def test_non_dict_passthrough():
    assert reconcile_decision_contract("plain") == "plain"
    assert reconcile_decision_contract(None) is None
