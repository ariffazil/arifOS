"""D2 regression — akal pre-judge rename + SABAR<->HOLD restraint-pair rule.

888-APEX verdict 2026-11-04 (D2, session SEAL-3f6a3d2834a44416):
(b) producer-side rename (akal dual_eval verdict -> pre_judge_state) so a
pre-judge advisory opinion never enters the reconciler's claim set, PLUS the
restraint-pair rule: HOLD/SABAR = same restraint class (no act, no seal),
zero behavioral delta = name collision, not a live veto.

RED before, GREEN after. T3 is the anti-masking tripwire: any bearing-key
disagreement OUTSIDE exactly {HOLD, SABAR} must still veto.

Note: reconcile_decision_contract is the live envelope-close reconciler
(tools.py:27920/27994). attach_effective_verdict early-returns on simple
responses and delegates here at verdict.py:623.
"""

from __future__ import annotations

import pathlib
import re

from arifosmcp.core.akal_wiring import akal_pre_judge
from arifosmcp.runtime.verdict import reconcile_decision_contract


def test_t5_restraint_pair_no_veto():
    """{effective: SABAR, postcondition: HOLD} -> recorded, NOT vetoed."""
    resp = {
        "akal": {"dual_eval": {"pre_judge_state": "HOLD"}},
        "effective_verdict": "SABAR",
        "meta": {"judge_postcondition": {"verdict": "HOLD"}},
    }
    reconcile_decision_contract(resp)
    rec = resp.get("meta", {}).get("reconciliation", {})
    assert rec.get("inconsistent") is False, rec
    assert rec.get("reason") == "RESTRAINT_PAIR", rec
    assert any("RESTRAINT_PAIR" in str(f) for f in rec.get("flags", [])), rec
    # canonical selection policy unchanged: NOT forced to HOLD
    assert resp.get("effective_verdict") == "SABAR", resp.get("effective_verdict")


def test_t3_cross_class_disagreement_still_vetoes():
    """Anti-masking tripwire: {effective: SEAL, postcondition: HOLD} vetoes.

    This is the UPGRADE direction R-1b deliberately keeps live (stage HOLD
    vs final SEAL — verdict.py R-1b note: "dangerous smoothing, REMAINS a
    live contradiction and keeps vetoing"). Note: the reverse direction
    (stage SEAL vs final SABAR) is superseded BY DESIGN in the degradation
    direction — conservative, not a masking gap; do not "fix" it back.
    """
    resp = {
        "effective_verdict": "SEAL",
        "meta": {"judge_postcondition": {"verdict": "HOLD"}},
    }
    reconcile_decision_contract(resp)
    rec = resp.get("meta", {}).get("reconciliation", {})
    assert rec.get("inconsistent") is True, rec
    assert any("VERDICT_FIELD_DIVERGENCE" in str(f) for f in rec.get("flags", [])), rec
    assert resp.get("effective_verdict") == "HOLD"  # fail-closed preserved


def test_t2_akal_returns_pre_judge_state_not_verdict():
    out = akal_pre_judge(blast_radius="low")
    assert "pre_judge_state" in out, list(out.keys())
    assert "verdict" not in out, list(out.keys())
    assert out["pre_judge_state"] in ("HOLD", "SEAL", "SABAR", "VOID"), out


def test_t6_no_consumer_reads_renamed_key():
    repo = pathlib.Path(__file__).resolve().parents[1]
    bad = []
    for p in (repo / "arifosmcp").rglob("*.py"):
        if p.name == "akal_wiring.py":
            continue
        src = p.read_text(errors="ignore")
        if (
            re.search(r'dual\.get\("verdict"', src)
            or re.search(r'dual_eval"\]\s*\[\s*"verdict"', src)
            or re.search(r'dual_eval"\]\.get\("verdict"', src)
        ):
            bad.append(str(p))
    assert not bad, f"consumers still read the renamed key: {bad}"
    wiring = (repo / "arifosmcp" / "core" / "akal_wiring.py").read_text()
    assert '"pre_judge_state"' in wiring
    server = (repo / "arifosmcp" / "server.py").read_text()
    assert '"pre_judge_state"' in server
