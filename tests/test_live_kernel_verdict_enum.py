"""Regression: live-kernel envelope emits ONLY canonical verdict tokens.

F13-ratified 5-state lattice (contracts/arifos_live_kernel_envelope.v1.json,
D6 2026-07-31): SEAL > PARTIAL > SABAR > HOLD > VOID. DEGRADED / DENY are
DEPRECATED aliases. Defect observed live 2026-10-13/14: envelope emitted
``verdict=DEGRADED`` (a STATE, not a verdict) which downstream reconciliation
flagged as NONCANONICAL_VERDICT_TOKEN and mapped to SABAR — producing the
three-way HOLD/SABAR/DEGRADED split in a single response.

Contract after fix:
  - intake maps DEGRADED -> SABAR, DENY -> VOID (deprecated alias, gone at source)
  - risk posture of the DEGRADED alias is preserved (MEDIUM / 0.5) WITHOUT
    contaminating genuine SABAR responses (LOW / 1.0)
  - unknown tokens still coerce to OBSERVE_ONLY (unchanged behavior)
"""

from __future__ import annotations

from arifosmcp.runtime.live_kernel import build_kernel_envelope


def _envelope(response: dict) -> dict:
    env = build_kernel_envelope(tool_name="probe_test", response=response)
    return env.model_dump(mode="json") if hasattr(env, "model_dump") else dict(env)


def test_degraded_alias_maps_to_sabar_keeps_risk_posture():
    out = _envelope({"verdict": "DEGRADED", "status": "DEGRADED"})
    assert out["verdict"] == "SABAR", "DEGRADED must never survive intake (D6 enum)"
    assert out["risk"]["blast_radius"] == "MEDIUM"
    assert out["risk"]["reversibility_score"] == 0.5


def test_deny_alias_maps_to_void():
    out = _envelope({"verdict": "DENY"})
    assert out["verdict"] == "VOID"
    assert out["risk"]["blast_radius"] == "MEDIUM"
    assert out["risk"]["reversibility_score"] == 0.0


def test_genuine_sabar_keeps_low_risk():
    """A real SABAR (patience) response is NOT the degraded alias."""
    out = _envelope({"verdict": "SABAR"})
    assert out["verdict"] == "SABAR"
    assert out["risk"]["blast_radius"] == "LOW"
    assert out["risk"]["reversibility_score"] == 1.0


def test_canonical_tokens_pass_through():
    for token in ("SEAL", "PARTIAL", "SABAR", "HOLD", "VOID"):
        assert _envelope({"verdict": token})["verdict"] == token


def test_unknown_token_still_coerces_observe_only():
    assert _envelope({"verdict": "SUPER_ENGINE_MODE"})["verdict"] == "OBSERVE_ONLY"


def test_default_fallback_unchanged():
    assert _envelope({})["verdict"] == "OBSERVE_ONLY"
