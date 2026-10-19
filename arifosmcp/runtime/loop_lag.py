"""Event-loop lag telemetry (P4c).

AUTHORITY: 888-APEX HOLD verdict 2026-10-19, Commit 1 only.
PURPOSE: make an event-loop block OBSERVABLE instead of inferred (INT -> OBS).
BOUNDARY: diagnostic only. This module is NOT a gate, watchdog, readiness
signal, or heartbeat. It never blocks a request and never changes a verdict.
F12: records the in-flight tool NAME only — never arguments, payloads, SCTs,
tokens, actor ids, or file paths.
"""

from __future__ import annotations

import asyncio
import logging
from collections import deque
from contextvars import ContextVar
from datetime import datetime, timezone

_LOG = logging.getLogger("arifos.loop_lag")

# Tool name is the ONLY context carried across the monitor boundary.
current_tool: ContextVar[str] = ContextVar("arifos_current_tool", default="unknown")

THRESHOLD_MS = 500.0
# 250ms cadence: a 500ms+ block must overshoot a scheduled tick, not slip
# between two 1s samples. Four wakeups/second is negligible load.
INTERVAL_S = 0.25
WINDOW = 60

_lag_ms: deque[float] = deque(maxlen=WINDOW)
_last_ms: float = 0.0
_last_at: str | None = None
_task: asyncio.Task | None = None


def _now_iso() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds").replace("+00:00", "Z")


def record(lag_ms: float) -> None:
    global _last_ms, _last_at
    _last_ms = float(lag_ms)
    _last_at = _now_iso()
    _lag_ms.append(_last_ms)


def snapshot() -> dict:
    """Additive, secret-free telemetry for /health."""
    return {
        "loop_lag_ms": round(_last_ms, 3),
        "loop_lag_max_ms": round(max(_lag_ms), 3) if _lag_ms else 0.0,
        "loop_lag_samples": len(_lag_ms),
        "loop_lag_threshold_ms": THRESHOLD_MS,
        "loop_lag_tool": current_tool.get(),
        "loop_lag_at": _last_at,
    }


def with_loop_lag(payload: dict) -> dict:
    """Return a copy of a health payload with live loop-lag telemetry."""
    out = dict(payload)
    try:
        out["loop_lag"] = snapshot()
    except Exception:  # telemetry must never take down /health
        pass
    return out


async def _monitor() -> None:
    loop = asyncio.get_running_loop()
    next_t = loop.time() + INTERVAL_S
    while True:
        await asyncio.sleep(max(0.0, next_t - loop.time()))
        now = loop.time()
        lag = max(0.0, (now - next_t) * 1000.0)
        next_t = now + INTERVAL_S
        record(lag)
        if lag >= THRESHOLD_MS:
            _LOG.warning(
                "event_loop_lag_exceeded lag_ms=%.1f tool=%s",
                lag,
                current_tool.get(),
            )


def start_monitor() -> None:
    """Idempotent. Safe to call from a Starlette startup handler."""
    global _task
    if _task is not None and not _task.done():
        return
    try:
        loop = asyncio.get_running_loop()
    except RuntimeError:
        return  # no loop yet (import-time or sync CLI); never spawn a bare task
    _task = loop.create_task(_monitor(), name="arifos-loop-lag-monitor")
