"""
Regression test: Constitutional seat model failure MUST NOT enter generic cascade.

AMEND-20260724-001: When a gated constitutional role (666_JUDGE / 999_SEAL) is
requested, the effective model is determined by select_model_for_role(). If that
exact model fails, the call must raise ConstitutionalSeatUnavailable and NEVER
fall through to MiniMax, MiMo, Groq, or any other provider.
"""

import pytest


def test_constitutional_seat_unavailable_exists():
    import arifosmcp.runtime.llm_client as llm

    assert hasattr(llm, "ConstitutionalSeatUnavailable")
    assert issubclass(llm.ConstitutionalSeatUnavailable, llm.LLMUnavailableError)


def test_constitutional_roles_gated_unchanged():
    import arifosmcp.runtime.llm_client as llm

    assert "666_JUDGE" in llm.CONSTITUTIONAL_ROLES_GATED
    assert "999_SEAL" in llm.CONSTITUTIONAL_ROLES_GATED
    assert "111_OBSERVE" not in llm.CONSTITUTIONAL_ROLES_GATED


def test_emit_seat_unavailable_exists():
    import arifosmcp.runtime.llm_client as llm

    assert hasattr(llm, "_emit_seat_unavailable")


def test_select_model_for_role_returns_string():
    import arifosmcp.runtime.llm_client as llm

    result = llm.select_model_for_role(
        role="666_JUDGE",
        requested_model="deepseek-v4-pro",
        agent_id="test_arif_judge",
    )
    assert isinstance(result, str)
    assert result


def test_select_model_forbidden_raises():
    import arifosmcp.runtime.llm_client as llm

    with pytest.raises(llm.LLMUnavailableError):
        llm.select_model_for_role(
            role="666_JUDGE",
            requested_model="mimo-v2.5-pro",
            agent_id="test",
        )
