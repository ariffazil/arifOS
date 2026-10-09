"""G0 dual-axis decomposition gates: metabolic stage ≠ governance tier.

The "888_JUDGE" conflation dies here: one string was encoding two
coordinates. decompose() maps any legacy token to BOTH axes without
guessing; every canonical verb carries both natively; the G0.6 capability
hash includes both fields so an axis reassignment flips the boundary.
"""

from __future__ import annotations

import copy
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO))

from arifosmcp.core.axis_map import (  # noqa: E402
    GOVERNANCE_TIERS,
    METABOLIC_STAGES,
    VERB_AXES,
    axes_for_verb,
    decompose,
)


def test_conflated_legacy_string_decomposes_to_both_axes():
    assert decompose("888_JUDGE") == {
        "metabolic_stage": "JUDGE_666",
        "governance_tier": "APEX_888",
    }
    assert decompose("JUDGE_888") == {
        "metabolic_stage": "JUDGE_666",
        "governance_tier": "APEX_888",
    }


def test_bare_number_is_metabolic_only_never_guessed_to_tier():
    assert decompose("666") == {"metabolic_stage": "JUDGE_666"}
    assert "governance_tier" not in decompose("777")


def test_canonical_compound_forms_round_trip():
    assert decompose("JUDGE_666") == {
        "metabolic_stage": "JUDGE_666",
        "governance_tier": "APEX_888",
    }
    assert decompose("APEX_888") == {
        "metabolic_stage": "JUDGE_666",
        "governance_tier": "APEX_888",
    }
    assert decompose("arif_judge") == {
        "metabolic_stage": "JUDGE_666",
        "governance_tier": "APEX_888",
    }


def test_every_canonical_verb_carries_both_axes():
    assert len(VERB_AXES) == 8
    for verb, axes in VERB_AXES.items():
        assert axes["metabolic_stage"].rsplit("_", 1)[1] in METABOLIC_STAGES
        assert axes["governance_tier"] in GOVERNANCE_TIERS
        assert axes_for_verb(verb) == axes


def test_judge_is_666_metabolic_and_888_is_apex_cell():
    """The D5 ratification and the APEX cell framing coexist — on axes."""
    assert VERB_AXES["arif_judge"]["metabolic_stage"] == "JUDGE_666"
    assert VERB_AXES["arif_judge"]["governance_tier"] == "APEX_888"
    assert VERB_AXES["arif_seal"]["governance_tier"] == "SOVEREIGN_F13"
    assert VERB_AXES["arif_forge"]["governance_tier"] == "EXECUTOR_777"


def test_capability_hash_carries_and_senses_axes():
    sys.path.insert(0, str(REPO / "scripts"))
    from compute_capability_hash import build_records, capability_hash

    records = build_records()
    for r in records:
        assert "metabolic_stage" in r and "governance_tier" in r
    h0 = capability_hash(records)
    mutated = copy.deepcopy(records)
    next(r for r in mutated if r["canonical_name"] == "arif_judge")[
        "governance_tier"
    ] = "KERNEL"
    assert capability_hash(mutated) != h0, "axis reassignment must flip the boundary"
