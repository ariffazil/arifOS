"""S4 verdict-channel closure regression (F13 FIX-S4, "FIX S4" imperative 2026-09-22).

Four mechanisms proven live 2026-09-22 against the running kernel and pinned here:

M1 — axis poisoning (G3): fq_gate wrote arifFlow/FQ tokens
     (UNKNOWN_ACTOR, UNREACHABLE, FLOWING, STUCK) into a key NAMED `verdict`
     inside metabolic_state. reconcile_decision_contract walks every
     verdict-bearing key → UNKNOWN_VERDICT_TOKEN → fail-closed HOLD on EVERY
     response embedding session state. Live: init hold_reason
     UNKNOWN_VERDICT_TOKEN:result.metabolic_state.verdict=UNKNOWN_ACTOR.
     Fix: axis separation — key renamed `fq_outcome`; walker untouched
     (still validates every carrier-named key; vigilance intact).

M2 — stage-invalid integrity (G1 core): judge postcondition compared the
     pre-judgment envelope effective_verdict against THIS judgment's verdict.
     Any legitimate disagreement read integrity=False → SEAL rewritten to
     SABAR, with integrity=False left in the report → reconcile Point-#4
     re-vetoed → HOLD self-perpetuating; a judge could never clear inherited
     state (the permanent seal-door block). Fix: callers defer (pass "");
     on substantive-rewrite the stale bit is cleared (downgrade for REAL
     evidence gaps kept).

M3 — frozen-core staleness: zen decision_core froze from `verdict`
     (default HOLD) while the envelope canonical field was effective_verdict
     → guaranteed VERDICT_FIELD_DIVERGENCE (core=HOLD beside root=SABAR).
     Fix: _extract_verdict_str prefers effective_verdict (last writer).

M4 — drift (S5 moving condition): redeploy aligns stamp ↔ HEAD; the
     DEPLOYMENT_DRIFT session flag is not re-tested here (operational).

STAGED (registered, not patched): band-vs-judgment admissible-combination
matrix (vocabulary-owners ruling per verdict.py review 2026-09-22);
prior-effective domination when attach merges a stale non-empty existing;
phantom spec path cited by judge_postcondition docstring; e-a26871f2(b)
W4 human-witness floor design question.

DITEMPA BUKAN DIBERI.
"""

from __future__ import annotations

from arifosmcp.composer import _extract_verdict_str
from arifosmcp.runtime.fq_gate import metabolic_cap
from arifosmcp.runtime.judge_postcondition import check_judge_postcondition
from arifosmcp.runtime.verdict import reconcile_decision_contract


# ── M1: axis separation ─────────────────────────────────────────────────────


def test_fq_state_has_no_verdict_key():
    """The FQ axis may never publish a key the verdict walker treats as carrier."""
    _, state = metabolic_cap(None, "FULL")
    assert "verdict" not in state, "fq axis leaking into verdict channel"
    assert state["fq_outcome"] == "NO_ACTOR"


def test_fq_sovereign_exempt_axis_shape():
    _, state = metabolic_cap("arif", "FULL", is_sovereign_principal=True)
    assert state["fq_outcome"] == "SOVEREIGN_EXEMPT"
    assert "verdict" not in state


def _flags(out: dict) -> list:
    return ((out.get("meta") or {}).get("reconciliation") or {}).get("flags") or []


def test_reconcile_is_poison_free_with_renamed_axis():
    resp = {
        "effective_verdict": "SABAR",
        "result": {
            "verdict": "SABAR",
            "metabolic_state": {"fq_outcome": "UNKNOWN_ACTOR", "actor_id": "x"},
        },
        "meta": {"judge_postcondition": {"verdict": "SABAR", "verdict_channel_integrity": True}},
    }
    out = reconcile_decision_contract(resp)
    flags = _flags(out)
    assert not any("UNKNOWN_VERDICT_TOKEN" in f for f in flags), flags
    # non-vacuous: clean carriers must keep their verdict (no fail-closed flip)
    assert out.get("effective_verdict") == "SABAR", (out.get("effective_verdict"), flags)
    rec = (out.get("meta") or {}).get("reconciliation") or {}
    assert rec.get("inconsistent") is not True, rec


def test_reconcile_still_catches_old_shape_and_true_unknowns():
    """Walker vigilance intact: a key NAMED verdict with unknown token still vetoes."""
    resp = {
        "effective_verdict": "SABAR",
        "result": {"metabolic_state": {"verdict": "UNKNOWN_ACTOR"}},
    }
    out = reconcile_decision_contract(resp)
    flags = _flags(out)
    assert any(f.startswith("UNKNOWN_VERDICT_TOKEN") for f in flags), flags
    assert out.get("effective_verdict") == "HOLD"  # fail-closed, by design


# ── M2: stage-valid integrity ───────────────────────────────────────────────


def _ev_ok() -> dict:
    return {"note": "measured", "observations": ["md5 live-probe equality"]}


def test_stale_integrity_no_longer_vetoes_or_persists():
    """Stale effective-vs-verdict compare: SEAL survives; bit cleared, not False."""
    rep = check_judge_postcondition(
        mode="judge",
        candidate="A1-A5 seal chain candidate — substantive text",
        evidence=_ev_ok(),
        verdict_str="SEAL",
        effective_verdict="HOLD",  # inherited/stale pre-judgment state
    )
    assert rep["verdict_channel_integrity"] is None
    assert "verdict_channel_integrity" not in rep["missing_evidence"]
    assert rep["applied"] is False
    assert rep["verdict"] == "SEAL"


def test_real_evidence_gap_still_downgrades():
    """Provenance gaps keep the conservative rewrite (substantive-evidence law)."""
    rep = check_judge_postcondition(
        mode="judge",
        candidate="substantive candidate text",
        evidence={"note": "no provenance keys and scalar-only values"},
        verdict_str="SEAL",
        effective_verdict="HOLD",
    )
    assert rep["applied"] is True
    assert rep["verdict"] == "SABAR"
    assert rep["missing_evidence"] == ["provenance"]
    assert rep["verdict_channel_integrity"] is None


def test_empty_evidence_rule1_unchanged():
    rep = check_judge_postcondition(
        mode="judge",
        candidate="substantive candidate text",
        evidence=None,
        verdict_str="SEAL",
        effective_verdict="",
    )
    assert rep["applied"] is True
    assert rep["verdict"] == "HOLD"
    assert rep["reason_code"] == "EVIDENCE_EMPTY_RULE1"


def test_deferred_caller_integrity_is_none_not_false():
    rep = check_judge_postcondition(
        mode="judge",
        candidate="substantive candidate",
        evidence=_ev_ok(),
        verdict_str="SEAL",
        effective_verdict="",  # S4 defer at judge call sites
    )
    assert rep["verdict_channel_integrity"] is None
    assert rep["verdict"] == "SEAL"
    assert rep["applied"] is False


# ── M3: frozen core tracks the canonical field ──────────────────────────────


def test_extract_is_stage_valid_at_freeze():
    """R-1/M3c: stage-native judgment wins; interim effective is never frozen."""
    # judgment present → judgment (effective at this stage is pre-wrapper interim)
    assert _extract_verdict_str({"effective_verdict": "SABAR", "verdict": "HOLD"}) == "HOLD"
    # interim effective ALONE → "" (absence of a stage-native judgment)
    assert _extract_verdict_str({"effective_verdict": "SABAR"}) == ""
    # heart-lineage tools: judgment lives in action_risk_verdict (canonical tokens)
    assert _extract_verdict_str({"action_risk_verdict": "HOLD"}) == "HOLD"
    # absence is NOT a claim — never fabricate a verdict from nothing
    assert _extract_verdict_str({}) == ""


def test_seed_result_verdict_fills_absent_and_gates_win():
    from arifosmcp.composer import seed_result_verdict

    # absent → filled from the postcondition-passed judgment (one lineage)
    r: dict = {}
    seed_result_verdict(r, "SABAR")
    assert r["verdict"] == "SABAR"
    # a governance gate wrote HOLD first → gate wins (fill-if-absent only)
    g: dict = {"verdict": "HOLD"}
    seed_result_verdict(g, "SABAR")
    assert g["verdict"] == "HOLD"
    # None counts as absent (the observed live judge shape)
    n: dict = {"verdict": None}
    seed_result_verdict(n, "SEAL")
    assert n["verdict"] == "SEAL"


# ── M1b: session_birth carries the AUTHORITY BAND, not a judgment ───────────


def test_birth_band_path_is_an_axis_not_a_verdict_carrier():
    """session_birth.verdict pins the band by design (5 tests) — carved out.

    Live evidence: init flagged
    UNKNOWN_VERDICT_TOKEN:result.session_birth.verdict=LIMITED_MUTATE —
    any non-OBSERVE band is 'unknown' to the verdict vocabulary, so every
    verified init fail-closed to HOLD.
    """
    resp = {
        "effective_verdict": "SABAR",
        "result": {"session_birth": {"verdict": "LIMITED_MUTATE", "authority_mode": "LIMITED_MUTATE"}},
        "meta": {"judge_postcondition": {"verdict": "SABAR", "verdict_channel_integrity": True}},
    }
    out = reconcile_decision_contract(resp)
    flags = _flags(out)
    assert not any("UNKNOWN_VERDICT_TOKEN" in f for f in flags), flags
    assert out.get("effective_verdict") == "SABAR", (out.get("effective_verdict"), flags)


def test_true_unknown_carrier_still_vetoes():
    """Carve-out is PATH-scoped: an unknown token on a generic verdict key still vetoes."""
    resp = {"effective_verdict": "SABAR", "meta": {"odd": {"verdict": "TOTALLY_UNKNOWN"}}}
    out = reconcile_decision_contract(resp)
    flags = _flags(out)
    assert any(f.startswith("UNKNOWN_VERDICT_TOKEN") for f in flags), flags
    assert out.get("effective_verdict") == "HOLD"


# ── R-1b: stage-claim supersession (claim-state doctrine, Phase-0 law kept) ─


def test_stage_claim_supersession_resolves_cross_stage_flag_without_rewrite():
    """postcond stage claim → SUPERSEDED (degradation direction only);
    field NEVER rewritten; no cross-stage flag once effective is attach-final."""
    resp = {
        "verdict": "HOLD",
        "effective_verdict": "HOLD",  # attach re-derives effective BEFORE reconcile
        "meta": {
            "judge_postcondition": {"verdict": "SABAR", "verdict_channel_integrity": None},
            "zen_apex": {"decision_core": {"verdict": "HOLD"}},
        },
    }
    out = reconcile_decision_contract(resp)
    pc = out["meta"]["judge_postcondition"]
    # Phase-0 law: the disagreeing field is NEVER rewritten
    assert pc["verdict"] == "SABAR", "stage history must stay in place"
    # claim-state doctrine: marked superseded (degradation direction: HOLD<=SABAR)
    assert pc["verdict_state"] == "SUPERSEDED"
    assert pc["superseded_by_final_verdict"] == "HOLD"
    assert "superseded_note" in pc
    # the cross-stage NOISE flag is gone; live verdict is the final
    assert not any("VERDICT_FIELD_DIVERGENCE" in f for f in _flags(out)), _flags(out)
    assert out.get("effective_verdict") == "HOLD"


def test_upgrade_direction_stage_hold_never_supersedes():
    """Stage HOLD vs final SEAL = dangerous smoothing — stays a LIVE veto
    (Phase-0 nested-conflict doctrine, mirrored here for the R-1b guard)."""
    resp = {
        "verdict": "SEAL",
        "effective_verdict": "SEAL",
        "meta": {"judge_postcondition": {"verdict": "HOLD"}},
    }
    out = reconcile_decision_contract(resp)
    pc = out["meta"]["judge_postcondition"]
    assert "verdict_state" not in pc, "upgrade direction must never supersede"
    assert pc["verdict"] == "HOLD"
    assert out.get("effective_verdict") == "HOLD"  # veto intact
    assert any("VERDICT_FIELD_DIVERGENCE" in f for f in _flags(out)), _flags(out)


def test_stage_claim_equal_is_not_marked():
    resp = {
        "verdict": "SABAR",
        "effective_verdict": "SABAR",
        "meta": {"judge_postcondition": {"verdict": "SABAR"}},
    }
    out = reconcile_decision_contract(resp)
    pc = out["meta"]["judge_postcondition"]
    assert "verdict_state" not in pc, "equal claims are not superseded"
    assert not any("VERDICT_FIELD_DIVERGENCE" in f for f in _flags(out)), _flags(out)


if __name__ == "__main__":  # pragma: no cover
    import pytest

    raise SystemExit(pytest.main([__file__, "-v"]))
