"""Unwitnessed-evidence tests — judge postcondition UNKNOWN surfacing (2026-10-27).

Defect (external Claude reality test, confirmed in code): an evidence item
self-declared UNKNOWN (tag/claim_class "UNKNOWN") was swallowed silently —
the judge reported missing_evidence:[] while holding an item it never
witnessed. These tests pin the contract:

  1. UNKNOWN items surface in report["unwitnessed_evidence"] on EVERY verdict.
  2. For the SEAL family, unwitnessed items enter missing_evidence and fire
     the EVIDENCE_POSTCONDITION_VIOLATION downgrade (SEAL may not rest on
     self-declared unknowns).
  3. Non-SEAL verdicts are annotated only — no enforcement flip.
  4. Evidence with no UNKNOWN items behaves exactly as before.
"""

from __future__ import annotations

import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from arifosmcp.runtime.judge_postcondition import (  # noqa: E402
    check_judge_postcondition,
)

_EVIDENCE_WITH_UNKNOWN = {
    "value": [
        {"fact": "PHP 8.4.27 released 2026-10-21", "source": "CERT-EU", "tag": "OBS"},
        {"fact": "CVSS 9.2", "source": "community PoC repo", "tag": "UNKNOWN"},
    ]
}
_EVIDENCE_CLEAN = {
    "value": [
        {"fact": "PHP 8.4.27 released 2026-10-21", "source": "CERT-EU", "tag": "OBS"},
    ]
}


def test_unknown_item_surfaces_on_every_verdict():
    r = check_judge_postcondition(
        mode="judge",
        candidate="PHP security release claim",
        evidence=_EVIDENCE_WITH_UNKNOWN,
        verdict_str="HOLD",
        effective_verdict="HOLD",
    )
    assert r["unwitnessed_evidence"], "UNKNOWN item must surface"
    assert r["unwitnessed_evidence"][0]["index"] == 1
    assert r["unwitnessed_evidence"][0]["field"] == "tag"
    assert "CVSS 9.2" in r["unwitnessed_evidence"][0]["item"]


def test_hold_verdict_advisory_only_no_enforcement_flip():
    r = check_judge_postcondition(
        mode="judge",
        candidate="PHP security release claim",
        evidence=_EVIDENCE_WITH_UNKNOWN,
        verdict_str="HOLD",
        effective_verdict="HOLD",
    )
    # Annotated, not enforced: HOLD stays HOLD, missing_evidence untouched.
    assert r["applied"] is False
    assert "unwitnessed_evidence_items" not in r["missing_evidence"]


def test_seal_family_downgrades_on_unwitnessed_items():
    r = check_judge_postcondition(
        mode="judge",
        candidate="PHP security release claim",
        evidence=_EVIDENCE_WITH_UNKNOWN,
        verdict_str="SEAL",
        effective_verdict="SEAL",
    )
    assert "unwitnessed_evidence_items" in r["missing_evidence"]
    assert r["applied"] is True
    assert r["verdict"] == "SABAR"
    assert r["reason_code"] == "EVIDENCE_POSTCONDITION_VIOLATION"


def test_clean_evidence_seal_path_unchanged():
    r = check_judge_postcondition(
        mode="judge",
        candidate="PHP security release claim",
        evidence=_EVIDENCE_CLEAN,
        verdict_str="SEAL",
        effective_verdict="SEAL",
    )
    assert r["unwitnessed_evidence"] == []
    assert "unwitnessed_evidence_items" not in r["missing_evidence"]
    assert r["applied"] is False


def test_claim_class_key_also_recognised():
    r = check_judge_postcondition(
        mode="judge",
        candidate="c",
        evidence={"value": [{"fact": "x", "claim_class": "unknown"}]},
        verdict_str="HOLD",
        effective_verdict="HOLD",
    )
    assert r["unwitnessed_evidence"] and r["unwitnessed_evidence"][0]["field"] == "claim_class"
