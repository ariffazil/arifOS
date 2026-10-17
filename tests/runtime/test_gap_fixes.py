"""G6/G8 regression guards (2026-10-17).

G6: non-canonical verdict tokens (PENDING_L5b, ALIVE) must never sit in a
    verdict field. Unknown tokens collapse to HOLD (fail-closed).
G8: arif_forge preview modes (dry_run/query/recall) are read-only and must
    not be blocked by the coarse OBSERVE_ONLY verb gate.
"""

from __future__ import annotations

import inspect

import pytest

from arifosmcp.runtime.verdict import CANONICAL_VERDICTS, HOLD, _normalize_verdict


@pytest.mark.parametrize(
    "token", ["PENDING_L5b", "ALIVE", "DEGRADED", "DENY", "UNKNOWN", "SYUBHAH", ""]
)
def test_ghost_tokens_collapse_to_canonical(token: str):
    out = _normalize_verdict(token)
    assert out in CANONICAL_VERDICTS


def test_pending_l5b_is_hold_not_verdict():
    assert _normalize_verdict("PENDING_L5b") == HOLD


def test_akal_wiring_does_not_emit_raw_judge_verdict():
    import arifosmcp.core.akal_wiring as akal

    src = inspect.getsource(akal)
    assert '"verdict": result.judge.verdict' not in src, (
        "akal_wiring must normalize judge verdicts before emitting them"
    )
    assert "judge_state" in src


def test_forge_read_only_exemption_present():
    from arifosmcp.runtime import tools as runtime_tools

    src = inspect.getsource(runtime_tools)
    assert "_forge_read_only" in src
    for mode in ("dry_run", "query", "recall"):
        assert f'"{mode}"' in src
