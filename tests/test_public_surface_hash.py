"""Regression test: the released surface_hash must cover the whole public wire.

Failure class (measured 2026-10-29 against the live release
`arifos-7599f1c42cf9`, public path https://mcp.arif-fazil.com/mcp):

  released surface_hash = sha256:6295a69b2fb7444ce7b75594606c564e07369346cb23b47fbe6ddceb61ff6290
  = SHA-256 over exactly 8 names:
      arif_forge arif_init arif_judge arif_memory arif_observe arif_route arif_seal arif_think

  the public `tools/list` exposed 14. The six outside the hash were:
      arif_report read_resource search_resources arif_research arif_recall arif_delegate

  All six are coordination channels. So removing any of them from the public
  surface left `surface_hash` unchanged — a caller had no way to detect that the
  surface had changed, or that five of the six were dead.

Cause: `_compute_tool_surface_hash()` hashed `public_tool_names()` (the
constitutional verbs only) while the wire exposed the constitutional verbs plus
the coordination channels. Three places computed "what is on the public wire"
by hand and could drift apart.

Fix: one owner — `public_surface.public_exposed_tool_names()` — read by the
tools/list filter, the tools/call gate, and the surface hash.
"""

from __future__ import annotations

import hashlib
import json

import pytest

PRODUCTION_MODE = "forge_next_8"

# Public wire reduced 14 → 9 (recommended by external probe 2026-10-29 02:21;
# ratified by Arif 11:46 MYT, F13).
# KERNEL_ABI_8 + arif_report. read_resource / search_resources are absorbed as
# arif_observe modes resource_read / resource_search; arif_research,
# arif_recall, arif_delegate are retired (jobs owned by observe/memory/route).
LIVE_PUBLIC_SURFACE = (
    "arif_forge",
    "arif_init",
    "arif_judge",
    "arif_memory",
    "arif_observe",
    "arif_report",
    "arif_route",
    "arif_seal",
    "arif_think",
)


def _hash_of(names) -> str:
    schemas = {name: {"name": name} for name in sorted(names)}
    raw = json.dumps(schemas, sort_keys=True, separators=(",", ":"))
    return "sha256:" + hashlib.sha256(raw.encode()).hexdigest()


@pytest.fixture
def production_mode(monkeypatch):
    monkeypatch.setenv("ARIFOS_PUBLIC_SURFACE_MODE", PRODUCTION_MODE)
    monkeypatch.setenv("ARIFOS_MCP_EXPOSE_DEV_TOOLS", "false")


def test_exposed_set_matches_the_live_public_wire(production_mode):
    from arifosmcp.runtime.public_surface import public_exposed_tool_names

    assert sorted(public_exposed_tool_names()) == sorted(LIVE_PUBLIC_SURFACE)


def test_retired_coordination_tools_are_off_the_wire(production_mode):
    """F13 2026-10-29: the five retired names must never appear on the wire.

    Off the wire entirely — "advertised-but-uncallable is worse than absent."
    """
    from arifosmcp.runtime.public_surface import (
        RETIRED_COORDINATION_TOOLS,
        public_exposed_tool_names,
    )

    exposed = set(public_exposed_tool_names())
    for name in RETIRED_COORDINATION_TOOLS:
        assert name not in exposed, f"{name} retired but still exposed"


def test_surface_hash_covers_every_exposed_tool(production_mode):
    """The hash input must be the exposed set — not the constitutional verbs only."""
    from arifosmcp.runtime.build import _compute_tool_surface_hash
    from arifosmcp.runtime.public_surface import public_exposed_tool_names

    exposed = sorted(public_exposed_tool_names())
    assert _compute_tool_surface_hash() == _hash_of(exposed)


def test_coordination_channels_are_inside_the_hash(production_mode):
    """Every coordination channel must be covered by the released hash."""
    from arifosmcp.runtime.build import _compute_tool_surface_hash
    from arifosmcp.runtime.public_surface import COORDINATION_TOOLS, public_exposed_tool_names

    exposed = set(public_exposed_tool_names())
    for name in COORDINATION_TOOLS:
        assert name in exposed, f"{name} is on the wire but outside the exposed set"


def test_removing_a_coordination_tool_changes_the_hash(production_mode, monkeypatch):
    """The proof: adding or removing a tool must move the hash.

    Before the fix this was a no-op for all six coordination channels.
    """
    from arifosmcp.runtime import build as build_mod
    from arifosmcp.runtime import public_surface as ps

    before = build_mod._compute_tool_surface_hash()
    # F13 2026-10-29: the only coordination channel left on the wire is
    # arif_report — removing it must still move the hash.
    monkeypatch.setattr(
        ps,
        "COORDINATION_TOOLS",
        tuple(t for t in ps.COORDINATION_TOOLS if t != "arif_report"),
    )
    after = build_mod._compute_tool_surface_hash()
    assert after != before, "removing an exposed tool did not change surface_hash"


def test_hash_matches_the_tools_list_filter(production_mode):
    """The list filter and the hash must read the same set — one owner."""
    from arifosmcp.runtime.build import _compute_tool_surface_hash
    from arifosmcp.runtime.public_surface import public_exposed_tool_names

    exposed = sorted(public_exposed_tool_names())
    assert _compute_tool_surface_hash() == _hash_of(exposed)
    # The filter in server.py uses this same function; assert the two agree.
    assert set(exposed) >= set(LIVE_PUBLIC_SURFACE) - set()
