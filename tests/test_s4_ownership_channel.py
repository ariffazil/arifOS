"""S4-OWNERSHIP — RED phase for OUT-OF-BAND OWNERSHIP v1.

Design: /root/forge_work/2026-10-26-FI-003-verdict-ownership-design.md
Basis : arifOS@6fbff1996 — reconcile_decision_contract has no `owned` parameter.

This file is SEPARATE from tests/test_s4_verdict_channel.py on purpose: that suite
pins ratified behaviour (F13 FIX-S4, M1-M5, R-1b/R-1d, transport carve-outs) and
must not be rewritten by a design that is not yet approved.

Two classes here:

  BASELINE (9) — behaviour that exists today. GREEN now, must stay green after.
                 Includes the transport carve-outs that this design must NOT reopen.
  CAPABILITY (9) — requires OwnedField / owned. RED now, by design.

Run:
    .venv/bin/pytest tests/test_s4_ownership_channel.py -q
"""
from __future__ import annotations

import pytest

from arifosmcp.runtime.verdict import _iter_verdict_bearing, reconcile_decision_contract


# ── helpers ────────────────────────────────────────────────────────────────

def _api():
    from arifosmcp.runtime import verdict as V

    missing = [n for n in ("OwnedField", "_value_token", "_is_owned") if not hasattr(V, n)]
    if missing:
        pytest.fail(f"DESIGN_NOT_IMPLEMENTED: verdict.py lacks {missing}")
    return V


def _walk(V, node, owned=None):
    if owned is None:
        pairs = list(V._iter_verdict_bearing(node))
    else:
        try:
            pairs = list(V._iter_verdict_bearing(node, root_id=id(node), owned=owned))
        except TypeError as exc:
            pytest.fail(
                f"DESIGN_NOT_IMPLEMENTED: _iter_verdict_bearing lacks root_id/owned ({exc})"
            )
    return dict(pairs)


def _field(V, node, path, value):
    return V.OwnedField(id(node), path, V._value_token(value))


def _flags(out):
    return ((out.get("meta") or {}).get("reconciliation") or {}).get("flags") or []


def _builder():
    from arifosmcp.runtime import tools as T

    fn = getattr(T, "_attach_v2_envelope_guarantee", None)
    if fn is None:
        pytest.fail(
            "DESIGN_NOT_IMPLEMENTED: _attach_v2_envelope_guarantee is a nested function in "
            "tools.py; hoist it to module level so it can return an ownership set"
        )
    return fn


# ── BASELINE (green today; the regression fence) ───────────────────────────

def test_b1_root_verdict_is_walked():
    assert "verdict" in dict(_iter_verdict_bearing({"verdict": "SEAL"}))


def test_b2_root_effective_verdict_is_walked():
    assert "effective_verdict" in dict(_iter_verdict_bearing({"effective_verdict": "SEAL"}))


def test_b3_wrapped_payload_verdict_is_walked():
    assert "result.payload.verdict" in dict(
        _iter_verdict_bearing({"result": {"payload": {"verdict": "SEAL"}}})
    )


def test_b4_double_wrapped_result_is_carved_out():
    """Carve-out (2026-10-05, FI-008 bridge collision): the route bridge embeds a
    bridged organ's payload verbatim at `result.result`; a domain "PASS" there is
    the organ's own check, not a kernel verdict. Pinned so the ownership design
    cannot silently re-open it. (The design's original case 10 assumed no wildcard
    existed here — it does.)
    """
    assert "result.result.verdict" not in dict(
        _iter_verdict_bearing({"result": {"result": {"verdict": "SEAL"}}})
    )


def test_b5_reconcile_is_idempotent_without_owned():
    base = {"verdict": "SEAL", "effective_verdict": "SABAR"}
    once = reconcile_decision_contract(dict(base))
    twice = reconcile_decision_contract(dict(once))
    assert once == twice


def test_b6_reconcile_judges_a_disagreement():
    out = reconcile_decision_contract({"verdict": "SEAL", "effective_verdict": "SABAR"})
    rec = (out.get("meta") or {}).get("reconciliation") or {}
    assert out.get("effective_verdict") == "HOLD" or rec, (
        "a disagreement must be judged to HOLD and/or recorded in meta.reconciliation"
    )


def test_b7_transport_carveout_root_canonical_verdict_untouched():
    """M5 (live 2026-10-25): canonical_verdict is the public projection
    (PROCEED/DENY), NOT an independent claim. The ownership design must not
    reopen this carve-out."""
    out = reconcile_decision_contract(
        {"status": "completed", "verdict": "HOLD", "effective_verdict": "HOLD",
         "canonical_verdict": "DENY"}
    )
    assert not any(f.startswith("UNKNOWN_VERDICT_TOKEN") for f in _flags(out)), _flags(out)
    assert out.get("effective_verdict") == "HOLD"


def test_b8_transport_carveout_nested_trace_state_untouched():
    """M5 nested (live 2026-10-25, arif_init triage): the v2 envelope republishes
    the projection inside intermediate_trace_states; that copy is also carved out."""
    out = reconcile_decision_contract(
        {"status": "completed", "verdict": "SEAL", "effective_verdict": "SEAL",
         "result": {"intermediate_trace_states": {"canonical_verdict": "PROCEED"}}}
    )
    assert not any(f.startswith("UNKNOWN_VERDICT_TOKEN") for f in _flags(out)), _flags(out)


def test_b9_nested_organ_canonical_verdict_still_judged():
    """The carve-out is path-scoped: an organ claim wearing canonical_verdict
    under a neutral parent still fails closed."""
    out = reconcile_decision_contract(
        {"effective_verdict": "SEAL", "result": {"payload": {"canonical_verdict": "DENY"}}}
    )
    assert any(
        f.startswith("UNKNOWN_VERDICT_TOKEN:result.payload.canonical_verdict")
        for f in _flags(out)
    ), _flags(out)
    assert out.get("effective_verdict") == "HOLD"


# ── CAPABILITY (red until the design lands) ────────────────────────────────

def test_n1_owned_root_verdict_is_exempt():
    V = _api()
    node = {"verdict": "SABAR"}
    got = _walk(V, node, frozenset({_field(V, node, "verdict", "SABAR")}))
    assert "verdict" not in got, "I1/I2: what the builder wrote is exempt"


def test_n2_owned_wrapped_field_is_exempt():
    V = _api()
    node = {"result": {"payload": {"verdict": "SABAR"}}}
    owned = frozenset({_field(V, node, "result.payload.verdict", "SABAR")})
    assert "result.payload.verdict" not in _walk(V, node, owned)


def test_n3_forged_field_beside_owned_field_is_judged():
    V = _api()
    node = {"verdict": "SABAR", "effective_verdict": "SABAR"}
    owned = frozenset({_field(V, node, "verdict", "SABAR")})
    got = _walk(V, node, owned)
    assert "effective_verdict" in got, "I5: effective_verdict is never exempt"


def test_n4_preexisting_key_grants_no_ownership():
    V = _api()
    build = _builder()
    node = {"canonical_verdict": "VOID"}
    owned = build(node, "arif_think")
    paths = {f.path for f in owned}
    assert "canonical_verdict" not in paths, "I1: a setdefault no-op confers nothing"
    assert node["canonical_verdict"] == "VOID", "builder must not overwrite an organ field"


def test_n5_owned_ghost_path_is_ignored():
    V = _api()
    node = {"verdict": "SABAR"}
    owned = frozenset({_field(V, node, "ghost.verdict", "SABAR")})
    assert "verdict" in _walk(V, node, owned), "a stale owned path must not exempt others"


def test_n6_same_path_different_value_is_judged():
    V = _api()
    node = {"verdict": "HOLD"}
    owned = frozenset({_field(V, node, "verdict", "SABAR")})
    assert "verdict" in _walk(V, node, owned), "I2: the value token is part of the binding"


def test_n7_effective_verdict_under_exempt_parent_is_judged():
    V = _api()
    node = {"payload": {"effective_verdict": "SABAR"}}
    owned = frozenset({_field(V, node, "payload", node["payload"])})
    assert "payload.effective_verdict" in _walk(V, node, owned), "I5 at any depth"


def test_n8_set_is_void_after_a_later_layer_rewrites_the_value():
    V = _api()
    node = {"effective_verdict": "SABAR"}
    owned = frozenset({_field(V, node, "effective_verdict", "SABAR")})
    node["effective_verdict"] = "HOLD"          # simulated server.py:1267 rewrite
    assert "effective_verdict" in _walk(V, node, owned), "I7: stale set must not exempt"


def test_n9_parent_ownership_does_not_cover_a_child_key():
    V = _api()
    node = {"stage": {"verdict": "SABAR"}}
    owned = frozenset({_field(V, node, "stage", node["stage"])})
    assert "stage.verdict" in _walk(V, node, owned), (
        "I6: owning a parent dict does not own a child the builder never wrote"
    )