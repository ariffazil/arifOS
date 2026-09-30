"""Tripwire: tool_registry.json is hand-maintained and its generator has diverged.

Measured 2026-09-30 (333-AGI). `tool_registry.json` used to declare
`_source: arifosmcp.abi.capability_registry + constitutional_map.CANONICAL_TOOLS`,
which invited any agent to regenerate it. Regenerating would be destructive:

  * 12 of 18 top-level keys differ from the committed artifact
  * 62 of 66 tool entries differ
  * internal_canonical_count would jump 6 -> 17
  * it would ADD arif_challenge / arif_commit / arif_stage and DROP arif_act /
    arif_runtime_health / arif_telegram_send / arif_verify
  * decisively, its `canonical_order` yields only SEVEN tools, omitting
    **arif_memory** — which the live MCP wire does expose (tools/list returns 8)

Six modules read this file (tools/health.py, runtime/capability_drift.py,
runtime/surface_consistency.py, tools/retrieve_tools.py,
runtime/rest_routes/topology_routes.py, scripts/observatory_emit.py), so a blind
regeneration would silently remove a live canonical verb from the registry that
decides the kernel's public surface.

These tests pin the divergence so it cannot be rediscovered by accident — and,
because the generator test is `strict` xfail, they will FAIL LOUDLY the day someone
repairs the generator without updating the marker. That is intentional: fixing the
generator is the goal, and doing so should force a deliberate edit here.
"""

from __future__ import annotations

import json
from pathlib import Path

import pytest

REGISTRY = Path(__file__).resolve().parents[2] / "arifosmcp" / "tool_registry.json"

# The eight canonical verbs the live MCP wire exposes (verified via tools/list).
LIVE_CANONICAL_EIGHT = [
    "arif_init",
    "arif_observe",
    "arif_think",
    "arif_route",
    "arif_memory",
    "arif_judge",
    "arif_forge",
    "arif_seal",
]


@pytest.fixture(scope="module")
def registry() -> dict:
    if not REGISTRY.is_file():
        pytest.skip(f"{REGISTRY} not found")
    return json.loads(REGISTRY.read_text())


def test_artifact_declares_itself_hand_maintained(registry):
    """The provenance field must not invite a regeneration that would corrupt it."""
    src = str(registry.get("_source", ""))
    assert "HAND-MAINTAINED" in src.upper(), (
        "_source no longer warns against regeneration — the false derivation claim "
        f"({src!r}) is what nearly caused a live canonical verb to be dropped"
    )
    assert registry.get("_maintenance"), "_maintenance block missing"


def test_artifact_canonical_order_is_the_live_eight(registry):
    """The committed artifact must keep all eight canonical verbs."""
    assert registry.get("canonical_order") == LIVE_CANONICAL_EIGHT, (
        f"canonical_order={registry.get('canonical_order')} != the live eight; "
        "this file decides the kernel's public surface"
    )


def test_artifact_counts_are_self_consistent(registry):
    """A count field must equal the length of the list it counts."""
    for count_key, list_key in (
        ("canonical_count", "canonical_order"),
        ("internal_canonical_count", "internal_canonical_order"),
    ):
        if count_key in registry and list_key in registry:
            assert registry[count_key] == len(registry[list_key]), (
                f"{count_key}={registry[count_key]} but {list_key} has "
                f"{len(registry[list_key])} entries — two numbers, one concept"
            )


@pytest.mark.xfail(
    strict=True,
    reason=(
        "build_tool_registry_manifest() is KNOWN BROKEN: its canonical_order omits "
        "arif_memory (yields 7 of the 8 live verbs). Repair the generator, then "
        "remove this marker — do NOT regenerate the artifact until it passes."
    ),
)
def test_generator_reproduces_the_live_canonical_eight():
    """The generator must not drop a canonical verb the live wire exposes."""
    from arifosmcp.constitutional_map import build_tool_registry_manifest

    gen = build_tool_registry_manifest()
    missing = [t for t in LIVE_CANONICAL_EIGHT if t not in (gen.get("canonical_order") or [])]
    assert not missing, f"generator's canonical_order omits live canonical verb(s): {missing}"
