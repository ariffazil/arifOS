"""
tests/test_m2_fail_closed_totality.py — M2 acceptance test

Verifies F9 ANTI-HANTU fix 2026-07-31: FloorEvaluator is a total function.
A raising floor (instantiation OR check) must degrade verdict to VOID with
the exception fingerprint recorded in the trace — NOT silently pass.

This test injects a deliberately-raising floor stub and asserts:
  1. The floor appears in `violated_laws` (verdict degrades to VOID).
  2. The exception class+message is in `floor_reasons[floor_label]`.
  3. The overall LawResult.verdict is VOID.

DITEMPA BUKAN DIBERI — Forged, Not Given.
"""

from __future__ import annotations

import sys
from pathlib import Path
from unittest.mock import MagicMock

import pytest

# Make sure the source tree is importable.
ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from arifosmcp.core.law_evaluator import FloorEvaluator  # noqa: E402
from arifosmcp.core.threat_engine import (  # noqa: E402
    IrreversibilityLevel,
    ThreatAssessment,
    ThreatCategory,
)


def _stub_context() -> MagicMock:
    """Build a MagicMock that satisfies FloorEvaluator._floor_context reads.

    Every attribute access returns a benign default. Specific tests override
    individual floor classes via monkeypatch — the context stays neutral.
    """
    ctx = MagicMock(spec=[])
    # Explicit defaults for fields _floor_context reads:
    ctx.tool_name = "arif_observe"
    ctx.mode = "fetch"
    ctx.actor_id = "test-actor"
    ctx.session_id = "test-session"
    ctx.target_agent = None
    ctx.session_registry = set()
    ctx.federation_registry = set()
    ctx.constitutional_chain_id = None
    ctx.ack_irreversible = False
    ctx.auth_token = ""
    ctx.witness_type = "ai"
    ctx.verification_surface = None
    ctx.query = ""
    ctx.regulation = 1.0
    ctx.trust = 1.0
    ctx.payload_text = lambda: ""
    return ctx


def _low_threat() -> ThreatAssessment:
    return ThreatAssessment(
        threats={ThreatCategory.FILESYSTEM_DESTRUCTIVE},
        irreversibility=IrreversibilityLevel.LOW,
        confidence=0.1,
        reasoning=[],
    )


def _critical_threat() -> ThreatAssessment:
    """A CRITICAL-irreversibility threat — guarantees VOID verdict when
    any floor fails (per FloorEvaluator.is_void logic at the verdict
    branch: threat.irreversibility == CRITICAL triggers is_void=True).
    """
    return ThreatAssessment(
        threats={ThreatCategory.FILESYSTEM_DESTRUCTIVE},
        irreversibility=IrreversibilityLevel.CRITICAL,
        confidence=0.9,
        reasoning=["critical action"],
    )


# ── Test 1: a floor that raises during instantiation → VOID + trace ─────────

class _RaisingOnInit:
    """Stub floor class that raises the moment it's instantiated."""
    def __init__(self):
        raise RuntimeError("forced raise on instantiation (M2 test)")


def test_raising_floor_instantiation_degrades_to_void(monkeypatch):
    """A floor that raises on instantiation MUST be recorded as VOID.

    Before M2: _lazy_floor caught the exception and returned None → caller
    skipped the floor → silent pass. This is the fail-open F1/F9 violation.

    After M2: _check_floor catches the exception in a total-function wrapper
    and records the floor as failed with the exception fingerprint.
    """
    monkeypatch.setattr(
        "arifosmcp.core.law_evaluator.F2_Truth",
        _RaisingOnInit,
    )

    result = FloorEvaluator.evaluate(_stub_context(), _critical_threat())

    assert result.verdict == "VOID", (
        f"raising floor on CRITICAL threat did not degrade to VOID: "
        f"got {result.verdict!r}, "
        f"violated_laws={result.violated_laws!r}, "
        f"floor_reasons={result.floor_reasons!r}"
    )

    assert "L02" in result.violated_laws, (
        f"L02 (the raising floor) must be in violated_laws; got "
        f"{result.violated_laws!r}"
    )

    reason = result.floor_reasons.get("L02", "")
    assert "forced raise on instantiation" in reason, (
        f"exception fingerprint must be in floor_reasons[L02]; got {reason!r}"
    )
    assert "RuntimeError" in reason, (
        f"exception class must be in floor_reasons[L02]; got {reason!r}"
    )


# ── Test 2: a floor that raises during .check() → VOID + trace ──────────────

class _HealthyInitButRaisingCheck:
    """Stub floor class that instantiates fine but raises on .check()."""
    def check(self, fc):
        raise ValueError("forced raise on check (M2 test)")


def test_raising_floor_check_degrades_to_void(monkeypatch):
    """A floor that raises inside .check() MUST be recorded as VOID."""
    monkeypatch.setattr(
        "arifosmcp.core.law_evaluator.F3_QuadWitness",
        _HealthyInitButRaisingCheck,
    )

    result = FloorEvaluator.evaluate(_stub_context(), _critical_threat())

    assert result.verdict == "VOID", (
        f"raising floor on CRITICAL threat did not degrade to VOID: "
        f"got {result.verdict!r}"
    )
    assert "L03" in result.violated_laws
    reason = result.floor_reasons.get("L03", "")
    assert "forced raise on check" in reason
    assert "ValueError" in reason


# ── Test 3: the anti-pattern itself — make sure no `except Exception: pass` ─

def test_no_silent_swallow_in_evaluator_source():
    """No `except Exception: pass` patterns remain in law_evaluator.py.

    This is the literal acceptance gate from the M2 brief:
        grep -c "except Exception: pass" core/law_evaluator.py → 0

    We check the SOURCE TEXT directly rather than behaviorally, because
    the bug class is a silent pass — exactly the thing behavior tests
    miss if the surrounding code is wrong.
    """
    src_path = (
        Path(__file__).resolve().parents[1]
        / "arifosmcp"
        / "core"
        / "law_evaluator.py"
    )
    src = src_path.read_text(encoding="utf-8")
    forbidden = "except Exception: pass"
    count = src.count(forbidden)
    assert count == 0, (
        f"found {count} '{forbidden}' patterns in law_evaluator.py — "
        f"silent swallow paths must not exist (M2 fail-closed totality)"
    )


# ── Test 4: a healthy floor still works (regression check) ──────────────────

def test_healthy_floor_still_records_pass():
    """Regression: fail-closed refactor must not break the happy path.

    When no floor raises, the evaluator should run normally and produce
    a result with the same shape as before (violated_laws + floor_reasons).
    """
    result = FloorEvaluator.evaluate(_stub_context(), _low_threat())

    assert hasattr(result, "verdict")
    assert hasattr(result, "violated_laws")
    assert hasattr(result, "floor_reasons")
    assert isinstance(result.violated_laws, list)
    assert isinstance(result.floor_reasons, dict)
    assert result.verdict in {"SEAL", "HOLD", "VOID"}
