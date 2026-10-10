"""FLR-F1-FQ v2 regression tests — F13 "pilih A", 2026-10-10.

The 2026-08-10 three-band φFQ mapping rendered FQ ∈ [0.5, 1.0) a guaranteed
F1 fail (φ = FQ/3.0 ≤ 0.333 < threshold 0.5) even while arifFlow diagnosed
BALANCED/FLOWING — a calibration contradiction with fq_policy.yaml (F13
RATIFIED 2026-09-12, floor 0.5). v2 (``_phi_fq_from_quotient``) aligns the
floor measurement to the policy floor: FQ ≥ 0.5 → φ=1.0, below → φ=0.0.

The seal path's stricter GENESIS/059 gate (tools/vault.py, seal requires
FQ ∈ [1,3]) is a different surface and is deliberately NOT covered here.

Run pinned, or collection binds the wrong tree:
    PYTHONPATH=/root/arifOS python3 -m pytest \\
        tests/runtime/test_phi_fq_calibration_v2.py \\
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
    _phi_fq_from_quotient,
)


@pytest.mark.parametrize(
    "quotient",
    [0.5, 0.684, 0.8077, 0.92, 1.0, 2.0, 3.0, 6.0, 12.7],
)
def test_policy_floor_and_above_is_full_trust(quotient):
    """v2: any FQ ≥ the fq_policy floor (0.5) measures φ=1.0 → F1 passes.

    Includes the previously-failing band [0.5, 1.0) and the previously
    attenuated >3 tail (old φ=min(1, 3/FQ) failed FQ > 6.0).
    """
    assert _phi_fq_from_quotient(quotient) == 1.0


@pytest.mark.parametrize("quotient", [0.0, 0.25, 0.4999])
def test_below_policy_floor_is_zero(quotient):
    """Below the operational floor there is no flow trust to measure."""
    assert _phi_fq_from_quotient(quotient) == 0.0


def test_superseded_mapping_would_have_failed_live_fq():
    """The exact live values that motivated the audit must now pass.

    Live probes 2026-10-10: fq=0.92 (old φ=0.3067 → F1 fail) and fq=0.684
    (old φ=0.228 → F1 fail) — both diagnosed BALANCED by arifFlow.
    """
    for live_value in (0.92, 0.684):
        assert _phi_fq_from_quotient(live_value) == 1.0


def test_boundary_exact_floor_passes():
    """The policy floor itself (0.5) belongs to the acceptable band."""
    assert _phi_fq_from_quotient(0.5) == 1.0
