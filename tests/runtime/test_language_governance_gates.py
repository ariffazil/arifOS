from __future__ import annotations

from arifosmcp.runtime.authority_gate import enforce_authority_boundary
from arifosmcp.runtime.evidence_guard import enforce_evidence_guard
from arifosmcp.runtime.irreversibility_guard import enforce_irreversibility
from arifosmcp.runtime.trace_enforcer import enforce_trace
from arifosmcp.runtime.uncertainty_gate import enforce_uncertainty_gate


def test_authority_gate_blocks_missing_required_fields() -> None:
    result = enforce_authority_boundary({"generated_by": "instrument_model"})
    assert result.status == "HOLD"
    assert any(v.startswith("missing_required_field") for v in result.violations)


def test_authority_gate_blocks_authority_smuggling() -> None:
    payload = {
        "actor_id": "Arif",
        "authority_level": "HUMAN_SOVEREIGN",
        "trace_id": "TRACE-aeee7670f9da",
        "decision_class": "C2",
        "uncertainty_state": "PARTIAL",
        "generated_by": "instrument_model",
        "requires_human_ack": True,
    }
    result = enforce_authority_boundary(payload)
    assert result.status == "HOLD"
    assert "authority_smuggling:model_claimed_sovereign_authority" in result.violations


def test_evidence_guard_requires_review_for_unverified() -> None:
    claim = {
        "text": "No major integrity risk detected.",
        "evidence_state": "UNVERIFIED",
        "confidence": 0.61,
        "source_count": 2,
        "human_review_required": False,
    }
    result = enforce_evidence_guard(claim)
    assert result.status == "HOLD"
    assert "human_review_required_for_unverified_or_hypothetical_claim" in result.violations


def test_uncertainty_gate_requires_block_below_threshold() -> None:
    payload = {"confidence": 0.60}
    result = enforce_uncertainty_gate(payload)
    assert result.status == "HOLD"
    assert "uncertainty_block_required_below_confidence_threshold" in result.violations


def test_trace_enforcer_rejects_invalid_trace_format() -> None:
    payload = {
        "actor_id": "Arif",
        "trace_id": "bad-trace",
        "decision_class": "C2",
    }
    result = enforce_trace(payload)
    assert result.status == "HOLD"
    assert "invalid_trace_id_format" in result.violations


def test_irreversibility_guard_requires_explicit_ack() -> None:
    payload = {
        "domain": "INFRASTRUCTURE",
        "action": "deploy",
        "ack_irreversible": False,
    }
    result = enforce_irreversibility(payload)
    assert result.status == "HOLD"
    assert "rule_violation:NO_IRREVERSIBLE_ACTION_WITHOUT_EXPLICIT_HUMAN_ACK" in result.violations
