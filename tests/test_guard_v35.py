# tests/test_guard_v35.py
#
# Tests for guard.py v35Ic verdict handling (888_HOLD and SABAR).

import math
import pytest
from typing import Any, Dict, Optional, Callable

from arifos_core.enforcement.metrics import Metrics
from arifos_core.integration.guards.guard import apex_guardrail, GuardrailError
from arifos_core import EyeSentinel


def _make_compute_metrics(
    truth: float = 0.99,
    delta_s: float = 0.1,
    peace_squared: float = 1.0,
    kappa_r: float = 0.95,
    omega_0: float = 0.04,
    amanah: bool = True,
    tri_witness: float = 0.95,
    psi: float = 1.0,
    ambiguity: Optional[float] = None,
    drift_delta: Optional[float] = None,
    paradox_load: Optional[float] = None,
) -> Callable[[str, str, Dict[str, Any]], Metrics]:
    """Create a compute_metrics function that returns fixed metrics."""

    def compute_metrics(user_input: str, raw_answer: str, context: Dict[str, Any]) -> Metrics:
        return Metrics(
            truth=truth,
            delta_s=delta_s,
            peace_squared=peace_squared,
            kappa_r=kappa_r,
            omega_0=omega_0,
            amanah=amanah,
            tri_witness=tri_witness,
            psi=psi,
            ambiguity=ambiguity,
            drift_delta=drift_delta,
            paradox_load=paradox_load,
        )

    return compute_metrics


class TestGuardV35Verdicts:
    """Test guard.py handles all v35Ic verdicts."""

    def test_guard_returns_raw_answer_on_seal(self) -> None:
        """Guard should return raw answer when verdict is SEAL."""

        @apex_guardrail(
            compute_metrics=_make_compute_metrics(),
        )
        def generate(user_input: str) -> str:
            return "Test response"

        result = generate("Test query")
        assert result == "Test response"

    def test_guard_returns_partial_message_on_partial(self) -> None:
        """Guard should return PARTIAL wrapper when soft floors fail."""

        @apex_guardrail(
            compute_metrics=_make_compute_metrics(peace_squared=0.8),
        )
        def generate(user_input: str) -> str:
            return "Test response"

        result = generate("Test query")
        assert "[PARTIAL]" in result
        assert "Test response" in result

    def test_guard_returns_void_message_on_void(self) -> None:
        """Guard should return VOID refusal when hard floors fail."""

        @apex_guardrail(
            compute_metrics=_make_compute_metrics(truth=0.5),
        )
        def generate(user_input: str) -> str:
            return "Test response"

        result = generate("Test query")
        assert "[VOID]" in result
        assert "refused" in result.lower()

    def test_guard_returns_888_hold_on_extended_failure(self) -> None:
        """Guard should return 888_HOLD when extended floors fail (v35Ic)."""

        @apex_guardrail(
            compute_metrics=_make_compute_metrics(ambiguity=0.5),  # > 0.1 threshold
        )
        def generate(user_input: str) -> str:
            return "Test response"

        result = generate("Test query")
        assert "[888_HOLD]" in result
        assert "judiciary hold" in result.lower() or "clarify" in result.lower()


class TestGuardEyeSentinelIntegration:
    """Tests for @EYE Sentinel wiring in apex_guardrail."""

    def test_guard_uses_eye_sentinel_for_sabar(self) -> None:
        """Guard should return SABAR when @EYE blocks on a hard-floor issue such as Amanah breach."""
        sentinel = EyeSentinel()

        @apex_guardrail(
            compute_metrics=_make_compute_metrics(amanah=False),
            eye_sentinel=sentinel,
        )
        def generate(user_input: str) -> str:
            # Amanah=False should trigger FloorView BLOCK -> SABAR via eye_blocking
            return "Test response"

        result = generate("Test query")
        assert "[SABAR]" in result
        assert "Stop. Acknowledge. Breathe. Adjust. Resume." in result


class TestGuardEdgeCases:
    """Test guard.py handles edge cases properly."""

    def test_guard_raises_error_without_compute_metrics(self) -> None:
        """Guard should raise GuardrailError if compute_metrics is None."""
        with pytest.raises(GuardrailError):

            @apex_guardrail(
                compute_metrics=None,
            )
            def generate(user_input: str) -> str:
                return "Test response"

    def test_guard_extracts_user_input_from_args(self) -> None:
        """Guard should extract user_input from positional args."""

        @apex_guardrail(
            compute_metrics=_make_compute_metrics(),
        )
        def generate(user_input: str) -> str:
            return f"Response to: {user_input}"

        result = generate("Hello")
        assert "Response to: Hello" in result

    def test_guard_extracts_user_input_from_kwargs(self) -> None:
        """Guard should extract user_input from keyword args."""

        @apex_guardrail(
            compute_metrics=_make_compute_metrics(),
        )
        def generate(user_input: str) -> str:
            return f"Response to: {user_input}"

        result = generate(user_input="Hello")
        assert "Response to: Hello" in result

    def test_guard_raises_error_without_user_input(self) -> None:
        """Guard should raise GuardrailError if user_input not provided."""

        @apex_guardrail(
            compute_metrics=_make_compute_metrics(),
        )
        def generate() -> str:
            return "Test response"

        with pytest.raises(GuardrailError):
            generate()


class TestGuardNumericalEdgeCases:
    """Test guard.py handles numerical edge cases."""

    def test_guard_handles_nan_metrics(self) -> None:
        """Guard should return VOID for NaN metrics."""

        @apex_guardrail(
            compute_metrics=_make_compute_metrics(truth=math.nan),
        )
        def generate(user_input: str) -> str:
            return "Test response"

        result = generate("Test query")
        # NaN comparisons return False, so truth check fails -> VOID
        assert "[VOID]" in result

    def test_guard_handles_negative_infinity(self) -> None:
        """Guard should return VOID for -inf metrics."""

        @apex_guardrail(
            compute_metrics=_make_compute_metrics(truth=-math.inf),
        )
        def generate(user_input: str) -> str:
            return "Test response"

        result = generate("Test query")
        assert "[VOID]" in result

    def test_guard_handles_zero_kappa_r(self) -> None:
        """Guard should return VOID or PARTIAL for zero kappa_r."""

        @apex_guardrail(
            compute_metrics=_make_compute_metrics(kappa_r=0.0),
        )
        def generate(user_input: str) -> str:
            return "Test response"

        result = generate("Test query")
        # kappa_r < 0.95 is a soft floor failure
        assert "[PARTIAL]" in result or "[VOID]" in result
