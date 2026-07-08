"""
tests/golden/organs/judge/test_judge_golden.py — 888_JUDGE Golden Contract Tests

Phase 0: Paradox anchors were removed 2026-07-04 (ABC falsifier proved they
only enriched meta, never affected VerdictCode). Tests updated to verify
the sentinel and that judge.py still imports cleanly.

DITEMPA BUKAN DIBERI — Forged, Not Given
"""

from __future__ import annotations

import pytest


class TestJudgeAnchorRegistry:
    """Verify paradox anchors were intentionally removed, not accidentally lost."""

    def test_paradox_anchors_removed_sentinel(self):
        """The sentinel flag confirms intentional removal, not accidental deletion."""
        from arifosmcp.tools.judge import PARADOX_ANCHORS_REMOVED_TO_CANON

        assert PARADOX_ANCHORS_REMOVED_TO_CANON is True

    def test_judge_module_imports_cleanly(self):
        """Judge module must import without error despite anchor removal."""
        import arifosmcp.tools.judge as judge_mod

        # Verify the module has the expected public surface
        assert hasattr(judge_mod, "PARADOX_ANCHORS_REMOVED_TO_CANON")

    def test_removed_symbols_do_not_exist(self):
        """The old symbols must NOT be re-importable — they are canon, not runtime."""
        import arifosmcp.tools.judge as judge_mod

        removed = [
            "JUDGE_PARADOX_ANCHORS",
            "_JUDGE_BY_CELL",
            "_JUDGE_BY_ID",
            "_inject_judge_paradox",
            "_judge_paradox_for_verdict",
        ]
        for symbol in removed:
            assert not hasattr(judge_mod, symbol), (
                f"{symbol} was removed 2026-07-04 but reappeared. "
                "Check docs/canon/paradox_anchors.md for the preserved canon."
            )
