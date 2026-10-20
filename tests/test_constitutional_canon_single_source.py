"""
Constitutional canon single-source gate (F13, 2026-10-20)
══════════════════════════════════════════════════════════

WHY: resources do not enforce invariants. On 2026-10-20 the SAME kernel
answered two ways for the same floor:

    arifos://doctrine            F06 MARUAH   • F11 AUDIT
    arif_think(mode="axioms")    F06 EMPATHY  • F11 "verify identity"
    arif_think confidence        0.97         (F02 caps at 0.90)

Five hand-typed floor tables existed. This test is the adversarial check
the proposal asked for: it fails the moment any renderer drifts from
arifosmcp/constitutional_canon.py, and it fails if the wire schema
advertises a parameter the live handler cannot accept (the `concise`
defect: every client that passed it got "invalid input types").
"""

from __future__ import annotations

import re

import pytest

from arifosmcp import constitutional_canon as canon

# ── helpers ──────────────────────────────────────────────────────────────


def _norm(text: str) -> str:
    """Name comparison ignores case, spaces, hyphens, digits and marks."""
    return re.sub(r"[^A-Z]", "", text.upper())


def _assert_mentions(name: str, text: str, where: str) -> None:
    assert _norm(name) in _norm(text), (
        f"{where}: canonical name {name!r} missing from prose {text!r}"
    )


# ── 1. canon integrity ───────────────────────────────────────────────────


def test_canon_has_thirteen_floors_with_frozen_law_ids():
    assert len(canon.FLOORS) == 13
    assert [f.fid for f in canon.FLOORS] == [f"F{i}" for i in range(1, 14)]
    # Law ids are persisted in receipts/VAULT999 — they must never move.
    assert canon.BY_FID["F6"].law_id == "L06_EMPATHY"
    assert canon.BY_FID["F11"].law_id == "L11_AUDIT"


def test_canon_names_match_ratified_doctrine():
    # The ratified resource text is the authority for display names.
    expected = {
        "F1": "AMANAH",
        "F2": "TRUTH",
        "F3": "WITNESS",
        "F4": "CLARITY",
        "F5": "PEACE",
        "F6": "MARUAH",
        "F7": "HUMILITY",
        "F8": "GENIUS",
        "F9": "ANTI-HANTU",
        "F10": "ONTOLOGY",
        "F11": "AUDIT",
        "F12": "INJECTION",
        "F13": "SOVEREIGN",
    }
    assert {f.fid: f.name for f in canon.FLOORS} == expected


def test_no_confidence_above_the_f7_band():
    """F7 sealed canon: cap = 1 − Ω₀ ∈ [0.95, 0.97], ceiling 0.96.
    The old 0.90 figure was itself the drift F13 absorbed on 2026-07-23."""
    for f in canon.FLOORS:
        c = f.to_axiom()["confidence"]
        assert 0.95 <= c <= 0.97, f"{f.fid} confidence {c} outside the Ω₀ band"
    assert canon.CONFIDENCE_CAP == 0.96
    assert canon.CONFIDENCE_MAX == 0.97


# ── 2. every renderer agrees with canon ──────────────────────────────────


def test_doctrine_resource_renders_from_canon():
    from arifosmcp.resources.doctrine import DOCTRINE_TEXT

    assert canon.doctrine_block() in DOCTRINE_TEXT, (
        "arifos://doctrine floor block is not the canon block — someone retyped it"
    )
    for f in canon.FLOORS:
        line = next(
            (ln for ln in DOCTRINE_TEXT.splitlines() if ln.startswith(f"F{int(f.fid[1:]):02d} ")),
            None,
        )
        assert line is not None, f"doctrine missing {f.fid}"
        assert f.doctrine in line, f"doctrine {f.fid} rule drifted: {line!r}"


def test_axioms_tool_catalogue_matches_canon():
    catalogue = canon.axiom_catalogue()
    assert [a["id"] for a in catalogue] == [f.law_id for f in canon.FLOORS]
    for item, f in zip(catalogue, canon.FLOORS, strict=True):
        assert item["name"] == f.name
        assert item["text"] == f.axiom
        assert 0.95 <= item["confidence"] <= 0.97
    # the exact drift that was live: EMPATHY, and authority-for-audit
    by_name = {a["name"]: a for a in catalogue}
    assert "EMPATHY" not in by_name
    assert by_name["MARUAH"]["text"].lower().startswith("maruah")
    assert "trace" in by_name["AUDIT"]["text"].lower()


def test_runtime_law_descriptions_derive_from_canon():
    from arifosmcp.runtime.law import LAW_DESCRIPTIONS

    assert len(LAW_DESCRIPTIONS) == 13
    for f in canon.FLOORS:
        key = next((k for k in LAW_DESCRIPTIONS if k.name == f.law_id), None)
        assert key is not None, f"runtime LAW_DESCRIPTIONS missing {f.law_id}"
        assert LAW_DESCRIPTIONS[key] == f.axiom, (
            f"runtime law {f.law_id} prose drifted from canon: "
            f"{LAW_DESCRIPTIONS[key]!r} != {f.axiom!r}"
        )


def test_core_law_descriptions_align_with_canon():
    from arifosmcp.core.law import LAW_DESCRIPTIONS

    for f in canon.FLOORS:
        key = next((k for k in LAW_DESCRIPTIONS if k.name == f.law_id), None)
        assert key is not None, f"core.law missing {f.law_id}"
        assert LAW_DESCRIPTIONS[key] == f.axiom, (
            f"core.law {f.law_id} prose drifted from canon: "
            f"{LAW_DESCRIPTIONS[key]!r} != {f.axiom!r}"
        )


def test_floor_table_names_align_with_canon():
    from arifosmcp.resources.floor_table import FLOOR_TABLE

    for f in canon.FLOORS:
        text = FLOOR_TABLE[f.fid]
        first = text.splitlines()[0]
        assert first.startswith(f"{f.fid} {f.name}"), (
            f"floor_table {f.fid} first line is not canonical: {first!r}"
        )


# ── 3. wire schema must not advertise what the handler rejects ───────────


def test_arif_think_advertises_only_accepted_parameters():
    """The `concise` defect: advertised, but the live handler cannot accept it."""
    import inspect

    import arifosmcp.server as server  # noqa: F401 — builds the live registry

    provider = server.mcp._local_provider
    components = getattr(provider, "_components", {})
    tool = next(
        (v for k, v in components.items() if str(k).startswith("tool:arif_think@")),
        None,
    )
    assert tool is not None, "arif_think is not registered on the live surface"

    advertised = set((tool.parameters or {}).get("properties") or {})
    handler = tool.fn
    accepted = {
        p.name
        for p in inspect.signature(handler).parameters.values()
        if p.kind
        in (inspect.Parameter.POSITIONAL_OR_KEYWORD, inspect.Parameter.KEYWORD_ONLY)
    }

    phantom = advertised - accepted
    assert not phantom, (
        "arif_think advertises parameters the handler cannot accept "
        f"(any call passing them fails): {sorted(phantom)}"
    )
