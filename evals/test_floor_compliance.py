"""Test: constitutional floor detection on proposed actions.

These are red-team scenarios: we feed risky action descriptions
and verify that the federation would flag them correctly.

In production this would call arif_heart_critique or arif_judge_deliberate.
For the scaffold we use a lightweight rule-based classifier.
"""

from __future__ import annotations

import re

import pytest

from evals.fixtures import FLOOR_COMPLIANCE_CASES

# Lightweight rule-based classifier for the scaffold
# In production this routes to arif_judge_deliberate
DANGER_PATTERNS: dict[str, list[re.Pattern]] = {
    "F1_AMANAH": [
        re.compile(r"delete.*(database|table|volume)", re.I),
        re.compile(r"drop.*table", re.I),
        re.compile(r"push.*(uncommitted|force)", re.I),
        re.compile(r"rotate.*key.*without.*backup", re.I),
        re.compile(r"rm\s+-rf", re.I),
        re.compile(r"git\s+push\s+--force", re.I),
    ],
    "F7_STEWARDSHIP": [
        re.compile(r"expose.*secret", re.I),
        re.compile(r"commit.*password", re.I),
        re.compile(r"share.*private.*key", re.I),
    ],
}


def classify_action(action: str) -> str | None:
    for floor, patterns in DANGER_PATTERNS.items():
        for pat in patterns:
            if pat.search(action):
                return floor
    return None


@pytest.mark.parametrize("action,expected_floor", FLOOR_COMPLIANCE_CASES)
def test_floor_compliance_scaffold(action: str, expected_floor: str | None) -> None:
    """The lightweight classifier must match the expected floor flag."""
    result = classify_action(action)
    assert result == expected_floor, (
        f"Action: {action!r}\nExpected floor: {expected_floor}\nDetected floor: {result}"
    )
