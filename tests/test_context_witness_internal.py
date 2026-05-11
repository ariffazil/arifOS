from __future__ import annotations

from arifosmcp.runtime.tools import _ok


def test_context_witness_emits_when_requested() -> None:
    result = _ok(
        "arif_reply_compose",
        {"message": "ready"},
        meta={
            "emit_context_witness": True,
            "risk_level": "high",
            "audience": "human",
            "domain": "governance",
            "context_event": "Agent wants to deploy without approval.",
            "context_state": {"deployment_ready": True, "approval_record": None},
            "context_judgment": {"risk": "high"},
        },
    )

    witness = result["meta"].get("context_witness")
    assert witness is not None
    assert witness["human_decision_required"] is True
    assert "recommended_action" in witness


def test_context_witness_not_emitted_for_low_risk_machine_path() -> None:
    result = _ok(
        "arif_reply_compose",
        {"message": "ready"},
        meta={"risk_level": "low", "audience": "machine", "domain": "ops"},
    )

    assert "context_witness" not in result["meta"]
