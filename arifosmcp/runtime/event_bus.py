"""
arifosmcp/runtime/event_bus.py — Constitutional Event Bus
═══════════════════════════════════════════════════════════════════════════════

Lightweight in-memory event bus for broadcasting governance events.
Observatory consumes from this bus via SSE.

CRITICAL: Events broadcast here are SANITIZED.
No secrets, no HMAC, no private payloads, no tokens.
Only verdicts, trace_ids, sources, and safe metadata.

DITEMPA BUKAN DIBERI — Forged, Not Given
"""

from __future__ import annotations

import asyncio
import logging
from collections import deque
from datetime import datetime, timezone
from typing import Any

logger = logging.getLogger(__name__)

# Bounded in-memory ring buffer for recent events
_MAX_BUFFER = 10_000
_event_buffer: deque[dict[str, Any]] = deque(maxlen=_MAX_BUFFER)

# Set of active SSE queues
_listeners: set[asyncio.Queue[dict[str, Any]]] = set()
_listener_lock = asyncio.Lock()


# ── Public API ────────────────────────────────────────────────────────────────


async def emit_event(event: dict[str, Any]) -> None:
    """
    Emit a sanitized governance event to all connected SSE listeners.

    Safe fields only:
        - trace_id
        - verdict
        - source
        - event_type
        - actor (sanitized)
        - timestamp
        - routing.action
        - confidence
        - issue_count
        - policy_version
        - approval_status
        - seal_required
        - vault_entry_id
        - chain_hash
        - observation_only
    """
    sanitized = _sanitize_event(event)
    _event_buffer.append(sanitized)

    async with _listener_lock:
        dead: set[asyncio.Queue] = set()
        for queue in _listeners:
            try:
                queue.put_nowait(sanitized)
            except asyncio.QueueFull:
                dead.add(queue)
            except Exception as e:
                logger.debug("Event bus queue error: %s", e)
                dead.add(queue)
        for queue in dead:
            _listeners.discard(queue)


def emit_event_sync(event: dict[str, Any]) -> None:
    """Synchronous wrapper for emit_event. Schedules on running loop or drops."""
    try:
        loop = asyncio.get_running_loop()
        loop.call_soon(lambda: asyncio.create_task(emit_event(event)))
    except RuntimeError:
        # No event loop running — log and drop (acceptable for startup edge cases)
        logger.debug("Event bus: no running loop, event dropped: %s", event.get("trace_id"))


async def subscribe() -> asyncio.Queue[dict[str, Any]]:
    """Create a new subscriber queue and seed with recent history."""
    queue: asyncio.Queue[dict[str, Any]] = asyncio.Queue(maxsize=256)
    async with _listener_lock:
        _listeners.add(queue)
    # Seed with last N events so new connections don't start empty
    for ev in list(_event_buffer)[-50:]:
        try:
            queue.put_nowait(ev)
        except asyncio.QueueFull:
            break
    return queue


async def unsubscribe(queue: asyncio.Queue[dict[str, Any]]) -> None:
    """Remove a subscriber queue."""
    async with _listener_lock:
        _listeners.discard(queue)


def get_recent_events(n: int = 100) -> list[dict[str, Any]]:
    """Return the N most recent events from the buffer."""
    return list(_event_buffer)[-n:]


# ── Internal ──────────────────────────────────────────────────────────────────


_SAFE_KEYS = {
    "trace_id",
    "verdict",
    "source",
    "event_type",
    "actor",
    "timestamp",
    "confidence",
    "reversibility",
    "routing",
    "event_id",
    "rate_limit",
    "policy_version",
    "approval_status",
    "seal_required",
    "vault_entry_id",
    "chain_hash",
    "observation_only",
}


def _sanitize_event(raw: dict[str, Any]) -> dict[str, Any]:
    """Strip everything except safe keys. Never leak payload, HMAC, or secrets."""
    safe: dict[str, Any] = {k: v for k, v in raw.items() if k in _SAFE_KEYS}
    safe["issue_count"] = len(raw.get("issues", []))
    safe["_event_kind"] = "webhook_intake"
    safe["_emitted_at"] = datetime.now(timezone.utc).isoformat()
    safe["observation_only"] = True
    return safe
