"""C3 Federation Receipt Proof: request-scoped session isolation."""

from __future__ import annotations

import time
from dataclasses import dataclass
from unittest.mock import patch

import pytest


@dataclass
class _InvalidStanding:
    valid: bool = False


def test_validate_session_never_inherits_environment(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setenv("ARIFOS_SESSION_ID", "c3-live-valid-probe")
    monkeypatch.setenv("ARIFOS_ACTOR_ID", "previous-test-actor")
    monkeypatch.setattr(
        "arifosmcp.runtime.sct.resolve_standing",
        lambda **_: _InvalidStanding(),
    )

    from arifosmcp.runtime.session_auth import validate_session

    result = validate_session(None, None)

    assert result["valid"] is False
    assert result["reason"] == "L11 AUTH: session_id missing"
    assert "c3-live-valid-probe" not in str(result)
    assert "previous-test-actor" not in str(result)


@pytest.mark.parametrize("actor_variant", ["ARIF", "Arif", "arif"])
def test_valid_session_actor_spelling_normalizes(
    monkeypatch: pytest.MonkeyPatch,
    actor_variant: str,
) -> None:
    monkeypatch.setattr(
        "arifosmcp.runtime.sct.resolve_standing",
        lambda **_: _InvalidStanding(),
    )

    from arifosmcp.runtime.session_auth import validate_session
    session_id = "SEAL-c3-case-normalization"
    sessions = {
        session_id: {
            "session_id": session_id,
            "actor_id": "arif",
            "signature_verified": True,
            "created_at_unix": time.time(),
            "expires_at_unix": time.time() + 600,
            "stage": "000",
        }
    }

    with patch("arifosmcp.runtime.tools._SESSIONS", sessions):
        result = validate_session(session_id, actor_variant)

    assert result["valid"] is True
    assert result["actor_id"] == "arif"


def test_schema_adapter_does_not_inject_previous_session() -> None:
    from arifosmcp.runtime.schema_adapter import get_session_state, prepare_call

    state = get_session_state()
    state.activate("c3-live-valid-probe", "previous-test-actor")
    try:
        prepared = prepare_call("arif_think", {"query": "isolated probe"})
    finally:
        state.clear()

    assert "session_id" not in prepared
    assert "actor_id" not in prepared


def test_schema_adapter_requires_explicit_session() -> None:
    from arifosmcp.runtime.schema_adapter import SchemaAdapterError, get_session_state, prepare_call

    state = get_session_state()
    state.activate("c3-live-valid-probe", "previous-test-actor")
    try:
        with pytest.raises(SchemaAdapterError):
            prepare_call("arif_judge", {"query": "isolated probe"}, require_session=True)
    finally:
        state.clear()
