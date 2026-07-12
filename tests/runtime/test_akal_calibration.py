from __future__ import annotations

import asyncio

from arifosmcp.core.akal import FrictionLevel, FrictionResult, tag_novelty
from arifosmcp.core.akal_wiring import (
    akal_pre_seal,
    akal_pre_think,
    clear_akal_state,
    get_akal_state,
)
from arifosmcp.tools.embodied_instances.arif_think_embodied import ArifMindReasonEmbodied


def test_structural_complexity_boosts_friction_without_keyword_dependence() -> None:
    simple = akal_pre_think("Summarize this note.")
    complex_query = (
        "Compare the two rollout paths, weigh reversibility against timeline risk, "
        "and explain what changes if we delay one step while keeping the dependency chain intact."
    )
    complex_result = akal_pre_think(complex_query)

    assert complex_result["friction_score"] > simple["friction_score"]


def test_tag_novelty_accepts_plain_text_input() -> None:
    result = tag_novelty(
        "This means the current signals combine into one operating picture. "
        "The key insight is that the second path reduces rollback cost."
    )

    assert result.novelty_pass is True
    assert result.synthesized_ratio > 0
    assert result.chunks


def test_embodied_reasoning_propagates_akal_escalation_metadata(monkeypatch) -> None:
    monkeypatch.setattr(
        "arifosmcp.core.akal_wiring.akal_pre_think",
        lambda *_args, **_kwargs: {
            "friction_score": 0.91,
            "friction_level": "critical",
            "escalation_required": True,
            "required_depth": "full_ascent",
            "required_pipeline": ["333_MIND", "555_HEART", "888_JUDGE"],
            "reasons": ["high structural complexity"],
            "present_state": {"evidence_class": "query", "grounded": True},
            "present_epistemic": {"reality_class": "OBSERVED"},
        },
    )
    monkeypatch.setattr(
        "arifosmcp.runtime.tools._arif_mind_reason",
        lambda **_kwargs: {"answer": "ok"},
    )

    result = asyncio.run(
        ArifMindReasonEmbodied().execute(
            {"mode": "reason", "query": "complex routing case", "session_id": "s1"},
            ctx=None,
        )
    )

    assert result["akal"]["escalation_recommended"] is True
    assert result["akal"]["recommended_pipeline"] == ["333_MIND", "555_HEART", "888_JUDGE"]
    assert result["akal"]["friction"]["friction_level"] == "critical"
    assert result["akal"]["friction"]["present_epistemic"]["reality_class"] == "OBSERVED"


def test_pre_seal_uses_real_cost_gate() -> None:
    session_id = "akal-cost-gate"
    try:
        akal_pre_think(
            "Compare four branching execution paths, reconcile competing constraints, "
            "and justify the irreversible choice across multiple dependencies.",
            session_id=session_id,
        )
        state = get_akal_state(session_id)
        state.friction = FrictionResult(
            score=0.9,
            level=FrictionLevel.CRITICAL,
            signals={},
            escalation_required=True,
            required_depth="full_ascent",
        )

        result = akal_pre_seal(
            session_id=session_id,
            blast_radius="high",
            passes_completed=20,
            branches_explored=20,
            cooling_elapsed=60,
        )

        assert result["proceed"] is False
        assert "cost" in result["reason"].lower()
        assert result["energy_state"]["cost_checked"] is True
        assert result["energy_state"]["cost_gate_pass"] is False
        assert result["energy_state"]["cost_usd"] > 1.0
    finally:
        clear_akal_state(session_id)
