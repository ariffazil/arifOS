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
import time
import uuid
from collections import deque
from collections.abc import Iterator
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

# Durable append-only JSONL buses (Session A — separate operation/receipt logs)
_DURABLE_BUS_DIR = Path(
    os.environ.get(
        "ARIFOS_DURABLE_EVENT_BUS_DIR",
        os.environ.get(
            "ARIFOS_DURABLE_EVENT_BUS",
            "/var/lib/arifos/event_bus",
        ),
    )
)
# If ARIFOS_DURABLE_EVENT_BUS points at a file path, use its parent as dir
if _DURABLE_BUS_DIR.suffix in {".jsonl", ".log"}:
    _LEGACY_LOG = _DURABLE_BUS_DIR
    _DURABLE_BUS_DIR = _DURABLE_BUS_DIR.parent
else:
    _LEGACY_LOG = _DURABLE_BUS_DIR / "events.jsonl"
_OPERATIONS_LOG = _DURABLE_BUS_DIR / "operations.log"
_RECEIPTS_LOG = _DURABLE_BUS_DIR / "receipts.log"
# alias for callers expecting a single path
_DURABLE_BUS_PATH = _LEGACY_LOG
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
    # ── Session A: Operation/Receipt fields ──────────────────────────
    "op_id",
    "actor_id",
    "capability",
    "params",
    "timestamp_start",
    "timestamp_end",
    "result_summary",
    "evidence_uri",
    "vault_candidate",
    "signature",
    "_event_kind",
    "_emitted_at",
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
    """Append-only JSONL durable bus. Routes to operations.log or receipts.log."""
    try:
        _DURABLE_BUS_DIR.mkdir(parents=True, exist_ok=True)
        line = json.dumps(event, separators=(",", ":"), default=str) + "\n"
        # Route to correct log based on event type
        event_type = event.get("event_type", "")
        if "receipt" in event_type or event.get("vault_candidate"):
            log_path = _RECEIPTS_LOG
        elif "operation" in event_type or event.get("op_id"):
            log_path = _OPERATIONS_LOG
        else:
            log_path = _LEGACY_LOG
        with open(log_path, "a", encoding="utf-8") as fh:
            fh.write(line)
    except Exception as exc:
        logger.debug("durable bus append failed: %s", exc)


# ── Session A: Operation/Receipt emission ──────────────────────────────────


def emit_operation(
    capability: str,
    *,
    actor_id: str | None = None,
    session_id: str | None = None,
    trace_id: str | None = None,
    organ: str = "arifos",
    params: dict[str, Any] | None = None,
    status: str = "STARTED",
    op_id: str | None = None,
) -> dict[str, Any]:
    """Emit an OperationEvent to the durable bus."""
    from arifosmcp.schemas.operation import OperationEvent

    op = OperationEvent(
        op_id=op_id or str(uuid.uuid4()),
        actor_id=actor_id,
        session_id=session_id,
        trace_id=trace_id,
        organ=organ,
        capability=capability,
        params=params or {},
        status=status,
    )
    event = op.model_dump()
    event["event_type"] = "operation"
    return emit_durable_event(event)


def emit_receipt(
    op_id: str,
    *,
    session_id: str | None = None,
    trace_id: str | None = None,
    organ: str = "arifos",
    result_summary: str = "",
    evidence_uri: str | None = None,
    vault_candidate: bool = False,
) -> dict[str, Any]:
    """Emit a ReceiptEvent to the durable bus. vault_candidate=True for lineage-worthy ops."""
    from arifosmcp.schemas.operation import ReceiptEvent

    receipt = ReceiptEvent(
        op_id=op_id,
        session_id=session_id,
        trace_id=trace_id,
        organ=organ,
        result_summary=result_summary,
        evidence_uri=evidence_uri,
        vault_candidate=vault_candidate,
    )
    event = receipt.model_dump()
    event["event_type"] = "receipt"
    return emit_durable_event(event)


# ── Session A: Replay ─────────────────────────────────────────────────────


def replay_operations(limit: int = 1000) -> list[dict[str, Any]]:
    """Replay operations.log in order."""
    ops: list[dict[str, Any]] = []
    try:
        if _OPERATIONS_LOG.exists():
            with open(_OPERATIONS_LOG, encoding="utf-8") as fh:
                for line in fh:
                    line = line.strip()
                    if line:
                        ops.append(json.loads(line))
    except Exception as exc:
        logger.error("replay_operations failed: %s", exc)
    return ops[-limit:]


def replay_receipts(limit: int = 1000) -> list[dict[str, Any]]:
    """Replay receipts.log in order."""
    receipts: list[dict[str, Any]] = []
    try:
        if _RECEIPTS_LOG.exists():
            with open(_RECEIPTS_LOG, encoding="utf-8") as fh:
                for line in fh:
                    line = line.strip()
                    if line:
                        receipts.append(json.loads(line))
    except Exception as exc:
        logger.error("replay_receipts failed: %s", exc)
    return receipts[-limit:]


def bus_stats() -> dict[str, Any]:
    """Return bus health statistics."""
    ops = replay_operations(limit=10000)
    receipts = replay_receipts(limit=10000)
    return {
        "operations_total": len(ops),
        "receipts_total": len(receipts),
        "vault_candidates": sum(1 for r in receipts if r.get("vault_candidate")),
        "operations_log_bytes": _OPERATIONS_LOG.stat().st_size if _OPERATIONS_LOG.exists() else 0,
        "receipts_log_bytes": _RECEIPTS_LOG.stat().st_size if _RECEIPTS_LOG.exists() else 0,
    }


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


_TAIL_CACHE_TTL_S = 60.0
_tail_cache: dict[tuple[Any, ...], tuple[float, list[dict[str, Any]]]] = {}

# ── Incremental durable-bus reads ───────────────────────────────────────────
# The durable bus is append-only (verified 2026-11-23: file sizes only grow,
# inodes stay stable, previously written bytes never change).  A reader can
# therefore consume only the bytes appended since its last position, so the
# cost of a refresh tracks the append rate instead of the archive size
# (operations.log was 205 MB and growing ~4.7 KB/min).
#
# Two entry points:
#   * read_durable_events_recent()  — cold start: the tail of recent traffic
#   * read_durable_events_incremental() — warm: only what was appended
# The caller owns the cursor (a plain dict of per-file byte positions), so
# nothing here holds mutable module state.


def _bus_files() -> tuple[Path, ...]:
    """Durable bus files in read order (legacy, operations, receipts)."""
    return (_LEGACY_LOG, _OPERATIONS_LOG, _RECEIPTS_LOG)


def _write_epoch(event: dict[str, Any]) -> float | None:
    """When a bus row was *written* (as opposed to when the tool ran).

    Used for horizon checks: freshness of a record is a property of when it
    landed in the log.  ``_emitted_at`` is stamped by ``_sanitize_event`` on
    every durable row; ``timestamp`` is the fallback for legacy rows written
    before that field existed.
    """
    for key in ("_emitted_at", "timestamp"):
        raw = event.get(key)
        if isinstance(raw, (int, float)):
            return float(raw)
        if isinstance(raw, str) and raw.strip():
            try:
                return datetime.fromisoformat(raw.replace("Z", "+00:00")).timestamp()
            except ValueError:
                continue
    return None


def _iter_backward_lines(path: Path, *, max_lines: int) -> Iterator[bytes]:
    """Yield raw lines from *path* newest-first, at most ``max_lines``.

    Streams in 1 MiB chunks so a bounded backward scan costs O(window)
    memory, never O(file).
    """
    try:
        size = path.stat().st_size
    except OSError:
        return
    if size <= 0 or max_lines <= 0:
        return
    seen = 0
    pending = b""
    with open(path, "rb") as fh:
        pos = size
        while pos > 0 and seen < max_lines:
            step = min(1 << 20, pos)
            pos -= step
            fh.seek(pos)
            chunk = fh.read(step)
            lines = (chunk + pending).split(b"\n")
            pending = lines[0]  # earliest fragment — its head is in an earlier chunk
            for raw in reversed(lines[1:]):
                seen += 1
                if seen > max_lines:
                    return
                yield raw
    if pending and seen < max_lines:
        # The file's first line — complete by definition (bounded by file start).
        yield pending


def read_durable_events_recent(
    *,
    within_seconds: float,
    max_lines_per_file: int = 50_000,
    files: tuple[Path, ...] | None = None,
) -> tuple[list[dict[str, Any]], dict[str, dict[str, int]]]:
    """Cold-start read: bus rows written within ``within_seconds``.

    Each bus file is scanned backwards from EOF and the scan stops at the
    horizon, so the cost is proportional to recent traffic rather than to
    archive size.  Rows older than the horizon are excluded: they cannot
    prove a tool is live, and the merge is monotone, so an older epoch never
    wins against a newer cached one.

    Returns ``(events, resume_cursor)``.  The cursor resumes at the size
    observed *before* the scan, so bytes appended during the scan are read
    again (and re-merged) on the next call rather than lost.
    """
    paths = files if files is not None else _bus_files()
    cutoff = time.time() - within_seconds
    events: list[dict[str, Any]] = []
    cursor: dict[str, dict[str, int]] = {}
    for path in paths:
        try:
            st = path.stat()
        except OSError:
            continue
        cursor[str(path)] = {"ino": st.st_ino, "offset": st.st_size}
        for raw in _iter_backward_lines(path, max_lines=max_lines_per_file):
            line = raw.strip()
            if not line:
                continue
            try:
                obj = json.loads(line.decode("utf-8", errors="replace"))
            except json.JSONDecodeError:
                continue
            if not isinstance(obj, dict):
                continue
            written = _write_epoch(obj)
            if written is not None and written < cutoff:
                break  # append-only: everything further back is older still
            events.append(obj)
    return events, cursor


def _read_appended(path: Path, offset: int) -> tuple[list[dict[str, Any]], int]:
    """Parse the complete lines appended to *path* after *offset``.

    Returns ``(events, new_offset)``.  The new offset stops at the last
    complete line, so a partially written trailing line is re-read on the
    next call rather than lost.
    """
    try:
        size = path.stat().st_size
    except OSError:
        return [], offset
    if size <= offset:
        return [], offset
    try:
        with open(path, "rb") as fh:
            fh.seek(offset)
            chunk = fh.read(size - offset)
    except OSError as exc:
        logger.debug("durable bus append read failed %s: %s", path, exc)
        return [], offset
    cut = chunk.rfind(b"\n")
    if cut < 0:
        return [], offset  # no complete line yet
    usable = chunk[: cut + 1]
    events: list[dict[str, Any]] = []
    for raw in usable.splitlines():
        raw = raw.strip()
        if not raw:
            continue
        try:
            obj = json.loads(raw.decode("utf-8", errors="replace"))
        except json.JSONDecodeError:
            continue
        if isinstance(obj, dict):
            events.append(obj)
    return events, offset + len(usable)


def read_durable_events_incremental(
    cursor: dict[str, dict[str, int]] | None = None,
    *,
    files: tuple[Path, ...] | None = None,
) -> tuple[list[dict[str, Any]], dict[str, dict[str, int]]]:
    """Read the durable bus events appended since ``cursor``.

    ``cursor`` maps a bus file path to ``{"ino": int, "offset": int}``.  Only
    bytes written since the recorded offset are read, so the cost tracks the
    append rate rather than the archive size.  A file that was rotated
    (inode changed) or truncated (size below the offset) restarts from the
    top.

    Returns ``(events, new_cursor)``.
    """
    paths = files if files is not None else _bus_files()
    previous = cursor or {}
    events: list[dict[str, Any]] = []
    new_cursor: dict[str, dict[str, int]] = {}
    for path in paths:
        key = str(path)
        prev = previous.get(key) or {}
        try:
            st = path.stat()
        except OSError:
            continue
        offset = int(prev.get("offset") or 0)
        ino = int(prev.get("ino") or 0)
        if ino and ino != st.st_ino:
            offset = 0  # rotated — the new file starts at the top
        elif st.st_size < offset:
            offset = 0  # truncated — rewind
        got, offset = _read_appended(path, offset)
        events.extend(got)
        new_cursor[key] = {"ino": st.st_ino, "offset": offset}
    return events, new_cursor



def _read_tail_lines(path: Path, take: int | None) -> list[str]:
    """Return the last ``take`` complete lines of *path* without parsing the
    whole file.

    Backward chunk scan counting newlines, then decode only the bounded
    window.  Full-file behaviour is preserved when ``take`` is None/<=0.
    (2026-10-09: operations.log grew to 104 MB / 168k lines and every
    /health re-parsed the entire bus under the GIL — kernel 503 storm.)
    """
    if take is None or take <= 0:
        with open(path, encoding="utf-8", errors="replace") as fh:
            return fh.readlines()
    chunk_size = 1 << 20  # 1 MB backward scan step
    size = path.stat().st_size
    with open(path, "rb") as fh:
        pos = size
        newlines = 0
        buf = b""
        while pos > 0 and newlines <= take:
            step = min(chunk_size, pos)
            pos -= step
            fh.seek(pos)
            chunk = fh.read(step)
            newlines += chunk.count(b"\n")
            buf = chunk + buf
    lines = buf.splitlines()
    if len(lines) > take:
        lines = lines[-take:]
    return [ln.decode("utf-8", errors="replace") for ln in lines]


def read_durable_events(
    limit: int = 5000,
    force: bool = False,
    *,
    files: tuple[Path, ...] | None = None,
) -> list[dict[str, Any]]:
    """Read durable JSONL events from the bus files (oldest-first per file).

    Tail-bounded per file (2026-10-09): only the last ``limit`` complete
    lines of EACH bus file are decoded, and the read cost is O(tail) instead
    of O(bus).

    2026-11-23 (starvation fix): the per-file windows were concatenated and
    then truncated as one block, so ``receipts.log`` — read last, and the
    largest file — displaced *every* ``operations.log`` row.  operations.log
    is the only bus file carrying ``capability``/``status``, so the
    capability hydration saw zero qualifying events at every window size
    while paying the full read cost on the /health request thread.  The
    per-file windows are now kept separate: each file contributes its own
    bounded window and no file can evict another's events.

    Results are cached for ``_TAIL_CACHE_TTL_S`` seconds (telemetry bus,
    not transactional); pass ``force=True`` to bypass the cache.
    """
    paths = files if files is not None else _bus_files()
    key = (int(limit or 0), tuple(str(p) for p in paths))
    now = time.monotonic()
    cached = _tail_cache.get(key)
    if not force and cached is not None and (now - cached[0]) < _TAIL_CACHE_TTL_S:
        return cached[1]

    out: list[dict[str, Any]] = []
    for path in paths:
        if not path.exists():
            continue
        try:
            for line in _read_tail_lines(path, limit):
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
            logger.debug("durable bus read failed %s: %s", path, exc)

    _tail_cache[key] = (now, out)
    if len(_tail_cache) > 8:  # bound distinct-limit cache entries
        oldest_key = min(_tail_cache, key=lambda k: _tail_cache[k][0])
        _tail_cache.pop(oldest_key, None)
    return out


def stage_counters(limit: int = 5000) -> dict[str, dict[str, Any]]:
    """Aggregate durable bus into per-stage invocation / success counts.

    Always reads the full ``events.jsonl`` file (the canonical stage event log)
    without truncation, then supplements with the normal windowed tail read of
    operations/receipts.  This prevents high-volume operations.log from
    displacing stage events when the combined bus exceeds *limit*.
    """
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

    # ── Priority source: events.jsonl read fully (stage events live here) ──────
    dedicated_events: list[dict[str, Any]] = []
    if _LEGACY_LOG.exists():
        try:
            with open(_LEGACY_LOG, encoding="utf-8") as fh:
                for line in fh:
                    line = line.strip()
                    if not line:
                        continue
                    try:
                        obj = json.loads(line)
                        if isinstance(obj, dict):
                            dedicated_events.append(obj)
                    except json.JSONDecodeError:
                        continue
        except Exception as exc:
            logger.debug("stage_counters: events.jsonl read failed: %s", exc)

    # ── Supplement: windowed tail from the operation/receipt logs ─────────────
    # events.jsonl is deliberately excluded: it was already read in full above,
    # so including it here would count every stage event twice.  The per-file
    # windows are kept separate (2026-11-23) so operations.log and
    # receipts.log can no longer displace one another.
    all_events = dedicated_events + read_durable_events(
        limit=limit, files=(_OPERATIONS_LOG, _RECEIPTS_LOG)
    )

    for ev in all_events:
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
