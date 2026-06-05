"""Test: does the Capability Index return the correct tool for a given intent?

This measures the quality of the vector search layer.
A passing eval means agents can reliably discover the right tool
without loading all 97 schemas into prompt context.
"""

from __future__ import annotations

import pytest

from capability_index.store import CapabilityStore
from evals.fixtures import TOOL_ACCURACY_GROUND_TRUTH


@pytest.mark.parametrize("intent,expected_tool", TOOL_ACCURACY_GROUND_TRUTH)
def test_capability_index_top3_accuracy(intent: str, expected_tool: str, capability_store: CapabilityStore) -> None:
    """The correct tool must appear in the top-3 search results."""
    results = capability_store.search(intent, limit=3)
    found = [r.tool_name for r in results]
    assert expected_tool in found, (
        f"Intent: {intent!r}\n"
        f"Expected: {expected_tool}\n"
        f"Got top-3: {found}"
    )


def test_capability_index_count(capability_store: CapabilityStore) -> None:
    """Index must contain all 97 tools (or however many are seeded)."""
    count = capability_store.count()
    assert count >= 90, f"Expected >= 90 tools, got {count}"
