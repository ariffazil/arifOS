"""Session Policy Clamp — unit + integration tests (Shadow Mode runtime binding).

Forged 2026-08-15. F13 "Go" on: display registers must be kernel state, not prompt.
"""
import sys

sys.path.insert(0, "/root/arifOS")

from arifosmcp.runtime.session_policy import (  # noqa: E402
    _RANK,
    _semantic_clamp,
    _self_check,
    session_policy_clamp,
)

SHADOW = {
    "agent_role": "hermes-shadow",
    "display_register": "shadow",
    "allowed_tools": ["arif_init", "arif_observe", "arif_think", "arif_route", "arif_memory"],
    "denied_tools": ["arif_seal", "arif_forge"],
    "irreversibility_threshold": 0.0,
    "policy_version": "1.0.0-shadow",
}


def test_semantic_ceiling():
    # shadow register blocks mutation-class and above
    assert _semantic_clamp(SHADOW, "arif_think", "MUTATE") is True
    assert _semantic_clamp(SHADOW, "arif_forge", "EXTERNAL_SIDE_EFFECT") is True
    assert _semantic_clamp(SHADOW, "arif_seal", "IRREVERSIBLE") is True
    # observe/analyze/draft/simulate pass the ceiling
    assert _semantic_clamp(SHADOW, "arif_observe", "OBSERVE") is False
    assert _semantic_clamp(SHADOW, "arif_think", "ANALYZE") is False
    assert _semantic_clamp(SHADOW, "arif_think", "DRAFT") is False
    assert _semantic_clamp(SHADOW, "arif_think", "SIMULATE") is False


def test_semantic_tool_lists():
    # explicit deny wins even for observe-class
    assert _semantic_clamp(SHADOW, "arif_seal", "OBSERVE") is True
    # not in allow-list
    assert _semantic_clamp(SHADOW, "arif_judge", "OBSERVE") is True
    # in allow-list
    assert _semantic_clamp(SHADOW, "arif_memory", "OBSERVE") is False


def test_semantic_no_policy():
    assert _semantic_clamp(None, "arif_forge", "MUTATE") is False
    assert _semantic_clamp({}, "arif_forge", "MUTATE") is False


def test_semantic_threshold():
    # MUTATE rank 4/6 ≈ 0.667 > 0.5 → clamp
    assert _semantic_clamp({"irreversibility_threshold": 0.5}, "arif_forge", "MUTATE") is True
    # threshold 0.9 permits MUTATE
    assert _semantic_clamp({"irreversibility_threshold": 0.9}, "arif_forge", "MUTATE") is False
    # observe never hits the threshold ladder
    assert _semantic_clamp({"irreversibility_threshold": 0.0}, "arif_observe", "OBSERVE") is False


def test_module_self_check():
    r = _self_check()
    assert r["verdict"] == "OK", r


def test_live_clamp_reads_session_store():
    """Integration: bind a fake session in the identity store, verify the
    live clamp finds it and enforces the policy."""
    from arifosmcp.runtime.session import bind_session_identity

    sid = "TEST-SHADOW-CLAMP-001"
    bind_session_identity(
        session_id=sid,
        actor_id="hermes",
        authority_level="OBSERVE_ONLY",
        auth_context={"source": "test"},
        agent_policy=dict(SHADOW),
    )
    # MUTATE under shadow → clamped
    c1 = session_policy_clamp(sid, "arif_think", "MUTATE")
    assert c1 is not None and "shadow" in c1["reason"].lower(), c1
    # OBSERVE allowed tool → passes
    c2 = session_policy_clamp(sid, "arif_observe", "OBSERVE")
    assert c2 is None, c2
    # denied tool even at OBSERVE → clamped
    c3 = session_policy_clamp(sid, "arif_seal", "OBSERVE")
    assert c3 is not None and "denied" in c3["reason"].lower(), c3


def test_live_clamp_unknown_session():
    # unknown session → no policy opinion (main gate still applies)
    assert session_policy_clamp("NO-SUCH-SESSION", "arif_forge", "MUTATE") is None


def test_live_clamp_init_exempt():
    from arifosmcp.runtime.session import bind_session_identity

    sid = "TEST-SHADOW-CLAMP-002"
    bind_session_identity(
        session_id=sid,
        actor_id="hermes",
        authority_level="OBSERVE_ONLY",
        auth_context={"source": "test"},
        agent_policy=dict(SHADOW),
    )
    # arif_init is ignition-exempt: a shadow session can always re-init/inspect
    assert session_policy_clamp(sid, "arif_init", "OBSERVE") is None


if __name__ == "__main__":
    failures = 0
    for name, fn in sorted(globals().items()):
        if name.startswith("test_") and callable(fn):
            try:
                fn()
                print(f"PASS {name}")
            except AssertionError as e:
                failures += 1
                print(f"FAIL {name}: {e}")
    print("RANK MAP:", _RANK)
    sys.exit(1 if failures else 0)
