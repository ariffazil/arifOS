"""F13 sovereign receipt must not rewrite unresolved HOLD into SEAL.

APEX integrity regression (2026-07-30): commit 298ef83 introduced
`(action_tier in (...) or True)` which made the action-tier check
always true, and the block promoted HOLD→SEAL whenever a sovereign
receipt was present.

Constitutional law:
  - F13 receipt authorizes a *passed* judgment.
  - HOLD stays HOLD; SEAL emerges only from a passed judgment.
  - No `or True` bypass. No empty-string "safe" defaults for rev/blast.
"""

from __future__ import annotations

import ast
import inspect
from pathlib import Path

import pytest

JUDGE_PATH = Path(__file__).resolve().parents[1] / "arifosmcp" / "tools" / "judge.py"


def test_source_has_no_or_true_tier_bypass() -> None:
    src = JUDGE_PATH.read_text(encoding="utf-8")
    assert "action_tier in (" in src
    # Exact constitutional defect pattern must stay gone
    assert "or True)" not in src or "or True)" not in [
        line for line in src.splitlines() if "action_tier" in line
    ]
    for line in src.splitlines():
        if "action_tier" in line and "or True" in line and not line.strip().startswith("#"):
            pytest.fail(f"action_tier bypass present: {line.strip()}")


def test_source_rejects_hold_promotion_marker() -> None:
    src = JUDGE_PATH.read_text(encoding="utf-8")
    assert "f13_does_not_promote_hold" in src
    assert "HOLD→SEAL under sovereign receipt" not in src


def test_f13_block_ast_never_assigns_seal_from_hold_branch() -> None:
    """HOLD may appear only as a *non-promotion* class (record receipt, leave
    verdict). It must not appear together with ALLOW/OK in a set that then
    assigns verdict SEAL.
    """
    src = JUDGE_PATH.read_text(encoding="utf-8")
    for line in src.splitlines():
        stripped = line.strip()
        if stripped.startswith("#"):
            continue
        # Forbidden: promotable set that still includes HOLD (old 298ef83 shape)
        if "HOLD" in stripped and ("ALLOW" in stripped or "OK" in stripped):
            if "_v_now in" in stripped or "verdict" in stripped.lower():
                if "does_not_promote" in stripped:
                    continue
                pytest.fail(
                    "HOLD must not share a promotable-verdict set with "
                    f"ALLOW/OK: {stripped}"
                )


def test_judge_module_parses() -> None:
    src = JUDGE_PATH.read_text(encoding="utf-8")
    ast.parse(src)
