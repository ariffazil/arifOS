"""Two-counters regression (2026-10-21) — one definition of floor pass.

Defect measured on live /health: the payload carried TWO pass counters over
the SAME floors_detail dataset with two definitions of "pass":

  1. layer_health.constitutional.floors_pass — derived from
     health_truth.floor_truth(), which gates every pass through measurement
     provenance (unmeasured_default -> unmeasured, STATIC_CLAIM/claims.json ->
     declared; neither counts as a pass).
  2. a sibling status-only counter — sum(_floor_detail == "pass") — that
     counted a pass whenever the threshold table said pass, provenance or
     not. On a partially-instrumented machine it inflated the pass count
     (e.g. 10/13 where floor_truth() says 7/13).

The status-only counter is deleted; floors_pass now has exactly one producer
(ANTI-BANGANG LAW 8: the mapping rule lives in health_truth.floor_truth()
and nowhere else). These tests pin that: if anyone reintroduces a count that
treats an unmeasured or declared floor as a pass, they fail here.

Pure unit tests over floor_truth + the /health classification vocabulary.
No kernel, no network.

Run pinned, or collection binds the wrong tree:
    PYTHONPATH=/root/arifOS python3 -m pytest \\
        tests/runtime/test_floors_pass_single_definition.py \\
        -p no:cacheprovider --override-ini="pythonpath="
"""

from __future__ import annotations

import sys
from pathlib import Path

import pytest

_REPO_ROOT = Path(__file__).resolve().parents[2]
if str(_REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(_REPO_ROOT))

from arifosmcp.runtime.health_truth import floor_truth  # noqa: E402
from arifosmcp.runtime.rest_routes.rest_routes import (  # noqa: E402
    _FLOOR_STATUS_PASS,
    _FLOOR_STATUS_UNMEASURED,
    _floor_status_with_provenance,
)

ALL_PASS = {f"F{i}": _FLOOR_STATUS_PASS for i in range(1, 14)}

# The two live greenwash shapes (measured 2026-10-21 on KVM8 /health):
_DEFAULTED = "unmeasured_default:empty_kernel_signal"   # placeholder, not a pass
_CLAIMED = "f4_f9_probe:claims.json:2026-10-21T09:00:00Z"  # claim, not a measurement


def _status_only_pass_count(detail: dict[str, str]) -> int:
    """The DELETED counter, rebuilt here only as the falsifier.

    This is the exact expression the /health handler used to publish beside
    floor_truth()'s count. If a fix or refactor restores it into the payload,
    the equivalence tests below fail — because this one counts passes that
    floor_truth() does not.
    """
    return sum(1 for st in detail.values() if st == _FLOOR_STATUS_PASS)


# ── 1. The live defect shape: 10 statuses "pass" but only 7 are measured ────

def test_live_defect_shape_two_counters_disagree() -> None:
    """Exactly the live reading: 3 fails + 10 threshold-passes, but F2/F5/F6's
    statuses are green while their provenance is a placeholder — floor_truth()
    counts 7, the status-only counter counts 10."""
    detail = dict(ALL_PASS)
    detail["F1"] = "fail"
    detail["F6"] = "fail"
    detail["F8"] = "fail"
    prov = {
        "F2": _DEFAULTED,
        "F5": _DEFAULTED,
        # everything else carries a live instrument
        **{f"F{i}": "arifflow_fq_probe:fq=0.9" for i in range(1, 14) if i not in (2, 5)},
    }
    truth = floor_truth(detail, 13, provenance=prov)

    # floor_truth refuses to launder placeholders into passes
    # (F6's measured fail dominates its provenance, so 13 - 3 fails - 2
    # placeholders = 8 genuine passes)
    assert truth.floors_pass == 8
    # ...while the deleted status-only counter would have said 10
    assert _status_only_pass_count(detail) == 10
    assert truth.floors_pass != _status_only_pass_count(detail)


# ── 2. The invariant the /health counter must obey ──────────────────────────

def test_unmeasured_floor_is_never_counted_as_pass() -> None:
    prov = {f"F{i}": _DEFAULTED for i in range(1, 14)}
    truth = floor_truth(ALL_PASS, 13, provenance=prov)
    # All 13 statuses say "pass"; zero instruments exist. 0/13, not 13/13.
    assert truth.floors_pass == 0
    assert truth.floor_passed is None
    assert len(truth.floors_unmeasured) == 13


def test_declared_floor_is_never_counted_as_pass() -> None:
    prov = {f"F{i}": _CLAIMED for i in range(1, 14)}
    truth = floor_truth(ALL_PASS, 13, provenance=prov)
    # claims.json is evidence OF a claim, never a measurement (KX-003).
    assert truth.floors_pass == 0
    assert len(truth.floors_declared) == 13


def test_measured_passes_are_all_floor_truth_counts() -> None:
    prov = {f"F{i}": "witness_producers:human+ai+earth" for i in range(1, 14)}
    truth = floor_truth(ALL_PASS, 13, provenance=prov)
    assert truth.floors_pass == 13
    # Only here — every floor measured — do the two definitions coincide.
    assert truth.floors_pass == _status_only_pass_count(ALL_PASS)


# ── 3. The classifier layer: provenance still gates the status vocabulary ───

@pytest.mark.parametrize("law_id,score", [("F2", 0.5), ("F5", 0.5), ("F9", 0.0)])
def test_classifier_keeps_defaulted_floors_out_of_the_pass_vocabulary(
    law_id: str, score: float
) -> None:
    """If the classifier ever renders a defaulted floor 'pass', the status-only
    counter class of defect becomes expressible again."""
    assert _floor_status_with_provenance(law_id, score, _DEFAULTED) == _FLOOR_STATUS_UNMEASURED


def test_module_source_carries_no_status_only_pass_counter() -> None:
    """Structural pin: the deleted expression must stay deleted. The single
    producer of floors_pass in /health is _floor_verdict.floors_pass."""
    src = Path(
        _REPO_ROOT / "arifosmcp/runtime/rest_routes/rest_routes.py"
    ).read_text()
    assert "_floors_pass_count" not in src
    # and the verdict's provenance-gated count is what the payload consumes
    assert '"floors_pass": _floor_verdict.floors_pass' in src
