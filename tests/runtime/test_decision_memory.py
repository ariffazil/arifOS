import pytest
from pydantic import ValidationError

from arifosmcp.runtime.decision_memory import (
    activation_changes,
    decayed_confidence,
    lifecycle_recommendation,
    predicted_value,
    record_outcome,
    record_retrieval,
    should_retrieve,
)
from arifosmcp.schemas.memory_object import MemoryAuthorityBlock


@pytest.mark.asyncio
async def test_remember_persists_decision_value_metadata(monkeypatch):
    from arifosmcp.runtime import memory_handlers_v5, memory_store

    captured = {}

    async def fake_pg_write(**kwargs):
        captured.update(kwargs)
        return True

    monkeypatch.setattr(memory_store, "_pg_write", fake_pg_write)
    result = await memory_handlers_v5._handle_remember(
        {
            "content": "Repeated tool failure predicts scope drift.",
            "memory_class": "episodic",
            "truth_class": {"status": "observed", "confidence": 0.9},
            "provenance": {"actor_id": "tester", "session_id": "s1"},
            "tier_hint": "L3",
            "future_value": VALUE,
            "authority": {"may_restrict_tools": True, "may_expand_tools": False},
        },
        ctx=None,
    )

    assert result["verdict"] == "SEAL"
    assert captured["metadata"]["schema_version"] == 6
    assert captured["metadata"]["future_value"] == VALUE
    assert captured["metadata"]["authority"]["may_restrict_tools"] is True
    assert result["payload"]["predicted_decision_value"] > 0.55


VALUE = {
    "recurrence_probability": 0.9,
    "decision_impact": 0.9,
    "evidence_reliability": 0.9,
    "retrieval_specificity": 0.9,
    "maintenance_cost": 0.02,
    "privacy_risk": 0.01,
    "misapplication_risk": 0.01,
}


def test_high_value_requires_verified_use_before_promotion():
    assert predicted_value(VALUE) > 0.55
    assert lifecycle_recommendation(VALUE) == "temporary"
    assert lifecycle_recommendation(VALUE, verified_useful_outcomes=1) == "eligible_for_promotion"


def test_risk_can_inhibit_retrieval():
    risky = {**VALUE, "staleness_risk": 0.5, "anchoring_risk": 0.5}
    assert should_retrieve(risky) is False


def test_memory_can_restrict_but_cannot_expand_authority():
    changes = activation_changes({"may_restrict_tools": True, "may_lower_autonomy": True})
    assert changes["tool_policy"] == "restrict_only"
    assert changes["authority_expansion_allowed"] is False
    with pytest.raises(ValidationError):
        MemoryAuthorityBlock(may_expand_tools=True)
    with pytest.raises(ValidationError):
        MemoryAuthorityBlock(may_raise_autonomy=True)


def test_usage_and_outcome_require_verified_evidence(monkeypatch, tmp_path):
    path = tmp_path / "events.jsonl"
    monkeypatch.setenv("ARIFOS_MEMORY_VALUE_LEDGER", str(path))
    record_retrieval("mem-1", "decision-1", "matched failure pattern")
    result = record_outcome("mem-1", "decision-1", verified=True, useful=True)
    verified = record_outcome(
        "mem-1", "decision-1", verified=True, useful=True, evidence_refs=["test-1"]
    )
    assert result["status"] == "UNVERIFIED"
    assert verified["status"] == "USEFUL"
    assert len(path.read_text().splitlines()) == 3


def test_confidence_decays_without_rewriting_history():
    assert decayed_confidence(0.8, months_elapsed=2, decay_per_month=0.05) == 0.7
