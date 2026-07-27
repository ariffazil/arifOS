"""A4: UNMEASURED sentinel type tests.

Test that UNMEASURED cannot be coerced to bool, float, or compared.
"""

from __future__ import annotations

import pytest

from arifosmcp.runtime.unmeasured import (
    UNMEASURED,
    UnmeasuredError,
    coerce_legacy,
    is_unmeasured,
)


class TestUnmeasuredSentinel:
    """A4 compliance: UNMEASURED may never satisfy a floor, never render as 0.0,
    never coerce to pass."""

    def test_is_singleton(self):
        """Identity check works — the sentinel is a singleton."""
        from arifosmcp.runtime.unmeasured import _Unmeasured

        a = _Unmeasured()
        b = _Unmeasured()
        assert a is b
        assert UNMEASURED is _Unmeasured()

    def test_bool_raises(self):
        """UNMEASURED cannot be used in boolean context."""
        with pytest.raises(UnmeasuredError, match="no truth value"):
            bool(UNMEASURED)

    def test_if_raises(self):
        """UNMEASURED cannot be used in if-statements."""
        with pytest.raises(UnmeasuredError):
            if UNMEASURED:  # type: ignore[truthy-function]
                pass  # pragma: no cover

    def test_float_raises(self):
        """UNMEASURED cannot be coerced to float."""
        with pytest.raises(UnmeasuredError, match="not a number"):
            float(UNMEASURED)

    def test_int_raises(self):
        """UNMEASURED cannot be coerced to int."""
        with pytest.raises(UnmeasuredError, match="not a number"):
            int(UNMEASURED)

    def test_lt_raises(self):
        """UNMEASURED cannot be compared with <."""
        with pytest.raises(UnmeasuredError, match="not ordered"):
            UNMEASURED < 0.5

    def test_gt_raises(self):
        """UNMEASURED cannot be compared with >."""
        with pytest.raises(UnmeasuredError, match="not ordered"):
            UNMEASURED > 0.0

    def test_le_raises(self):
        """UNMEASURED cannot be compared with <=."""
        with pytest.raises(UnmeasuredError, match="not ordered"):
            UNMEASURED <= 0.5

    def test_ge_raises(self):
        """UNMEASURED cannot be compared with >=."""
        with pytest.raises(UnmeasuredError, match="not ordered"):
            UNMEASURED >= 0.0

    def test_g_not_raises_with_is_check(self):
        """Identity check `is UNMEASURED` must NOT raise."""
        G = UNMEASURED
        assert G is UNMEASURED
        assert G is not None

    def test_not_equal_to_anything(self):
        """UNMEASURED is not equal to anything, including itself."""
        assert UNMEASURED != UNMEASURED  # intentional — two unknowns aren't equal
        assert UNMEASURED != 0
        assert UNMEASURED != 0.0
        assert UNMEASURED != None  # noqa: E711
        assert UNMEASURED != "UNMEASURED"
        assert UNMEASURED != "anything"

    def test_add_raises(self):
        with pytest.raises(UnmeasuredError):
            UNMEASURED + 1

    def test_sub_raises(self):
        with pytest.raises(UnmeasuredError):
            UNMEASURED - 1

    def test_mul_raises(self):
        with pytest.raises(UnmeasuredError):
            UNMEASURED * 2

    def test_div_raises(self):
        with pytest.raises(UnmeasuredError):
            UNMEASURED / 2

    def test_repr(self):
        assert repr(UNMEASURED) == "UNMEASURED"

    def test_str(self):
        assert str(UNMEASURED) == "UNMEASURED"

    def test_hashable(self):
        """UNMEASURED can be used as a dict key (for sentinel pattern)."""
        d = {UNMEASURED: "sentinel"}
        assert d[UNMEASURED] == "sentinel"

    def test_is_unmeasured_helper(self):
        assert is_unmeasured(UNMEASURED) is True
        assert is_unmeasured("UNMEASURED") is False
        assert is_unmeasured(None) is False
        assert is_unmeasured(0) is False

    def test_coerce_legacy_string(self):
        """Legacy 'UNMEASURED' string converts to sentinel."""
        assert coerce_legacy("UNMEASURED") is UNMEASURED

    def test_coerce_legacy_passthrough(self):
        """Non-UNMEASURED values pass through unchanged."""
        assert coerce_legacy(0.5) == 0.5
        assert coerce_legacy(None) is None
        assert coerce_legacy("hello") == "hello"

    def test_floor_check_raises(self):
        """A4 acceptance: UNMEASURED cannot satisfy a floor check."""

        def floor_check(value):
            return value > 0.7

        with pytest.raises(UnmeasuredError):
            floor_check(UNMEASURED)

    def test_as_string_safe(self):
        """Explicit serialization opt-in is safe."""
        assert UNMEASURED.as_string_safe() == "UNMEASURED"
