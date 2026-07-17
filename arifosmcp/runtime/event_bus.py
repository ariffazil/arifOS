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
import json
import logging
import os
from collections import deque
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

logger = logging.getLogger(__name__)

# Bounded in-memory ring buffer for recent events
_MAX_BUFFER = 10_000
_event_buffer: deque[dict[str, Any]] = deque(maxlen=_MAX_BUFFER)

# Set of active SSE queues
_listeners: set[asyncio.Queue[dict[str, Any]]] = set()
_listener_lock = asyncio.Lock()

# Durable append-only JSONL bus (F-002 / F-003 substrate)
_DURABLE_BUS_PATH = Path(
    os.environ.get(
        "ARIFOS_DURABLE_EVENT_BUS",
        "/root/.local/share/arifos/event_bus/events.jsonl",
    )
)
_STAGE_ALIASES = {
    "000": "000_INIT",
    "000_INIT": "000_INIT",
    "init": "000_INIT",
    "111": "111_OBSERVE",
    "111_OBSERVE": "111_OBSERVE",
    "observe": "111_OBSERVE",
    "222": "222_EVIDENCE",
    "222_EVIDENCE": "222_EVIDENCE",
    "333": "333_THINK",
    "333_THINK": "333_THINK",
    "think": "333_THINK",
    "444": "444_ROUTE",
    "444_ROUTE": "444_ROUTE",
    "route": "444_ROUTE",
    "555": "555_MEMORY",
    "555_MEMORY": "555_MEMORY",
    "memory": "555_MEMORY",
    "666": "666_CRITIQUE",
    "666_CRITIQUE": "666_CRITIQUE",
    "777": "777_MEASURE",
    "777_MEASURE": "777_MEASURE",
    "888": "888_JUDGE",
    "888_JUDGE": "888_JUDGE",
    "judge": "888_JUDGE",
    "999": "999_RECEIPT",
    "999_RECEIPT": "999_RECEIPT",
    "receipt": "999_RECEIPT",
    "seal": "999_RECEIPT",
    "010": "010_FORGE",
    "010_FORGE": "010_FORGE",
    "forge": "010_FORGE",
}


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
    "stage",
    "tool",
    "success",
    "session_id",
    "lane",
    "organ",
    "receipt_id",
    "status",
}


def _sanitize_event(raw: dict[str, Any]) -> dict[str, Any]:
    """Strip everything except safe keys. Never leak payload, HMAC, or secrets."""
    safe: dict[str, Any] = {k: v for k, v in raw.items() if k in _SAFE_KEYS}
    safe["issue_count"] = len(raw.get("issues", []))
    safe["_event_kind"] = raw.get("event_type") or raw.get("_event_kind") or "webhook_intake"
    safe["_emitted_at"] = datetime.now(UTC).isoformat()
    safe["observation_only"] = True
    return safe


def _append_durable(event: dict[str, Any]) -> None:
    """Append-only JSONL durable bus. Best-effort; never raises to callers."""
    try:
        _DURABLE_BUS_PATH.parent.mkdir(parents=True, exist_ok=True)
        line = json.dumps(event, separators=(",", ":"), default=str) + "\n"
        with open(_DURABLE_BUS_PATH, "a", encoding="utf-8") as fh:
            fh.write(line)
    except Exception as exc:
        logger.debug("durable bus append failed: %s", exc)


def emit_durable_event(event: dict[str, Any]) -> dict[str, Any]:
    """Sanitize, buffer, durable-append, and best-effort SSE broadcast."""
    sanitized = _sanitize_event(event)
    _event_buffer.append(sanitized)
    _append_durable(sanitized)
    try:
        emit_event_sync(sanitized)
    except Exception:
        pass
    return sanitized


def emit_stage_event(
    stage: str,
    *,
    success: bool = True,
    tool: str | None = None,
    session_id: str | None = None,
    actor: str | None = None,
    trace_id: str | None = None,
    lane: str | None = None,
    organ: str = "arifos",
    receipt_id: str | None = None,
    extra: dict[str, Any] | None = None,
) -> dict[str, Any]:
    """Record a metabolism-stage event on the durable bus."""
    canonical = _STAGE_ALIASES.get(stage, stage)
    payload: dict[str, Any] = {
        "event_type": "metabolism_stage",
        "stage": canonical,
        "success": success,
        "tool": tool,
        "session_id": session_id,
        "actor": actor,
        "trace_id": trace_id,
        "lane": lane or organ,
        "organ": organ,
        "receipt_id": receipt_id,
        "timestamp": datetime.now(UTC).isoformat(),
        "verdict": "SEAL" if success else "HOLD",
        "source": "durable_event_bus",
    }
    if extra:
        payload.update({k: v for k, v in extra.items() if k in _SAFE_KEYS})
    return emit_durable_event(payload)


def read_durable_events(limit: int = 5000) -> list[dict[str, Any]]:
    """Read durable JSONL events (newest-last). Tolerates corrupt lines."""
    if not _DURABLE_BUS_PATH.exists():
        return []
    out: list[dict[str, Any]] = []
    try:
        with open(_DURABLE_BUS_PATH, encoding="utf-8") as fh:
            for line in fh:
                line = line.strip()
                if not line:
                    continue
                try:
                    obj = json.loads(line)
                except json.JSONDecodeError:
                    continue
                if isinstance(obj, dict):
                    out.append(obj)
    except Exception as exc:
        logger.debug("durable bus read failed: %s", exc)
        return []
    if limit and len(out) > limit:
        return out[-limit:]
    return out


def stage_counters(limit: int = 5000) -> dict[str, dict[str, Any]]:
    """Aggregate durable bus into per-stage invocation / success counts."""
    stages = [
        "000_INIT",
        "111_OBSERVE",
        "222_EVIDENCE",
        "333_THINK",
        "444_ROUTE",
        "555_MEMORY",
        "666_CRITIQUE",
        "777_MEASURE",
        "888_JUDGE",
        "999_RECEIPT",
        "010_FORGE",
    ]
    counts: dict[str, dict[str, Any]] = {
        s: {"invocations": 0, "success": 0, "fail": 0, "last_tool": None, "last_trace": None}
        for s in stages
    }
    for ev in read_durable_events(limit=limit):
        stage = ev.get("stage")
        if not stage:
            # map tool names to stages when stage omitted
            tool = str(ev.get("tool") or "")
            if tool.startswith("arif_init"):
                stage = "000_INIT"
            elif tool.startswith("arif_observe"):
                stage = "111_OBSERVE"
            elif tool.startswith("arif_think"):
                stage = "333_THINK"
            elif tool.startswith("arif_route"):
                stage = "444_ROUTE"
            elif tool.startswith("arif_memory"):
                stage = "555_MEMORY"
            elif tool.startswith("arif_judge"):
                stage = "888_JUDGE"
            elif tool.startswith("arif_forge"):
                stage = "010_FORGE"
            elif tool.startswith("arif_seal"):
                stage = "999_RECEIPT"
            else:
                continue
        stage = _STAGE_ALIASES.get(str(stage), str(stage))
        if stage not in counts:
            continue
        counts[stage]["invocations"] += 1
        if ev.get("success", True):
            counts[stage]["success"] += 1
        else:
            counts[stage]["fail"] += 1
        if ev.get("tool"):
            counts[stage]["last_tool"] = ev.get("tool")
        if ev.get("trace_id"):
            counts[stage]["last_trace"] = ev.get("trace_id")
    return counts
