"""T3 + T6 regression (F13 A1 batch, ratified "all as recommended" 2026-09-22).

T3 — absence of attestation is UNMEASURED, never FAILED:
    pre-fix: record=None → is_healthy("UNATTESTED")=False →
             session_authority_state=BOOT_ATTESTATION_FAILED +
             substrate_state=DEGRADED, for a measurement that never happened.
    post-fix: boot_gate_state() returns ("UNATTESTED", False); the envelope
             carries MUST_ATTEST (honest gap) and does not degrade substrate.
    Live witness pre-fix (OBS 2026-09-22 ~21:20 MYT):
        result.effective_state.session_authority_state = 'BOOT_ATTESTATION_FAILED'

T6 — verdict floor-guard (thresholds canon-grounded, not invented):
    W3 < 0.75 → HOLD band   — APEX-REALITY-KERNEL.md L154 +
                              W3-HYSTERESIS-DOCTRINE-2026-09-20
    G  < 0.80 → F08 breach  — CANON-FLOOR-INDEX-2026-09-20
    Live witness pre-fix: thermodynamic.verdict=SEAL beside G=0.4649,
    W3=0.7439 — one payload, two truths.

DITEMPA BUKAN DIBERI.
"""

from __future__ import annotations

from pathlib import Path

from arifosmcp.runtime import organ_attestation as oa

REPO = Path(__file__).resolve().parents[1]


# ── T3 ──────────────────────────────────────────────────────────────────────


def test_absence_of_attestation_does_not_block():
    """Empty registry → UNMEASURED, not FAILED (the T3 defect)."""
    saved = dict(oa._ORGAN_REGISTRY)
    try:
        oa._ORGAN_REGISTRY.clear()
        status, blocks = oa.boot_gate_state("arifOS")
        assert status == "UNATTESTED"
        assert blocks is False
    finally:
        oa._ORGAN_REGISTRY.clear()
        oa._ORGAN_REGISTRY.update(saved)


def test_unhealthy_record_still_blocks():
    """A genuinely unhealthy attestation must still gate (refuse-on-FAIL)."""
    saved = dict(oa._ORGAN_REGISTRY)
    try:
        oa._ORGAN_REGISTRY["arifOS"] = oa.OrganAttestationRecord(
            organ_id="arifOS", role="constitutional_kernel", version="test",
            tool_count=0, schema_hash="x", constitution_hash="y",
            identity_anchor_type="constitution_hash", identity_anchor_hash="z",
            status="DEGRADED",
        )
        status, blocks = oa.boot_gate_state("arifOS")
        assert status == "DEGRADED"
        assert blocks is True
    finally:
        oa._ORGAN_REGISTRY.clear()
        oa._ORGAN_REGISTRY.update(saved)


def test_healthy_record_passes():
    saved = dict(oa._ORGAN_REGISTRY)
    try:
        oa._ORGAN_REGISTRY["arifOS"] = oa.OrganAttestationRecord(
            organ_id="arifOS", role="constitutional_kernel", version="test",
            tool_count=0, schema_hash="x", constitution_hash="y",
            identity_anchor_type="constitution_hash", identity_anchor_hash="z",
            status="ALIVE",
        )
        status, blocks = oa.boot_gate_state("arifOS")
        assert status == "ALIVE"
        assert blocks is False
    finally:
        oa._ORGAN_REGISTRY.clear()
        oa._ORGAN_REGISTRY.update(saved)


def test_session_envelope_uses_the_new_gate():
    """The envelope consumer must route through boot_gate_state + MUST_ATTEST."""
    src = (REPO / "arifosmcp/tools/session.py").read_text()
    assert "boot_gate_state" in src, "session.py still runs the old is_healthy-absence path"
    assert '"MUST_ATTEST"' in src, "absence has no honest label in the ternary chain"


# ── T6 ──────────────────────────────────────────────────────────────────────


def test_t6_floor_guard_present_and_canon_grounded():
    """The guard exists in the /health route and cites canon, not the paste."""
    src = (REPO / "arifosmcp/runtime/rest_routes/rest_routes.py").read_text()
    assert "T6 verdict floor-guard" in src
    assert "APEX-REALITY-KERNEL.md" in src, "W3 threshold must cite its canon source"
    assert "CANON-FLOOR-INDEX-2026-09-20" in src, "G threshold must cite its canon source"
    # guard runs BEFORE the cache store so cached and live payloads agree
    guard_at = src.index("T6 verdict floor-guard")
    cache_at = src.index('_health_cache["payload"] = payload', guard_at)
    assert guard_at < cache_at, "guard must run before cache store"


def test_boot_seeder_registered_at_startup():
    src = (REPO / "arifosmcp/runtime/__main__.py").read_text()
    assert "organ-attest-seed" in src, "T3 boot seeder thread missing from main()"


# ── self_bridge (the phantom module the config always declared) ─────────────


def test_self_bridge_exists_and_is_the_configured_module():
    """SEMANTIC_AUTHORITY: NAME ∩ CALL_PATH — the configured module resolves."""
    import importlib

    mod = importlib.import_module("arifosmcp.runtime.self_bridge")
    assert callable(getattr(mod, "arifos_health_check"))
    assert callable(getattr(mod, "list_arifos_tools"))


def test_self_bridge_health_is_real_not_constant_green():
    from arifosmcp.runtime.self_bridge import arifos_health_check

    h = arifos_health_check()
    assert h["status"] in ("healthy", "degraded")
    assert h["failures"] == [], f"unexpected failures: {h['failures']}"
    assert h["status"] == "healthy"
    assert h["floors_active"] == 13
    assert h["version"] not in ("", None)
    assert h["source_commit"] not in ("", "unknown")


def test_self_bridge_tools_nonempty():
    from arifosmcp.runtime.self_bridge import list_arifos_tools

    tools = list_arifos_tools()
    assert tools, "empty tool surface would push attestation into PARTIAL_DEGRADED"
    assert all("name" in t for t in tools)


def test_end_to_end_attest_arifos_is_alive():
    """The full T3 path: attest_organ('arifOS') must produce a passing record."""
    import asyncio

    from arifosmcp.runtime import organ_attestation as oa

    asyncio.run(oa.attest_organ("arifOS"))
    rec = oa.get_organ_attestation("arifOS")
    assert rec is not None, "attest_organ wrote no record"
    assert rec.status == "ALIVE", f"expected ALIVE, got {rec.status} ({rec.reason})"
    assert oa.boot_gate_state("arifOS") == ("ALIVE", False)


if __name__ == "__main__":  # pragma: no cover
    import pytest

    raise SystemExit(pytest.main([__file__, "-v"]))
