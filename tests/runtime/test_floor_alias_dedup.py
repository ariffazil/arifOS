"""Regression tests for FLR-005 — L→F alias dedup in floor counting.

Root cause (2026-10-16): LAW_SPEC_KEYS stores floors 10-13 under the L-prefix
(L10..L13) while the F2/F11/F12/F13 producers emit F11/F12/F13, and
``_wire_producer()`` syncs the F→L aliases back into ``resolved_floors``. The
published map therefore carried BOTH the canonical F id and its L alias for
floors 10-13 — 16 entries for 13 floors — which inflated ``floors_pass`` to 16
and minted phantom coverage (L11≡F11, L12≡F12, L13≡F13 double-counted).

The fix is a single normalizer at the publish boundary that collapses
L10-L13 → F10-F13 and drops duplicate alias keys. It is STRICTLY structural:
no threshold, comparator, or floor semantics change (see test 10).

Run pinned (same as sibling floor tests):
    PYTHONPATH=/root/arifOS python3 -m pytest \
        tests/runtime/test_floor_alias_dedup.py \
        -p no:cacheprovider --override-ini="pythonpath="
"""

from __future__ import annotations

import sys
from pathlib import Path

import pytest

_REPO_ROOT = Path(__file__).resolve().parents[2]
if str(_REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(_REPO_ROOT))

from arifosmcp.runtime.rest_routes.rest_routes import (  # noqa: E402
    _CANONICAL_FLOOR_IDS,
    _FLOOR_STATUS_FAIL,
    _floor_status_with_provenance,
    _normalize_floors_to_canonical,
)
from core.shared.laws import (  # noqa: E402
    get_floor_comparator,
    get_floor_spec,
    get_law_threshold,
)

# A full 13-floor canonical map (F1-F13), values arbitrary but distinct.
_CANON13 = {f"F{i}": 0.5 + i * 0.01 for i in range(1, 14)}
# The legacy 10-13 aliases, with values matching their F counterparts.
_LEGACY10_13 = {"L10": 0.6, "L11": 0.61, "L12": 0.62, "L13": 0.63}


# ── 1. F1-F13 alone → exactly 13 floors ──────────────────────────────────────
def test_canonical_only_yields_13_floors():
    scores, prov, contradictions = _normalize_floors_to_canonical(_CANON13)
    assert set(scores) == set(_CANONICAL_FLOOR_IDS)
    assert len(scores) == 13
    assert contradictions == set()


# ── 2. L10-L13 alone normalize to F10-F13 ────────────────────────────────────
def test_legacy_aliases_normalize_to_canonical_f():
    legacy = dict(_LEGACY10_13)
    scores, prov, contradictions = _normalize_floors_to_canonical(legacy)
    assert set(scores) == {"F10", "F11", "F12", "F13"}
    assert scores["F10"] == 0.6
    assert scores["F13"] == 0.63
    assert contradictions == set()


# ── 3. Mixed L10-L13 + F10-F13 still yields exactly 13 floors ────────────────
def test_mixed_alias_and_canonical_dedup_to_13():
    mixed = dict(_CANON13)          # has F10-F13
    mixed.update(_LEGACY10_13)      # adds L10-L13 aliases (equal values)
    assert len(mixed) == 17          # sanity: 13 + 4 aliases
    scores, prov, contradictions = _normalize_floors_to_canonical(mixed)
    assert len(scores) == 13
    assert set(scores) == set(_CANONICAL_FLOOR_IDS)
    assert contradictions == set()
    # canonical value survives, alias dropped
    assert scores["F11"] == _CANON13["F11"]


# ── 4. Contradicting alias+canonical values fail closed, not silently picked ──
def test_contradicting_alias_is_not_silently_reconciled():
    mixed = dict(_CANON13)
    mixed["L11"] = 999.0            # contradicts F11 == 0.61
    scores, prov, contradictions = _normalize_floors_to_canonical(mixed)
    assert "F11" in contradictions
    assert prov["F11"] == "floor_alias_contradiction"
    # And the status path fails closed (never pass, never unmeasured-silent):
    assert (
        _floor_status_with_provenance("F11", None, "floor_alias_contradiction")
        == _FLOOR_STATUS_FAIL
    )


# ── 5. Duplicate aliases do not raise the denominator ────────────────────────
def test_duplicate_aliases_do_not_raise_denominator():
    mixed = dict(_CANON13)
    mixed.update(_LEGACY10_13)
    scores, _, _ = _normalize_floors_to_canonical(mixed)
    # denominator is the canonical floor set — 13, not 17
    assert len(scores) == 13
    assert len(scores) < len(mixed)


# ── 6. Unknown floor names never become new floors ───────────────────────────
def test_unknown_floor_names_are_dropped():
    dirty = dict(_CANON13)
    dirty["F14"] = 0.99
    dirty["NOT_A_FLOOR"] = 0.5
    scores, _, _ = _normalize_floors_to_canonical(dirty)
    assert "F14" not in scores
    assert "NOT_A_FLOOR" not in scores
    assert len(scores) == 13


# ── 7. Existing canonical input keeps working ────────────────────────────────
def test_existing_canonical_input_preserved():
    scores, prov, contradictions = _normalize_floors_to_canonical(
        _CANON13, provenance={f"F{i}": "measured" for i in range(1, 14)}
    )
    assert scores == _CANON13
    assert prov["F5"] == "measured"
    assert contradictions == set()


# ── 8. Legacy compatibility input remains readable where supported ───────────
def test_legacy_input_remains_readable():
    legacy = dict(_LEGACY10_13)
    legacy_prov = {"L10": "floor_producer:PASS:ontology", "L11": "legacy"}
    scores, prov, contradictions = _normalize_floors_to_canonical(legacy, legacy_prov)
    assert scores["F10"] == 0.6
    assert prov["F10"] == "floor_producer:PASS:ontology"
    assert prov["F11"] == "legacy"
    assert contradictions == set()


# ── 9. Aggregate verdict uses the canonical set only ─────────────────────────
def test_aggregate_uses_canonical_set_only():
    mixed = dict(_CANON13)
    mixed.update(_LEGACY10_13)
    scores, prov, contradictions = _normalize_floors_to_canonical(mixed)
    # Rebuild the pass-count the same way rest_routes does, on the normalized map.
    pass_count = sum(
        1
        for fid, sc in scores.items()
        if _floor_status_with_provenance(fid, sc, prov.get(fid)) == "pass"
    )
    # Every canonical entry is counted at most once; total never exceeds 13.
    assert pass_count <= 13
    assert len(scores) == 13


# ── 10. F4/F7/F9 semantics and thresholds are unchanged ──────────────────────
def test_f4_f7_f9_semantics_unchanged():
    # The normalizer is identity on F4/F7/F9 (keys and values untouched).
    scores, _, _ = _normalize_floors_to_canonical(
        {"F4": 0.8, "F7": 0.04, "F9": 0.0}
    )
    assert scores == {"F4": 0.8, "F7": 0.04, "F9": 0.0}
    # Canonical thresholds are exactly as ratified — no threshold moved.
    assert get_floor_spec("F4").get("threshold") == 0.00
    assert get_floor_spec("F7").get("range") == (0.03, 0.05)
    assert get_floor_spec("F9").get("threshold") == 0.30
    assert get_floor_comparator("F9") == "<"
    assert get_law_threshold("F7") == 0.05  # upper bound of the humility band
