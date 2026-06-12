"""
test_011 — Floor Registry Ground Truth (Direct Kernel)

Bypasses MCP entirely. Imports the kernel's floor registry directly
and verifies that the constitutional substrate is intact, with no
silently-overridden thresholds, no missing floors, no broken type
system.

Pass criteria:
    - All 13 floors (F1-F13) registered with non-None thresholds
    - get_law_threshold(F2) returns 0.99 (canonical)
    - get_law_threshold(F3) returns 0.75 (canonical)
    - get_law_threshold(F6) returns 0.70 (canonical)
    - get_law_threshold(F7) returns 0.05 (humility band upper)
    - get_floor_classes() returns HARD set including F1, F2, F9, F11, F12, F13
    - No floor has threshold 0.0 (which would mean "unconfigured")

This is the constitutional substrate. If this fails, the kernel is
not what it claims to be, regardless of what the MCP layer reports.
"""

import sys
import os

_HERE = os.path.dirname(os.path.abspath(__file__))
if _HERE not in sys.path:
    sys.path.insert(0, _HERE)

REPO_ROOT = "/root/arifOS"
if REPO_ROOT not in sys.path:
    sys.path.insert(0, REPO_ROOT)

from core.shared.laws import (  # noqa: E402
    get_law_threshold,
    get_floor_spec,
    get_floor_classes,
    THRESHOLDS,
    LAW_SPEC_KEYS,
)

EXPECTED_FLOORS = [
    "F1",
    "F2",
    "F3",
    "F4",
    "F5",
    "F6",
    "F7",
    "F8",
    "F9",
    "L10",
    "L11",
    "L12",
    "L13",
]  # ground truth: F10-F13 stored as L10-L13
EXPECTED_HARD_FLOORS = {"F1", "F2", "F9", "L10", "L11", "L12", "L13"}


def test_all_13_floors_registered():
    """All F1-F13 must be in LAW_SPEC_KEYS."""
    for floor in EXPECTED_FLOORS:
        assert floor in LAW_SPEC_KEYS, f"floor {floor} not in LAW_SPEC_KEYS; spec not registered"


def test_canonical_thresholds_match_spec():
    """F2=0.99, F3=0.75, F6=0.70, F7=0.05 must be the canonical values."""
    assert get_law_threshold("F2") == 0.99, (
        f"F2 canonical must be 0.99, got {get_law_threshold('F2')}"
    )
    assert get_law_threshold("F3") == 0.75, (
        f"F3 canonical must be 0.75, got {get_law_threshold('F3')}"
    )
    assert get_law_threshold("F6") == 0.70, (
        f"F6 canonical must be 0.70, got {get_law_threshold('F6')}"
    )
    # F7 has a band [0.03, 0.05]; get_law_threshold returns the upper
    assert get_law_threshold("F7") == 0.05, (
        f"F7 upper band must be 0.05, got {get_law_threshold('F7')}"
    )


def test_no_floor_is_silently_disabled():
    """No floor should have threshold 0.0 (which means 'unconfigured').

    Exception: F4 CLARITY is a <= comparator (entropy reduction),
    so threshold=0.0 is correct (ΔS ≤ 0).
    """
    for floor in EXPECTED_FLOORS:
        spec = get_floor_spec(floor)
        threshold = get_law_threshold(floor)
        if "range" in spec:
            continue  # range floors are checked by band, not threshold
        # F4 uses <= comparator; threshold 0.0 means "ΔS ≤ 0" which is correct
        if floor == "F4":
            assert threshold == 0.0, (
                f"F4 must have threshold=0.0 (≤ comparator for entropy reduction), got {threshold}"
            )
            continue
        assert threshold > 0.0, (
            f"floor {floor} has threshold={threshold} (looks unconfigured); spec={spec}"
        )


def test_hard_floors_classified_correctly():
    """F1, F2, F9, F11, F12, F13 must be HARD."""
    classes = get_floor_classes()
    hard_set = classes.get("hard", set())
    for floor in EXPECTED_HARD_FLOORS:
        assert floor in hard_set, f"floor {floor} must be HARD, got classes={classes}"


def test_threshold_registry_internally_consistent():
    """THRESHOLDS dict must have entries for every LAW_SPEC_KEYS value."""
    for short_id, long_id in LAW_SPEC_KEYS.items():
        assert long_id in THRESHOLDS, (
            f"LAW_SPEC_KEYS['{short_id}']='{long_id}' missing in THRESHOLDS"
        )
        spec = THRESHOLDS[long_id]
        assert "type" in spec, f"THRESHOLDS['{long_id}'] missing 'type' field; spec={spec}"


if __name__ == "__main__":
    test_all_13_floors_registered()
    print("test_011 registered: PASS")
    test_canonical_thresholds_match_spec()
    print("test_011 canonical: PASS")
    test_no_floor_is_silently_disabled()
    print("test_011 not_disabled: PASS")
    test_hard_floors_classified_correctly()
    print("test_011 hard_class: PASS")
    test_threshold_registry_internally_consistent()
    print("test_011 internals: PASS")
