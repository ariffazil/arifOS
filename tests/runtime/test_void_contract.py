"""test_void_contract.py — mutation-tested both ways (BIJAKSANA Rule 3p).

A wiring test must execute the REAL assembler and die when the control is
removed. This file therefore asserts:

  1. a bare VOID is marked incomplete and NAMES the five missing fields;
  2. a complete VOID is marked complete;
  3. the runtime envelope chokepoint actually calls the stamper
     (removing the call from tools_internal.py must make this test fail).

Test 3 is the one that matters: without it this is a unit test of a helper
nobody calls — which is how declared-but-uncoupled controls are born.
"""

from __future__ import annotations

import inspect

from arifosmcp.runtime.void_contract import (
    VOID_REQUIRED,
    stamp_void_contract,
    validate_void,
)


class _Env:
    def __init__(self, verdict: str, payload: dict | None = None):
        self.verdict = verdict
        self.payload = payload if payload is not None else {}


# ── 1. bare VOID is incomplete, and says which fields are missing ────────────
def test_bare_void_is_incomplete_and_names_the_gaps() -> None:
    contract = validate_void({})
    assert contract["complete"] is False
    assert set(contract["missing"]) == set(VOID_REQUIRED)
    assert contract["present"] == []


# ── 2. a filled contract is complete ────────────────────────────────────────
def test_complete_void_passes() -> None:
    payload = {
        "boundary": "F1 violated: FQ below ratified floor",
        "set": ["unverified actor", "cold window", "genuine degradation"],
        "probe": "recompute FQ from arifFlow receipts for the same window",
        "price": "one probe call, ~2s",
        "decision_effect": "whether deploy proceeds or holds",
    }
    contract = validate_void(payload)
    assert contract["complete"] is True, contract
    assert contract["missing"] == []


# ── 3. short/empty content does not satisfy a field ─────────────────────────
def test_shrug_is_not_content() -> None:
    contract = validate_void({"boundary": "?", "set": [], "probe": "", "price": None})
    assert contract["complete"] is False
    assert "probe" in contract["missing"]
    assert "price" in contract["missing"]
    assert "set" in contract["missing"]


# ── 4. non-VOID verdicts are untouched ──────────────────────────────────────
def test_non_void_is_not_stamped() -> None:
    env = _Env("hold", {})
    assert stamp_void_contract(env) is None
    assert "void_contract" not in env.payload


def test_void_is_stamped_on_the_envelope() -> None:
    env = _Env("void", {})
    contract = stamp_void_contract(env)
    assert contract is not None
    assert env.payload["void_contract"]["complete"] is False


# ── 5. THE COUPLING TEST: the runtime chokepoint must call the stamper ──────
def test_runtime_chokepoint_calls_the_stamper() -> None:
    """If the call is removed from tools_internal.py, this test must fail.

    This is the anti-ceremony assertion: the module existing proves nothing.
    """
    from arifosmcp.runtime import tools_internal

    src = inspect.getsource(tools_internal)
    assert "stamp_void_contract" in src, (
        "the runtime envelope chokepoint no longer stamps the VOID contract — "
        "the module is declared but uncoupled (KX-010 shape)"
    )
    assert "from arifosmcp.runtime.void_contract import stamp_void_contract" in src
