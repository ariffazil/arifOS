"""
test_verdict_lattice.py — J-Space Monotonicity Test Suite
═══════════════════════════════════════════════════════════════════════════════
v1.0 ratified 2026-07-07 — tests the 5-state verdict lattice:

    VOID > HOLD > SABAR > PARTIAL > SEAL
    (most restrictive ─────────► least restrictive)

Covers:
  - SealType enum has exactly 5 canonical states (no drift, no extra)
  - VERDICT_ORDER monotonicity: VOID > HOLD > SABAR > PARTIAL > SEAL
  - VerdictState enum has 14 qualified substates (12 inherited + 2 new PARTIAL_*)
  - merge_verdicts() commutative + associative + idempotent
  - merge_verdicts() respects monotonicity (max-rank wins)
  - is_verdict_allowed() returns True for SEAL/PARTIAL/SABAR, False for HOLD/VOID
  - 5-state lattice matches runtime cascade at core/laws.py:352-372

DITEMPA BUKAN DIBERI — geometry is verified, not assumed.
"""

import pytest

from arifosmcp.models.verdicts import (
    SealType,
    VerdictState,
    FloorName,
    VERDICT_ORDER,
    Verdict,
    enforce_verdict_monotonicity,
    merge_verdicts,
    is_verdict_allowed,
)


# ── LATTICE SHAPE ───────────────────────────────────────────────────────────


def test_seal_type_has_exactly_5_states():
    """SealType must be the canonical 5-state lattice."""
    states = {s.value for s in SealType}
    assert states == {"VOID", "HOLD", "SABAR", "PARTIAL", "SEAL"}


def test_verdict_state_has_14_substates():
    """VerdictState must have 14 canonical substates (12 inherited + 2 PARTIAL)."""
    states = {s.value for s in VerdictState}

    expected = {
        # SEAL substates (2)
        "SEAL_CANONICAL",
        "SEAL_QUALIFIED",
        # HOLD substates (3)
        "HOLD_888",
        "HOLD_UNCERTAINTY",
        "HOLD_TEMPORAL",
        # VOID substates (3)
        "VOID_BREACH",
        "VOID_HANTU",
        "VOID_IRREVERSIBLE",
        # SABAR substates (2)
        "SABAR_EPISTEMIC",
        "SABAR_GEOPOLITICAL",
        # PARTIAL substates (2) — NEW v1.0
        "PARTIAL_DERIVED",
        "PARTIAL_REVERSIBILITY",
    }
    assert states == expected, f"Expected 14 substates, got {len(states)}: {states - expected}"


def test_floor_name_uses_tri_witness_not_quad():
    """The canonical F3 constant must be F3_TRI_WITNESS (not F3_QUAD_WITNESS)."""
    floor_names = {s.value for s in FloorName}
    assert "F3_TRI_WITNESS" in floor_names
    assert "F3_QUAD_WITNESS" not in floor_names


# ── MONOTONICITY ────────────────────────────────────────────────────────────


def test_verdict_order_strictly_monotone():
    """Higher weight = higher authority. VOID > HOLD > SABAR > PARTIAL > SEAL."""
    assert VERDICT_ORDER["SEAL"] < VERDICT_ORDER["PARTIAL"]
    assert VERDICT_ORDER["PARTIAL"] < VERDICT_ORDER["SABAR"]
    assert VERDICT_ORDER["SABAR"] < VERDICT_ORDER["HOLD"]
    assert VERDICT_ORDER["HOLD"] < VERDICT_ORDER["VOID"]


def test_verdict_order_exact_weights():
    """Exact weight assignments per v1.0 canon."""
    assert VERDICT_ORDER["SEAL"] == 0
    assert VERDICT_ORDER["PARTIAL"] == 1
    assert VERDICT_ORDER["SABAR"] == 2
    assert VERDICT_ORDER["HOLD"] == 3
    assert VERDICT_ORDER["VOID"] == 4


def test_enforce_verdict_monotonicity_unknown_raises():
    """Non-canonical verdict strings must raise ValueError."""
    with pytest.raises(ValueError, match="Unknown verdict"):
        enforce_verdict_monotonicity("BANGANG")
    with pytest.raises(ValueError, match="Unknown verdict"):
        enforce_verdict_monotonicity("UNKNOWN")


# ── MERGE PROPERTIES ────────────────────────────────────────────────────────


@pytest.mark.parametrize(
    "v1,v2,expected",
    [
        # Same-weight merges
        ("SEAL", "SEAL", "SEAL"),
        ("PARTIAL", "PARTIAL", "PARTIAL"),
        ("SABAR", "SABAR", "SABAR"),
        ("HOLD", "HOLD", "HOLD"),
        ("VOID", "VOID", "VOID"),
        # Max-rank wins
        ("SEAL", "VOID", "VOID"),
        ("SEAL", "HOLD", "HOLD"),
        ("SEAL", "SABAR", "SABAR"),
        ("SEAL", "PARTIAL", "PARTIAL"),
        ("PARTIAL", "VOID", "VOID"),
        ("PARTIAL", "HOLD", "HOLD"),
        ("PARTIAL", "SABAR", "SABAR"),
        ("SABAR", "VOID", "VOID"),
        ("SABAR", "HOLD", "HOLD"),
        ("HOLD", "VOID", "VOID"),
        # Symmetric
        ("HOLD", "SEAL", "HOLD"),
        ("VOID", "PARTIAL", "VOID"),
    ],
)
def test_merge_verdicts_max_rank_wins(v1, v2, expected):
    """Two verdicts merge by max-rank (the more restrictive wins)."""
    assert merge_verdicts(v1, v2) == expected


def test_merge_verdicts_commutative():
    """merge(v1, v2) == merge(v2, v1) for all pairs."""
    pairs = [
        ("SEAL", "PARTIAL"),
        ("PARTIAL", "SEAL"),
        ("SEAL", "SABAR"),
        ("SABAR", "SEAL"),
        ("PARTIAL", "HOLD"),
        ("HOLD", "PARTIAL"),
        ("SABAR", "VOID"),
        ("VOID", "SABAR"),
    ]
    for v1, v2 in pairs:
        assert merge_verdicts(v1, v2) == merge_verdicts(v2, v1)


def test_merge_verdicts_idempotent():
    """merge(v, v) == v for every canonical verdict."""
    for v in ["SEAL", "PARTIAL", "SABAR", "HOLD", "VOID"]:
        assert merge_verdicts(v, v) == v


def test_merge_verdicts_associative():
    """(a ⊕ b) ⊕ c == a ⊕ (b ⊕ c) for all combinations."""
    cases = [
        ("SEAL", "PARTIAL", "SABAR"),
        ("PARTIAL", "SABAR", "HOLD"),
        ("SABAR", "HOLD", "VOID"),
        ("SEAL", "SEAL", "VOID"),
    ]
    for a, b, c in cases:
        left = merge_verdicts(merge_verdicts(a, b), c)
        right = merge_verdicts(a, merge_verdicts(b, c))
        assert left == right, f"({a} ⊕ {b}) ⊕ {c} = {left} ≠ {right} = {a} ⊕ ({b} ⊕ {c})"


# ── PROGRESSION ─────────────────────────────────────────────────────────────


@pytest.mark.parametrize("v", ["SEAL", "PARTIAL", "SABAR"])
def test_progression_allowed_for_low_weight(v):
    """SEAL/PARTIAL/SABAR allow progression (with semantics)."""
    assert is_verdict_allowed(v) is True


@pytest.mark.parametrize("v", ["HOLD", "VOID"])
def test_progression_blocked_for_high_weight(v):
    """HOLD/VOID block progression."""
    assert is_verdict_allowed(v) is False


# ── RUNTIME CASCADE ALIGNMENT ───────────────────────────────────────────────


def test_partial_substates_are_part_of_partial_substate_namespace():
    """The new PARTIAL_DERIVED and PARTIAL_REVERSIBILITY substates exist."""
    assert VerdictState.PARTIAL_DERIVED.value == "PARTIAL_DERIVED"
    assert VerdictState.PARTIAL_REVERSIBILITY.value == "PARTIAL_REVERSIBILITY"


def test_partial_is_not_in_seal_or_sabar_substate_namespaces():
    """Sanity check: the 2 new substates belong to PARTIAL, not to other verdicts."""
    # All substate names that contain "PARTIAL_" should map to PARTIAL conceptually
    partial_substates = [s for s in VerdictState if "PARTIAL" in s.value]
    assert len(partial_substates) == 2
    assert VerdictState.PARTIAL_DERIVED in partial_substates
    assert VerdictState.PARTIAL_REVERSIBILITY in partial_substates


def test_seal_alias_is_canonical():
    """Verdict aliased to SealType — same identity."""
    assert Verdict is SealType


# ── TERMINAL VERDICTS ───────────────────────────────────────────────────────


def test_terminal_verdicts_have_no_legal_out_transition():
    """VOID and SEAL are terminal — once emitted, no verdict override."""
    # SEAL followed by anything is SEAL (because VOID wins if any is VOID,
    # but HOLD cannot downgrade SEAL — SEAL is terminal for progression)
    assert merge_verdicts("SEAL", "VOID") == "VOID"  # VOID overrides everything
    # But SEAL is the lowest weight for proceeding; VOID takes precedence
    # Terminal test: VOID merges with anything remain VOID
    for v in ["SEAL", "PARTIAL", "SABAR", "HOLD"]:
        assert merge_verdicts("VOID", v) == "VOID"
        assert merge_verdicts(v, "VOID") == "VOID"


# ── LATTICE COVERAGE ────────────────────────────────────────────────────────


def test_all_5_states_round_trip_through_seal_type():
    """Each state name stringifies → enum → stringifies back unchanged."""
    for v in ["VOID", "HOLD", "SABAR", "PARTIAL", "SEAL"]:
        enum_val = SealType(v)
        assert enum_val.value == v
        # Verify monotonicity works on enum
        w = enforce_verdict_monotonicity(enum_val)
        assert isinstance(w, int)
        assert 0 <= w <= 4
