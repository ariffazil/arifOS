"""
tests/runtime/test_honesty_hotfix.py — Unit tests for the honest capability hotfix bundle.

Each test exercises a pure function. No network, no subprocess side effects beyond
a controlled `git rev-parse` invocation in a temporary repo (created with
`git init` in tmp_path). No live runtime touched.

DITEMPA BUKAN DIBERI.
"""

from __future__ import annotations

import subprocess
import time
from pathlib import Path

import pytest

from arifosmcp.runtime.honesty_hotfix import (
    CircuitBreaker,
    RANK_TO_VERDICT,
    VERDICT_RANK,
    min_verdict,
    probe_status_self,
    resolve_kernel_version,
)


# ──────────────────────────────────────────────────────────────────────
# Gap 11 — Self-probe SELF status
# ──────────────────────────────────────────────────────────────────────


class TestSelfProbe:
    def test_self_status_for_currently_executing_tool(self) -> None:
        result = probe_status_self("arif_forge_execute", "arif_forge_execute", is_alive=True)
        assert result["status"] == "SELF"
        assert "Gödel" in result["note"]

    def test_self_status_even_when_alive(self) -> None:
        # The whole point: a tool that is alive but currently executing
        # cannot be attested by itself. SELF wins over ALIGNED.
        result = probe_status_self("arif_session_init", "arif_session_init", is_alive=True)
        assert result["status"] == "SELF"

    def test_aligned_for_other_alive_tool(self) -> None:
        result = probe_status_self("arif_forge_execute", "arif_session_init", is_alive=True)
        assert result["status"] == "ALIGNED"
        assert result["tool"] == "arif_forge_execute"

    def test_dead_for_unresponsive_other_tool(self) -> None:
        result = probe_status_self("arif_forge_execute", "arif_session_init", is_alive=False)
        assert result["status"] == "DEAD"

    def test_no_currently_executing_falls_through_normally(self) -> None:
        result = probe_status_self("arif_forge_execute", None, is_alive=True)
        assert result["status"] == "ALIGNED"


# ──────────────────────────────────────────────────────────────────────
# Gap 7 — MIN() verdict invariant
# ──────────────────────────────────────────────────────────────────────


class TestMinVerdict:
    def test_wrapper_cannot_upgrade_hold_to_seal(self) -> None:
        # This is the bug the 06-07 audit caught.
        assert min_verdict("HOLD", "SEAL") == "HOLD"

    def test_wrapper_cannot_upgrade_seal_to_hold_is_impossible(self) -> None:
        # SEAl is already the highest; if inner is SEAL, wrapper HOLD does not downgrade it.
        assert min_verdict("SEAL", "HOLD") == "HOLD"  # wrapper SEAL < inner HOLD
        # Wait — let me check: inner=SEAL(5), wrapper=HOLD(2). min=2 = HOLD. Correct.
        # The wrapper wins because it says HOLD. The inner saying SEAL is overridden
        # by the wrapper's downgrade signal. That is the correct structural behavior:
        # the wrapper is the OUTER witness; it may forbid the inner's claim.

    def test_equal_verdicts_pass_through(self) -> None:
        for v in VERDICT_RANK:
            assert min_verdict(v, v) == v

    def test_void_wins_over_seal(self) -> None:
        # VOID is the strongest negative signal. If inner is VOID, no SEAL can hide it.
        assert min_verdict("VOID", "SEAL") == "VOID"

    def test_unknown_inner_raises(self) -> None:
        with pytest.raises(ValueError):
            min_verdict("BOGUS", "SEAL")

    def test_unknown_wrapper_raises(self) -> None:
        with pytest.raises(ValueError):
            min_verdict("SEAL", "BOGUS")

    def test_all_pairs_no_upgrade(self) -> None:
        """
        Property: for every (inner, wrapper) pair, min_verdict(inner, wrapper)
        has rank ≤ rank(inner) and rank ≤ rank(wrapper). The wrapper never
        produces a higher-ranked final verdict than either input.
        """
        for inner in VERDICT_RANK:
            for wrapper in VERDICT_RANK:
                result = min_verdict(inner, wrapper)
                assert VERDICT_RANK[result] <= VERDICT_RANK[inner]
                assert VERDICT_RANK[result] <= VERDICT_RANK[wrapper]


# ──────────────────────────────────────────────────────────────────────
# Gap 12 — Build-time git hash injection
# ──────────────────────────────────────────────────────────────────────


class TestKernelVersion:
    def test_env_var_wins(self, monkeypatch: pytest.MonkeyPatch) -> None:
        monkeypatch.setenv("ARIFOS_KERNEL_VERSION", "kanon-test123")
        assert resolve_kernel_version() == "kanon-test123"

    def test_falls_back_to_git(self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
        monkeypatch.delenv("ARIFOS_KERNEL_VERSION", raising=False)
        # Make a tiny git repo
        subprocess.check_call(
            ["git", "init", str(tmp_path)], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL
        )
        subprocess.check_call(
            ["git", "-C", str(tmp_path), "config", "user.email", "test@example.com"],
            stdout=subprocess.DEVNULL,
        )
        subprocess.check_call(
            ["git", "-C", str(tmp_path), "config", "user.name", "Test"],
            stdout=subprocess.DEVNULL,
        )
        (tmp_path / "f").write_text("x")
        subprocess.check_call(
            ["git", "-C", str(tmp_path), "add", "f"],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
        )
        subprocess.check_call(
            ["git", "-C", str(tmp_path), "commit", "-m", "init"],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
        )
        sha = (
            subprocess.check_output(
                ["git", "-C", str(tmp_path), "rev-parse", "--short", "HEAD"],
            )
            .decode()
            .strip()
        )

        # Patch the known repo paths to include this tmp_path
        from arifosmcp.runtime import honesty_hotfix

        original = honesty_hotfix._KNOWN_REPO_PATHS
        honesty_hotfix._KNOWN_REPO_PATHS = (tmp_path,) + original
        try:
            result = resolve_kernel_version()
        finally:
            honesty_hotfix._KNOWN_REPO_PATHS = original
        assert result == f"kanon-{sha}"
        # Crucially: it is NOT the placeholder.
        assert result != "version-unresolved"
        assert "unknown" not in result

    def test_never_returns_kanon_unknown(self, monkeypatch: pytest.MonkeyPatch) -> None:
        # Even with all envs cleared and no git, it must not produce kanon-unknown.
        monkeypatch.delenv("ARIFOS_KERNEL_VERSION", raising=False)
        from arifosmcp.runtime import honesty_hotfix

        original = honesty_hotfix._KNOWN_REPO_PATHS
        honesty_hotfix._KNOWN_REPO_PATHS = ()  # type: ignore[assignment]
        try:
            result = resolve_kernel_version()
        finally:
            honesty_hotfix._KNOWN_REPO_PATHS = original
        assert result != "kanon-unknown"
        assert result == "version-unresolved"


# ──────────────────────────────────────────────────────────────────────
# Gap 3 (partial) — Circuit breaker
# ──────────────────────────────────────────────────────────────────────


class TestCircuitBreaker:
    def test_closed_breaker_passes_through(self) -> None:
        cb = CircuitBreaker(name="test")
        result = cb.call(lambda: {"ok": True})
        assert result == {"ok": True}
        assert cb.state == "closed"

    def test_one_failure_increments_strikes(self) -> None:
        cb = CircuitBreaker(strike_limit=3, name="test")
        result = cb.call(self._raise)
        assert result["status"] == "STALE"
        assert result["strikes"] == 1
        assert cb.state == "closed"

    def test_three_failures_open_breaker(self) -> None:
        cb = CircuitBreaker(strike_limit=3, name="test")
        cb.call(self._raise)
        cb.call(self._raise)
        result = cb.call(self._raise)
        assert result["status"] == "DEAD"
        assert result["tri_witness"] == "2/3_DEGRADED"
        assert cb.state == "open"

    def test_open_breaker_short_circuits(self) -> None:
        cb = CircuitBreaker(strike_limit=2, backoff_base=10, name="test")
        cb.call(self._raise)
        cb.call(self._raise)
        # Now open. Next call should short-circuit.
        result = cb.call(lambda: {"ok": True})
        assert result["status"] == "DEAD"
        assert result["reason"] == "circuit_open"
        assert "retry_in_s" in result
        assert result["retry_in_s"] > 0
        assert cb.state == "open"

    def test_open_breaker_eventually_half_opens(self) -> None:
        cb = CircuitBreaker(strike_limit=2, backoff_base=1.1, backoff_cap_s=2, name="test")
        cb.call(self._raise)
        cb.call(self._raise)
        # Wait for backoff to expire
        time.sleep(1.5)
        result = cb.call(lambda: {"ok": True})
        assert result == {"ok": True}
        assert cb.state == "closed"

    def test_open_breaker_reopens_on_half_open_failure(self) -> None:
        cb = CircuitBreaker(strike_limit=2, backoff_base=1.1, backoff_cap_s=2, name="test")
        cb.call(self._raise)
        cb.call(self._raise)
        time.sleep(1.5)
        result = cb.call(self._raise)
        assert result["status"] == "DEAD"
        assert cb.state == "open"

    @staticmethod
    def _raise() -> None:
        raise ConnectionError("geox unreachable")
