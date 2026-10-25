"""P4c/P4d — event-loop lag telemetry falsifier (888-authorized Commit 1).

RED-FIRST CONTRACT
------------------
On the pre-patch commit this file must fail (module absent). It only proves
something once the module exists and the monitor actually observes a blocked
loop. It is a DIAGNOSTIC test: it does not assert that /health stays fast
(that is Commit 2 / P4a), it asserts that the blocker is made visible.

Evidence labels: OBSERVED_RUNTIME (monitor values), TARGET (health invariant).
"""

import asyncio
import time

from arifosmcp.runtime.loop_lag import snapshot, start_monitor


def test_snapshot_shape_is_additive_and_secret_free():
    s = snapshot()
    assert "loop_lag_ms" in s
    assert "loop_lag_max_ms" in s
    assert "loop_lag_threshold_ms" in s
    assert s["loop_lag_threshold_ms"] == 500.0
    # F12: tool name only. No args, payloads, tokens or paths.
    assert set(s) >= {"loop_lag_tool", "loop_lag_at"}
    assert isinstance(s["loop_lag_tool"], str)


def test_p99_and_process_gauges_are_present():
    """Commit 3 gate inputs must be observable, not inferred."""
    from arifosmcp.runtime.loop_lag import record

    for _ in range(100):
        record(10.0)
    record(900.0)
    s = snapshot()
    assert s["loop_lag_p99_24h_ms"] is not None
    assert s["loop_lag_window_hours"] >= 1
    assert isinstance(s["process_threads"], int) and s["process_threads"] >= 1
    assert isinstance(s["process_fds"], int) and s["process_fds"] >= 1


def test_blocked_loop_is_observed():
    """A synchronous block on the loop MUST be recorded as lag >= threshold."""

    async def scenario() -> dict:
        start_monitor()
        await asyncio.sleep(0.05)
        time.sleep(1.3)  # simulate a long synchronous judge/IO section
        await asyncio.sleep(1.1)  # let the 1s monitor tick observe the drift
        return snapshot()

    s = asyncio.run(scenario())
    assert s["loop_lag_max_ms"] >= 500.0, f"blocked loop not observed: {s}"
