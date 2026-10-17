"""
failure_wal.py — Failure Write-Ahead Log (WAL)
═══════════════════════════════════════════════════════════════════════════════

INV-L5-WAL: Zero-loss error telemetry. Every healing_error() call synchronously
appends a structured failure envelope to an append-only JSONL ledger before
returning to the agent loop.

Schema per line:
{
  "ts":           ISO8601,
  "session_id":   str | null,
  "organ":        str | null,
  "tool":         str | null,
  "code":         str,            # ErrorCodes constant
  "category":     "planning" | "tool" | "impl" | "verify" | "resource",
  "sig_hash":     str,            # sha256(tool + code + normalized_trace)
  "locus":        str | null,     # file/module if known
  "ctx_hash":     str | null,     # sha256(context snapshot)
  "recovery":     null | { "available": [...], "discovery_tool": str },
  "recovery_action": null | str,  # filled after successful recovery
}

Governance:
  - Append-only. No deletes. No overwrites.
  - File rotation by date: failure-wal-YYYY-MM-DD.jsonl
  - Feature-flagged: ARIFOS_FAILURE_WAL=1 (default ON)
  - Bounded: max 100KB per line (truncate oversized context)

DITEMPA BUKAN DIBERI ⚒️
"""

from __future__ import annotations

import hashlib
import json
import os
import threading
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

# ── Configuration ────────────────────────────────────────────────────────────
_WAL_DIR = Path(
    os.environ.get(
        "ARIFOS_FAILURE_WAL_DIR",
        "/root/.local/share/arifos/state/failure-wal",
    )
)
_WAL_ENABLED = os.environ.get("ARIFOS_FAILURE_WAL", "1") != "0"
_MAX_LINE_BYTES = 100_000  # 100KB per line safety cap

# Thread-local for session context injection
_ctx = threading.local()

# ── Error category classifier ────────────────────────────────────────────────
_CATEGORY_MAP: dict[str, str] = {
    # Tool/parameter errors → "tool"
    "INVALID_FIELD": "tool",
    "INVALID_TOOL": "tool",
    "INVALID_PARAMETER": "tool",
    "MISSING_PARAMETER": "tool",
    "TYPE_MISMATCH": "tool",
    # Resource errors → "resource"
    "NOT_FOUND": "resource",
    "SERVICE_UNAVAILABLE": "resource",
    "ORGAN_UNAVAILABLE": "resource",
    # Auth errors → "tool" (caller used wrong scope)
    "FORBIDDEN": "tool",
    "AUTHENTICATION_REQUIRED": "tool",
    "INSUFFICIENT_SCOPE": "tool",
    # Governance → "verify"
    "GOVERNANCE_HOLD": "verify",
    "GOVERNANCE_VOID": "verify",
    "CONSTITUTIONAL_VIOLATION": "verify",
    # Execution → "impl"
    "EXECUTION_FAILED": "impl",
    "TIMEOUT": "impl",
    "RATE_LIMITED": "resource",
}


def _classify(code: str) -> str:
    """Map error code to failure category."""
    return _CATEGORY_MAP.get(code, "impl")


def _sig_hash(tool: str | None, code: str, context: dict[str, Any] | None) -> str:
    """Deterministic signature hash: sha256(tool + code + sorted_context_keys)."""
    parts = [tool or "", code]
    if context:
        # Normalize: sorted keys, stringified values
        for k in sorted(context.keys()):
            v = context[k]
            parts.append(f"{k}={v}" if v is not None else k)
    raw = "|".join(parts)
    return hashlib.sha256(raw.encode("utf-8")).hexdigest()[:16]


def _ctx_hash(context: dict[str, Any] | None) -> str | None:
    """SHA-256 of context snapshot for dedup detection."""
    if not context:
        return None
    raw = json.dumps(context, sort_keys=True, default=str)
    return hashlib.sha256(raw.encode("utf-8")).hexdigest()[:16]


def _truncate(obj: Any, max_bytes: int = _MAX_LINE_BYTES) -> str:
    """JSON-serialize with byte-level truncation safety."""
    raw = json.dumps(obj, default=str, ensure_ascii=False)
    if len(raw.encode("utf-8")) > max_bytes:
        # Truncate and mark
        raw = raw[: max_bytes - 50] + "...[TRUNCATED]}"
    return raw


# ── Public API ───────────────────────────────────────────────────────────────


def set_session(session_id: str | None) -> None:
    """Set session_id for the current thread (called from arif_init)."""
    _ctx.session_id = session_id


def wal_append(
    *,
    code: str,
    message: str,
    organ: str | None = None,
    tool: str | None = None,
    parameter: str | None = None,
    received: Any = None,
    available: list[str] | None = None,
    discovery_tool: str | None = None,
    context: dict[str, Any] | None = None,
    recovery_action: str | None = None,
) -> dict[str, Any] | None:
    """Append a structured failure envelope to the WAL.

    Returns the WAL record dict (for inspection), or None if WAL is disabled.
    Raises nothing — WAL failure must never block the error response.
    """
    if not _WAL_ENABLED:
        return None

    try:
        # Ensure WAL directory exists
        _WAL_DIR.mkdir(parents=True, exist_ok=True)

        now = datetime.now(timezone.utc)
        record = {
            "ts": now.isoformat(),
            "session_id": getattr(_ctx, "session_id", None),
            "organ": organ,
            "tool": tool,
            "code": code,
            "category": _classify(code),
            "sig_hash": _sig_hash(tool, code, context),
            "locus": parameter,
            "ctx_hash": _ctx_hash(context),
            "recovery": {
                "available": (available or [])[:10],
                "discovery_tool": discovery_tool,
            }
            if (available or discovery_tool)
            else None,
            "recovery_action": recovery_action,
        }

        # Date-rotated filename
        wal_file = _WAL_DIR / f"failure-wal-{now.strftime('%Y-%m-%d')}.jsonl"
        line = _truncate(record) + "\n"

        # Synchronous append — atomic at line level on POSIX
        with open(wal_file, "a", encoding="utf-8") as f:
            f.write(line)
            f.flush()
            os.fsync(f.fileno())

        return record

    except Exception:
        # WAL failure MUST NEVER block the error response
        return None


def wal_query_today(
    *,
    sig_hash: str | None = None,
    code: str | None = None,
    organ: str | None = None,
) -> list[dict[str, Any]]:
    """Read today's WAL entries, optionally filtered.

    Used by the strategy bank (P2) to detect repeating failures.
    """
    now = datetime.now(timezone.utc)
    wal_file = _WAL_DIR / f"failure-wal-{now.strftime('%Y-%m-%d')}.jsonl"
    if not wal_file.exists():
        return []

    results = []
    try:
        with open(wal_file, "r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if not line:
                    continue
                try:
                    rec = json.loads(line)
                except json.JSONDecodeError:
                    continue
                # Apply filters
                if sig_hash and rec.get("sig_hash") != sig_hash:
                    continue
                if code and rec.get("code") != code:
                    continue
                if organ and rec.get("organ") != organ:
                    continue
                results.append(rec)
    except Exception:
        pass

    return results


def wal_count_sig(sig_hash: str) -> int:
    """Count occurrences of a signature hash in today's WAL.

    Used by INV-L5-REFLEX to detect N >= 2 repeating failures.
    """
    return len(wal_query_today(sig_hash=sig_hash))
