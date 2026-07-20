"""
arifosmcp.runtime.mcp_logging — MCP logging utility (FREEZE — SEP-2577)

SEP-2577 Final: logging/setLevel + notifications/message are deprecated.
Do NOT add new call sites or expand this module. Maintenance-only.

Canonical ops path: stderr + structured receipts + mcp_log_bridge HOLD_CANDIDATE.

Still valid while deprecated: declare before emit; scrub; rate limit; stderr always.
"""

from __future__ import annotations

import logging
import re
import sys
import time
from collections.abc import Mapping
from typing import Any

_stderr = logging.getLogger("arifos.mcp_log")
if not _stderr.handlers:
    _h = logging.StreamHandler(sys.stderr)
    _h.setFormatter(logging.Formatter("%(asctime)s %(levelname)s [arifos.mcp] %(message)s"))
    _stderr.addHandler(_h)
    _stderr.setLevel(logging.DEBUG)
    _stderr.propagate = False

# RFC 5424 levels accepted by MCP (ordered least → most severe)
_LEVEL_ORDER: tuple[str, ...] = (
    "debug",
    "info",
    "notice",
    "warning",
    "error",
    "critical",
    "alert",
    "emergency",
)
_LEVELS = frozenset(_LEVEL_ORDER)
_LEVEL_RANK = {name: i for i, name in enumerate(_LEVEL_ORDER)}

# Default minimum for MCP client stream when setLevel not sent (zen tip 4).
DEFAULT_MIN_LEVEL = "warning"

# Rate limit: one emit per key within window (zen tip 3 / spec SHOULD)
_RATE_WINDOW_S = 2.0
_rate_last: dict[str, float] = {}

# Scrub keys (case-insensitive substring match) — MUST NOT log secrets/PII (zen tip 5)
_SCRUB_KEY_PARTS = (
    "token",
    "password",
    "secret",
    "authorization",
    "api_key",
    "apikey",
    "private_key",
    "bearer",
    "cookie",
    "session_secret",
    "lease_secret",
    "credit_card",
    "nric",
    "passport",
)
_PATH_RE = re.compile(r"(/(?:root|home|opt|var|etc)/[^\s\"']+)", re.I)


def _rank(level: str) -> int:
    return _LEVEL_RANK.get(level, _LEVEL_RANK["info"])


def _passes_min(level: str, min_level: str) -> bool:
    return _rank(level) >= _rank(min_level)


def _scrub_value(key: str, value: Any) -> Any:
    kl = key.lower()
    if any(p in kl for p in _SCRUB_KEY_PARTS):
        return "[redacted]"
    if isinstance(value, str):
        if len(value) > 200:
            value = value[:200] + "…"
        return _PATH_RE.sub("[path]", value)
    if isinstance(value, dict):
        return {str(k): _scrub_value(str(k), v) for k, v in list(value.items())[:20]}
    if isinstance(value, (list, tuple)):
        return [_scrub_value(key, v) for v in list(value)[:10]]
    return value


def scrub_data(data: Mapping[str, Any]) -> dict[str, Any]:
    """Return a copy safe for MCP log data / stderr tails."""
    return {str(k): _scrub_value(str(k), v) for k, v in data.items()}


def _rate_allow(key: str) -> bool:
    now = time.monotonic()
    last = _rate_last.get(key)
    if last is not None and (now - last) < _RATE_WINDOW_S:
        return False
    _rate_last[key] = now
    # prune occasionally
    if len(_rate_last) > 512:
        cutoff = now - _RATE_WINDOW_S * 4
        for k, t in list(_rate_last.items()):
            if t < cutoff:
                _rate_last.pop(k, None)
    return True


def _resolve_client_min_level() -> str:
    """Session setLevel if present, else DEFAULT_MIN_LEVEL."""
    try:
        from fastmcp.server.dependencies import get_context

        ctx = get_context()
        if ctx is None:
            return DEFAULT_MIN_LEVEL
        session = getattr(ctx, "session", None)
        if session is None:
            return DEFAULT_MIN_LEVEL
        min_level = getattr(session, "_minimum_logging_level", None)
        if min_level:
            return str(min_level).lower()
        fm = getattr(session, "fastmcp", None)
        if fm is not None and getattr(fm, "client_log_level", None):
            return str(fm.client_log_level).lower()
    except Exception:
        pass
    return DEFAULT_MIN_LEVEL


def _stderr_mirror(level: str, message: str, data: Mapping[str, Any] | None) -> None:
    """Always-safe mirror. Never touches stdout."""
    payload = message
    if data:
        bits = " ".join(f"{k}={v!r}" for k, v in list(data.items())[:12])
        payload = f"{message} | {bits}"
    if level in ("emergency", "alert", "critical", "error"):
        _stderr.error(payload)
    elif level == "warning":
        _stderr.warning(payload)
    elif level in ("notice", "info"):
        _stderr.info(payload)
    else:
        _stderr.debug(payload)


async def emit_mcp_log(
    level: str,
    message: str,
    *,
    organ: str = "arifOS",
    tool: str | None = None,
    floor: str | None = None,
    verdict: str | None = None,
    extra: Mapping[str, Any] | None = None,
    logger_name: str = "arifos.judge",
    rate_key: str | None = None,
) -> None:
    """Emit MCP log notification if allowed; always mirror to stderr (ops).

    Fail-soft: never raises into the tool path.
    """
    level_l = (level or DEFAULT_MIN_LEVEL).lower()
    if level_l not in _LEVELS:
        level_l = DEFAULT_MIN_LEVEL

    # Structured constitutional / machine state (zen tip 2)
    data: dict[str, Any] = {"organ": organ}
    if tool:
        data["tool"] = tool
    if floor:
        data["floor"] = floor
    if verdict:
        data["verdict"] = verdict
    if extra:
        data.update(dict(extra))
    data = scrub_data(data)

    # Rate limit (one summary per key) — still stderr-mirror the first only
    rk = rate_key or f"{organ}:{tool or '-'}:{verdict or level_l}:{floor or '-'}"
    if not _rate_allow(rk):
        return

    # Ops always sees stderr (zen tip 6) — unfiltered for operators
    _stderr_mirror(level_l, message, data)

    # Phase 1c: bridge inspects structured data → HOLD_CANDIDATE (never auto-888)
    try:
        from arifosmcp.runtime.mcp_log_bridge import evaluate_and_record

        evaluate_and_record(level=level_l, data=data, message=message)
    except Exception:
        pass

    # Protocol channel FREEZE (SEP-2577): default OFF — stderr + HOLD_CANDIDATE only.
    # Set MCP_PROTOCOL_LOGGING=1 only for legacy client compatibility during deprecation window.
    import os as _os

    _proto = _os.environ.get("MCP_PROTOCOL_LOGGING", "0").strip().lower() in ("1", "true", "yes")
    if not _proto:
        return

    # Client stream: honor setLevel / default warning (zen tip 4)
    min_level = _resolve_client_min_level()
    if not _passes_min(level_l, min_level):
        return

    try:
        from fastmcp.server.dependencies import get_context

        ctx = get_context()
        if ctx is None:
            return
        await ctx.log(
            message,
            level=level_l,  # type: ignore[arg-type]
            logger_name=logger_name,
            extra=data,
        )
    except Exception:
        # Outside request context, or client without logging support — stderr only.
        return


def floor_event_to_level(
    outcome: str,
    *,
    capped: bool = False,
    failed_floors: list[str] | None = None,
) -> str:
    """Map floor outcome → MCP severity (federation constitutional table)."""
    o = (outcome or "").upper()
    failed = failed_floors or []
    if "F13" in failed or o in ("888_HOLD", "SOVEREIGN_HOLD"):
        return "alert"
    if o in ("BLOCK", "BLOCKED"):
        return "critical"
    if o in ("HOLD", "VOID"):
        return "error"
    if capped or o == "WARNING":
        return "warning"
    # Below default client min — still available if setLevel lowers
    return "info"
