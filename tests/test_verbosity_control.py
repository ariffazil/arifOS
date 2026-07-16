from __future__ import annotations

import inspect
import json

from arifosmcp.runtime.tools import _arif_session_init
from arifosmcp.runtime.verbosity import trim_for_verbosity


def _full_response() -> dict:
    return {
        "status": "OK",
        "tool": "arif_init",
        "verdict": "SEAL",
        "actor_id": "arif",
        "actor_verified": True,
        "actor": {"claimed_id": "arif", "authority_level": "SOVEREIGN"},
        "session_id": "SEAL-test",
        "call_hash": "sha256:test",
        "trace_id": "trace-test",
        "signature": "sig-test",
        "result": {"next_safe_action": "Call arif_observe", "large": "x" * 8000},
        "constitution": {"large": "x" * 8000},
    }


def test_arif_init_exposes_bounded_verbosity_schema() -> None:
    parameter = inspect.signature(_arif_session_init).parameters["verbosity"]
    assert parameter.default == "standard"
    assert "minimal" in str(parameter.annotation)
    assert "standard" in str(parameter.annotation)
    assert "full" in str(parameter.annotation)


def test_minimal_is_small_and_keeps_acceptance_fields() -> None:
    minimal = trim_for_verbosity(_full_response(), "minimal")
    assert len(json.dumps(minimal).split()) <= 500
    assert minimal["verdict"] == "SEAL"
    assert minimal["session_id"] == "SEAL-test"
    assert minimal["actor"]["actor_id"] == "arif"
    assert minimal["call_hash"] == "sha256:test"
    assert minimal["next_safe_action"] == "Call arif_observe"


def test_standard_and_full_preserve_current_response() -> None:
    response = _full_response()
    assert trim_for_verbosity(response, "standard") is response
    assert trim_for_verbosity(response, "full") is response
