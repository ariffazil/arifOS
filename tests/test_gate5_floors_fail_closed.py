"""
tests/test_gate5_floors_fail_closed.py — GATE 5 (FLOORS) fail-closed regression
═══════════════════════════════════════════════════════════════════════════════

Regression guard for the latent fail-open in
``GovernancePipeline._gate_floors``.

Defect (2026-09-21): the ``except ImportError`` branch of ``_gate_floors``
returned ``GateResult(passed=True, reason="check_laws not available — soft pass
(degraded mode)")``. So an unavailable floor module turned "13 floors active"
into "floors not evaluated" *while the pipeline still emitted a pass-shaped
result* — verdict PASS, all_clear True, blocked_at None.

Latent, not a live outage: ``from arifosmcp.runtime.law import check_laws``
resolves in a complete install (including with ARIFOS_ML_FLOORS=0). It fires
only when the import chain (law.py → constitutional_map, semantic_gate) breaks:
a partial install, a missing optional dependency, or a packaging omission.
The expensive failure mode is exactly the quiet one: a broken install that keeps
reporting PASS.

Correct behaviour — the direct precedent in the same file is
``_gate_godel_closure``, which FAILS CLOSED when ``_GODEL_LOCK_GATE_AVAILABLE``
is False ("unverified self-certification protection cannot be guaranteed → HOLD
action"). GATE 5 is the primary floor gate and was the inconsistency.

DITEMPA BUKAN DIBERI — the primary gate tested absent, not assumed present.
"""

import sys

import pytest

import arifosmcp.runtime.governance_pipeline as gp
from arifosmcp.runtime.governance_pipeline import (
    Gate,
    GateResult,
    GovernancePipeline,
    PipelineVerdict,
    ToolCallContext,
)

FLOOR_MODULE = "arifosmcp.runtime.law"


# ═══════════════════════════════════════════════════════════════════════════════
# FIXTURES
# ═══════════════════════════════════════════════════════════════════════════════


def _floor_ctx() -> ToolCallContext:
    """A benign context that passes the floor check when the module resolves."""
    return ToolCallContext(
        tool_name="arif_mind_reason",
        session_id="floor-gate-fc-session",
        actor_id="arif",
        action_class="ANALYZE",
    )


def _pipeline() -> GovernancePipeline:
    """Pipeline with only GATE 5 and the cheap prerequisite gates live."""
    return GovernancePipeline(
        f0_rootkey_enabled=False,
        f13_gate_enabled=False,
        vault_liveness_enabled=False,
        drift_enabled=False,
        floor_enabled=True,
    )


@pytest.fixture
def floor_module_unavailable(monkeypatch):
    """Force ``from arifosmcp.runtime.law import check_laws`` to raise ImportError.

    A ``None`` entry in ``sys.modules`` makes the import system raise
    ImportError for that module name — the same error class a partial install,
    a missing optional dependency, or a packaging omission produces. monkeypatch
    restores the real module afterwards.
    """
    monkeypatch.setitem(sys.modules, FLOOR_MODULE, None)
    yield


@pytest.fixture
def floor_module_available():
    """Control: the floor module resolves and check_laws is importable."""
    pytest.importorskip(FLOOR_MODULE)
    from arifosmcp.runtime.law import check_laws  # noqa: F401
    yield


# ═══════════════════════════════════════════════════════════════════════════════
# (a) FORCED IMPORT ERROR → FAIL CLOSED
# ═══════════════════════════════════════════════════════════════════════════════


class TestFloorsGateFailsClosed:
    def test_floor_module_unavailable_does_not_pass(self, floor_module_unavailable):
        """An unavailable floor module must not yield a passed GateResult."""
        result = _pipeline()._gate_floors(_floor_ctx())

        assert result.passed is False, (
            "GATE 5 fail-open regression: _gate_floors returned passed=True "
            f"while the floor module was unavailable (reason={result.reason!r})"
        )
        assert result.gate == Gate.FLOORS
        assert "FAIL-CLOSED" in result.reason
        assert "not evaluated" in result.reason

    def test_floor_module_unavailable_not_seal_shaped(self, floor_module_unavailable):
        """The pipeline must HOLD, not emit a SEAL/PASS-shaped verdict.

        PipelineVerdict carries no SEAL member (PASS/WARN/HOLD/VOID); the
        SEAL-shaped outcome available to this pipeline is PASS. Both are
        excluded explicitly so a future SEAL member cannot silently satisfy
        this guard.
        """
        res = _pipeline().run(_floor_ctx())

        assert res.verdict not in ("SEAL", "PASS"), (
            f"GATE 5 fail-open regression: verdict={res.verdict!r} on an "
            "unevaluated primary floor gate"
        )
        assert res.verdict == PipelineVerdict.HOLD
        assert res.all_clear is False, "all_clear must be False when floors were not evaluated"
        assert res.blocked_at == Gate.FLOORS

        floor_gates = [g for g in res.gate_results if g.gate == Gate.FLOORS]
        assert len(floor_gates) == 1
        assert floor_gates[0].passed is False

    def test_floor_module_unavailable_carries_no_violation_claim(
        self, floor_module_unavailable
    ):
        """Fail-closed must not invent violated laws — the floors never ran."""
        result = _pipeline()._gate_floors(_floor_ctx())

        assert result.metadata.get("violated_laws") == []
        assert result.metadata.get("output_policy") == "HOLD"

    def test_exception_branch_still_fails_closed(self, monkeypatch):
        """Pre-existing behaviour preserved: a runtime error in check_laws HOLDs."""
        import arifosmcp.runtime.law as law

        def _boom(*_args, **_kwargs):
            raise RuntimeError("synthetic floor engine failure")

        monkeypatch.setattr(law, "check_laws", _boom)
        result = _pipeline()._gate_floors(_floor_ctx())

        assert result.passed is False
        assert "Floor check error" in result.reason


# ═══════════════════════════════════════════════════════════════════════════════
# (b) DEGRADED-MODE MARKER ON METADATA
# ═══════════════════════════════════════════════════════════════════════════════


class TestDegradedMarker:
    def test_metadata_distinguishes_not_evaluated_from_passed(
        self, floor_module_unavailable
    ):
        """A downstream reader must be able to tell 'floors passed' from
        'floors could not be evaluated'."""
        result = _pipeline()._gate_floors(_floor_ctx())

        assert isinstance(result, GateResult)
        assert result.metadata.get("degraded") is True
        assert result.metadata.get("floors_evaluated") is False

    def test_control_passed_result_has_no_floor_marker(self, floor_module_available):
        """The normal pass path stays clean — metadata is not polluted with a
        marker that would make a real pass look degraded."""
        result = _pipeline()._gate_floors(_floor_ctx())

        assert result.passed is True
        assert result.metadata.get("floors_evaluated") is None
        assert result.metadata.get("degraded") is None


# ═══════════════════════════════════════════════════════════════════════════════
# (c) CONTROL — NORMAL FLOOR BEHAVIOUR UNCHANGED
# ═══════════════════════════════════════════════════════════════════════════════


class TestControlImportSucceeds:
    def test_import_succeeds_floors_still_pass(self, floor_module_available):
        """With the module importable, GATE 5 behaves exactly as before."""
        p = _pipeline()
        result = p._gate_floors(_floor_ctx())

        assert result.passed is True
        assert result.reason == "All floors passed"

    def test_import_succeeds_pipeline_still_reaches_floor_gate(self, floor_module_available):
        """The full pipeline still evaluates GATE 5 (no gate-order change)."""
        res = _pipeline().run(_floor_ctx())

        floor_gates = [g for g in res.gate_results if g.gate == Gate.FLOORS]
        assert len(floor_gates) == 1
        assert floor_gates[0].passed is True
        assert floor_gates[0].reason == "All floors passed"

    def test_floor_enabled_false_still_skips_gate(self):
        """floor_enabled=False is an explicit opt-out and is unaffected."""
        p = GovernancePipeline(floor_enabled=False)
        res = p.run(_floor_ctx())

        assert [g for g in res.gate_results if g.gate == Gate.FLOORS] == []


# ═══════════════════════════════════════════════════════════════════════════════
# PRECEDENT CONSISTENCY — GATE 5 now matches the Gödel gate
# ═══════════════════════════════════════════════════════════════════════════════


class TestMatchesGodelPrecedent:
    def test_both_primary_gates_fail_closed_when_unavailable(self, monkeypatch):
        """The sibling precedent: _gate_godel_closure HOLDs when its gate module
        is unavailable. GATE 5 must agree with it."""
        monkeypatch.setitem(sys.modules, FLOOR_MODULE, None)
        monkeypatch.setattr(gp, "_GODEL_LOCK_GATE_AVAILABLE", False)

        floors = _pipeline()._gate_floors(_floor_ctx())
        godel = gp.GovernancePipeline()._gate_godel_closure(_floor_ctx())

        assert floors.passed is False
        assert godel.passed is False
        assert "fail-closed" in godel.reason.lower()
        assert "FAIL-CLOSED" in floors.reason
