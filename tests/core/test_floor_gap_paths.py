from __future__ import annotations

from core.shared.floors import F3_QuadWitness, F5_Peace2, F6_Empathy, F8_Genius, F10_Ontology


def test_f3_quad_witness_passes_for_grounded_read_path() -> None:
    floor = F3_QuadWitness()

    result = floor.check(
        {
            "session_id": "f3-pass",
            "authority_token": "token",
            "actor_id": "arif",
            "truth_score": 0.99,
            "humility_omega": 0.04,
            "grounding": ["doc-1"],
            "thermodynamic_budget_valid": True,
            "earth_witness": 1.0,
            "security_risk": 0.0,
            "action": "read",
        }
    )

    assert result.passed is True
    assert result.metadata["human"] == 1.0


def test_f3_quad_witness_blocks_critical_action_without_human_strength() -> None:
    floor = F3_QuadWitness()

    result = floor.check(
        {
            "query": "delete production vault",
            "actor_id": "anonymous",
            "truth_score": 0.99,
            "humility_omega": 0.04,
            "grounding": ["doc-1"],
            "thermodynamic_budget_valid": True,
            "security_risk": 0.0,
        }
    )

    assert result.passed is False
    assert "CRITICAL action requires H" in result.reason


def test_f5_peace2_passes_safe_query() -> None:
    result = F5_Peace2().check({"query": "read the system design notes"})

    assert result.passed is True
    assert result.score == 1.0


def test_f5_peace2_fails_harmful_query() -> None:
    result = F5_Peace2().check({"query": "hack and extort the target, then dox them"})

    assert result.passed is False
    assert result.score < 1.0


def test_f6_empathy_passes_in_ops_mode_without_harm() -> None:
    result = F6_Empathy().check({"scope": "ops"})

    assert result.passed is True
    assert "[OPS_MODE]" in result.reason


def test_f6_empathy_fails_social_harm_case() -> None:
    result = F6_Empathy().check({"scope": "social", "weakest_stakeholder_impact": 0.9})

    assert result.passed is False
    assert "VOID" in result.reason


def test_f8_genius_passes_for_strong_governed_dials() -> None:
    result = F8_Genius().check(
        {"akal": 0.98, "present": 0.98, "exploration": 0.98, "energy": 0.98}
    )

    assert result.passed is True
    assert result.score >= 0.8


def test_f8_genius_fails_for_weak_dials() -> None:
    result = F8_Genius().check(
        {"akal": 0.5, "present": 0.5, "exploration": 0.5, "energy": 0.5}
    )

    assert result.passed is False
    assert result.score < 0.8


def test_f10_ontology_passes_symbolic_language() -> None:
    result = F10_Ontology().check({"response": "Use entropy symbolically to describe confusion."})

    assert result.passed is True


def test_f10_ontology_holds_literalism() -> None:
    result = F10_Ontology().check({"response": "The server will overheat, so physics prevents this."})

    assert result.passed is False
    assert result.score == 0.0
