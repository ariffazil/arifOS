"""Regression pin — surface self-consistency must not hide what it cannot see.

Measured before the fix (2026-09-21, arifOS MCP :8088, deployed sha 3db8a658):
/health reported surface_consistency.verdict="CONSISTENT" with divergences=[]
while, on the same living system:

  * ZEN_ABSORBED (public_surface.py) declared 5 names "absorbed — handlers remain
    for compatibility". Three of them were ALSO in tool_registry.json's
    internal_canonical_order, and one (arif_triage) still DISPATCHED on the live
    wire while two others (arif_fetch, arif_critique) answered "Unknown tool".
    One set of five; three different realities.
  * The absorbed names were SUBTRACTED from the internal-only set by name, so no
    vantage ever reported them.
  * `any_divergence` was computed and then never consulted by the verdict.

A name-level check passes on every one of those names. That is the point: a hash
over names certifies nothing. These assertions pin the reachability check, not
the spelling.

Self-contained on purpose: imports only symbols that exist today, so it cannot be
silently uncollectable (the failure mode that left the SCT/ACT gate with zero
coverage). Read-only: writes nothing, calls nothing that mutates.
"""

from __future__ import annotations

import os

import pytest


@pytest.fixture(scope="module")
def result():
    from arifosmcp.runtime.surface_consistency import verify_surface_consistency

    return verify_surface_consistency()


def _absorbed_vantage(res: dict):
    for v in res.get("vantages", []):
        if "absorbed_tools" in v:
            return v
    return None


def test_absorbed_names_are_reported_not_subtracted(result):
    """The absorbed set must be carried as its own reported set."""
    v = _absorbed_vantage(result)
    assert v is not None, (
        "no vantage reports absorbed_tools — the absorbed names are being "
        "subtracted silently again, so nothing can compare them"
    )
    assert "absorbed_count" in v, "absorbed_count missing"
    assert isinstance(v["absorbed_tools"], list), "absorbed_tools must be a list"
    assert v["absorbed_count"] == len(v["absorbed_tools"]), (
        "absorbed_count disagrees with absorbed_tools — two numbers, one concept"
    )


def test_absorbed_set_matches_the_declared_absorb_list(result):
    """Whatever ZEN_ABSORBED names that are also canonical must be listed."""
    from arifosmcp.constitutional_map import CANONICAL_TOOLS
    from arifosmcp.runtime.public_surface import ZEN_ABSORBED

    expected = sorted(set(CANONICAL_TOOLS.keys()) & ZEN_ABSORBED)
    v = _absorbed_vantage(result)
    assert v is not None
    assert sorted(v["absorbed_tools"]) == expected, (
        f"absorbed_tools={sorted(v['absorbed_tools'])} != ZEN_ABSORBED∩CANONICAL_TOOLS={expected}"
    )


def test_divergences_are_load_bearing(result):
    """A recorded divergence must move the verdict. Otherwise the witness is decoration."""
    divergences = result.get("divergences") or []
    verdict = result.get("verdict")
    if divergences:
        assert verdict != "CONSISTENT", (
            f"{len(divergences)} divergence(s) recorded but verdict={verdict!r} — "
            "any_divergence is not feeding the verdict again"
        )
    assert verdict in ("CONSISTENT", "DIVERGENT", "BROKEN"), f"bad verdict {verdict!r}"


def test_absorbed_name_declared_canonical_is_flagged(result):
    """The real, currently-live defect: an 'absorbed' name still declared canonical."""
    v = _absorbed_vantage(result)
    if v is None:
        pytest.skip("absorbed vantage unavailable")
    absorbed = set(v["absorbed_tools"])
    if not absorbed:
        pytest.skip("no absorbed names on this surface")

    reg_path = None
    for p in (
        "/opt/arifos/app/arifosmcp/tool_registry.json",
        "/root/arifOS/arifosmcp/tool_registry.json",
    ):
        if os.path.isfile(p):
            reg_path = p
            break
    if reg_path is None:
        pytest.skip("tool_registry.json not found")

    import json

    with open(reg_path) as fh:
        reg = json.load(fh)
    declared = set(reg.get("canonical_order", [])) | set(reg.get("internal_canonical_order", []))
    overlap = sorted(absorbed & declared)
    if not overlap:
        pytest.skip("no overlap between absorbed and declared-canonical names")

    divergences = " || ".join(result.get("divergences") or [])
    for name in overlap:
        assert name in divergences, (
            f"{name} is declared 'absorbed' AND declared canonical in "
            f"{os.path.basename(reg_path)}, but no divergence names it. "
            f"divergences={result.get('divergences')}"
        )
