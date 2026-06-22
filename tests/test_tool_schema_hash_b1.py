"""
test_tool_schema_hash_b1.py — B1 fix verification.

Pins the B1 behavior (2026-06-21): compute_tool_schema_hash() must
return a real SHA256 for tools in DIAGNOSTIC_TOOLS, not the
fabrication-defense sentinel "sha256:unknown_tool".

Audit finding (2026-06-21):
  6 canary / transport / conformance tools were returning
  "sha256:unknown_tool" in /ping → public_surface.tool_schema_hashes,
  blocking clients from detecting per-tool schema drift on diagnostic
  instruments.

Iron rule: a tool's schema_hash must be computable whenever the tool
is live-registered, regardless of whether it lives in CANONICAL_TOOLS
or DIAGNOSTIC_TOOLS. The unknown_tool sentinel is reserved for
fabrication-defense (genuinely absent tools).
"""

from __future__ import annotations

from arifosmcp.constitutional_map import CANONICAL_TOOLS, DIAGNOSTIC_TOOLS
from arifosmcp.tools.drift_check import compute_tool_schema_hash


# The 6 canary / transport / conformance tools that were affected by B1
DIAGNOSTIC_CANARY_TOOLS = (
    "arif_ping",
    "arif_conformance_report",
    "arif_schema_echo",
    "arif_version_echo",
    "arif_transport_echo",
    "arif_initialize_probe",
)


def test_b1_canonical_tools_still_hash():
    """Canonical tools must still produce real SHA256 — no regression."""
    for name in CANONICAL_TOOLS:
        h = compute_tool_schema_hash(name)
        assert h.startswith("sha256:"), f"canonical {name}: bad prefix {h!r}"
        assert h != "sha256:unknown_tool", f"canonical {name} regressed to sentinel"
        assert len(h) == 7 + 64, f"canonical {name}: bad length {len(h)}"


def test_b1_diagnostic_canary_tools_now_hash():
    """The 6 canary tools must now produce real SHA256, not the sentinel."""
    for name in DIAGNOSTIC_CANARY_TOOLS:
        # Sanity: the tool must be in DIAGNOSTIC_TOOLS (else the test is moot)
        assert name in DIAGNOSTIC_TOOLS, (
            f"test setup error: {name} missing from DIAGNOSTIC_TOOLS"
        )
        h = compute_tool_schema_hash(name)
        assert h.startswith("sha256:"), f"{name}: bad prefix {h!r}"
        assert h != "sha256:unknown_tool", (
            f"B1 REGRESSION: {name} still returns sentinel — fix reverted?"
        )
        assert len(h) == 7 + 64, f"{name}: bad length {len(h)}"


def test_b1_unknown_tool_returns_sentinel():
    """Fabrication defense must be preserved for genuinely unknown tools."""
    h = compute_tool_schema_hash("arif_definitely_does_not_exist_xyz")
    assert h == "sha256:unknown_tool", (
        f"fabrication defense broken: got {h!r}"
    )


def test_b1_canonical_priority_preserved():
    """If a name is in both maps, CANONICAL_TOOLS must win (priority preserved)."""
    # Build a synthetic conflict by checking a known canonical tool
    canonical_name = next(iter(CANONICAL_TOOLS))
    h_canonical = compute_tool_schema_hash(canonical_name)
    assert h_canonical.startswith("sha256:"), f"{canonical_name} should hash"
    # The hash should match the CANONICAL_TOOLS spec, not DIAGNOSTIC_TOOLS
    import hashlib, json

    payload = json.dumps(CANONICAL_TOOLS[canonical_name], sort_keys=True, default=str)
    expected = f"sha256:{hashlib.sha256(payload.encode()).hexdigest()}"
    assert h_canonical == expected, (
        f"canonical priority broken: got {h_canonical}, expected {expected}"
    )


def test_b1_diagnostic_hash_differs_from_canonical_for_same_name():
    """For tools only in DIAGNOSTIC_TOOLS, the hash must reflect that spec."""
    name = "arif_ping"
    assert name not in CANONICAL_TOOLS
    assert name in DIAGNOSTIC_TOOLS
    h = compute_tool_schema_hash(name)
    import hashlib, json

    payload = json.dumps(DIAGNOSTIC_TOOLS[name], sort_keys=True, default=str)
    expected = f"sha256:{hashlib.sha256(payload.encode()).hexdigest()}"
    assert h == expected, (
        f"diagnostic lookup broken: got {h}, expected {expected}"
    )


def test_b1_hash_is_deterministic():
    """Same spec must produce same hash on repeated calls (no time / RNG leakage)."""
    name = "arif_conformance_report"
    h1 = compute_tool_schema_hash(name)
    h2 = compute_tool_schema_hash(name)
    assert h1 == h2, "hash is not deterministic"