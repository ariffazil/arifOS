from __future__ import annotations

from arifosmcp.runtime.context_safety import validate_interpretation_safety
from arifosmcp.runtime.quote_ledger import load_quote_ledger


def _candidate_quotes():
    ledger = load_quote_ledger()
    return [q for q in ledger if q["allow_use"] and q["source_status"] != "uncertain"][
        :3
    ]


def test_context_safety_rejects_unknown_quote_id() -> None:
    candidates = _candidate_quotes()
    interpretation = {
        "selected_quote_id": "UNKNOWN_ID",
        "meaning": "x",
        "interpretation": "y",
        "arifos_alignment": {"physics": "p", "math": "m", "linguistic": "l"},
        "decision_boundary": "None",
        "human_decision_required": True,
        "recommended_action": "HOLD",
        "uncertainty": [],
        "safety_notes": [],
    }
    safety = validate_interpretation_safety(
        interpretation, candidates, risk_level="high"
    )
    assert safety["status"] == "hold"
    assert safety["error_code"] == "quote_not_in_approved_ledger"


def test_context_safety_rejects_author_drift() -> None:
    candidates = _candidate_quotes()
    q = candidates[0]
    interpretation = {
        "selected_quote_id": q["id"],
        "quote": q["quote"],
        "author": q["author"] + " drift",
        "meaning": "x",
        "interpretation": "y",
        "arifos_alignment": {"physics": "p", "math": "m", "linguistic": "l"},
        "decision_boundary": "None",
        "human_decision_required": True,
        "recommended_action": "HOLD",
        "uncertainty": [],
        "safety_notes": [],
    }
    safety = validate_interpretation_safety(
        interpretation, candidates, risk_level="high"
    )
    assert safety["status"] == "hold"
    assert safety["error"] == "author_integrity_failed"
