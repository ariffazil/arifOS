"""F7 HUMILITY producer (Gate 4, F13 directive 2026-11-02).

Ω₀ uncertainty-band discipline. Canon: core/shared/types.py AgiMetrics.omega_0
Field(ge=0.03, le=0.05) HARD ("F7: Ω₀ ∈ [0.03, 0.05]"); mottos.py PromptManifold
Ω₀ ≈ 0.04. Independent of F6 (no dignity/meters) and F8 (no contradiction
register): F7 restrains CERTAINTY claims.

Live wire verified by the K9 deploy probe (runtime_floors_status.F7 +
governance floors + observatory re-emit); these tests pin the pure function,
the canon constraint behaviour, and the ontology row.
"""

from __future__ import annotations

import pytest
from pydantic import ValidationError

from arifosmcp.runtime.floor_producers import (
    _FLOOR_ONTOLOGY,
    _f7_humility,
    collect_floor_producer_signal,
)

HONEST = {
    "omega_0": 0.04,
    "band": [0.03, 0.05],
    "constraint_enforced": True,
}


def test_pass_inside_band():
    sig = _f7_humility(dict(HONEST))
    assert sig["status"] == "PASS"
    assert sig["omega_0"] == pytest.approx(0.04)
    assert 0.03 <= sig["omega_0"] <= 0.05
    assert "shadow_residual" in sig


def test_fail_omega_outside_band():
    sig = _f7_humility({**HONEST, "omega_0": 0.2})
    assert sig["status"] == "FAIL"
    assert sig["reason"] == "omega0_outside_band"


def test_fail_decorative_constraint():
    sig = _f7_humility({**HONEST, "constraint_enforced": False})
    assert sig["status"] == "FAIL"
    assert sig["reason"] == "band_constraint_not_enforced"


def test_fail_perfect_certainty_published():
    sig = _f7_humility({**HONEST, "max_published_confidence": 1.0})
    assert sig["status"] == "FAIL"
    assert sig["reason"] == "perfect_certainty_published"


def test_unmeasured_when_sources_absent():
    for src in (
        {},
        {"omega_0": None},
        {"omega_0": "junk"},
        {"omega_0": 0.04},
        {"omega_0": 0.04, "band": [0.03]},
    ):
        assert _f7_humility(src)["status"] == "UNMEASURED"


def test_canon_constraint_is_real_not_decorative():
    """The builder's live check: AgiMetrics must REJECT an out-of-band Ω₀."""
    from core.shared.types import AgiMetrics

    with pytest.raises(ValidationError):
        AgiMetrics(
            truth_score=0.99, delta_s=-0.1, omega_0=0.9, precision=1.0, free_energy=0.0
        )
    ok = AgiMetrics(
        truth_score=0.99, delta_s=-0.1, omega_0=0.04, precision=1.0, free_energy=0.0
    )
    assert 0.03 <= ok.omega_0 <= 0.05


def test_canon_omega_value_is_declared():
    from core.shared.mottos import PromptManifold

    assert 0.03 <= float(PromptManifold().omega_0) <= 0.05


def test_signal_and_label_wire():
    sig = collect_floor_producer_signal("F7", sources=dict(HONEST))
    assert sig["status"] == "PASS"
    assert sig["falsification_test"], "F7 contract label must ride the signal"


def test_ontology_row_names_the_instrument():
    row = _FLOOR_ONTOLOGY["F7"]
    assert "_f7_humility" in row["producer_instrument"]
    assert row["value_kind"] == "score"
    assert row["evidence_class"] == "PREDICATE_PASS"
