"""arifosmcp/runtime/f6/consent_writer.py — ConsentLedger state writer (G2 v2).

HUMAN_RASA G2 sovereign wiring v2 (2026-11-02, F13 "finish off all" +
reconciliation requirements 4/5). Naming settled here:

  (1) FORMAT   — the ledger file is a JSON **array of scope rows** — exactly
                 the contract read_consent_ledger() already enforces. v1's
                 dict/events wrapper was a writer/reader mismatch (self-found
                 in the 2026-11-02 reconciliation); v2 adopts the reader's
                 contract as canonical. History/append-only semantics live in
                 the organ receipt layer (VAULT999 side), NOT in this state
                 file — this file answers "what consent exists RIGHT NOW".
  (2) LOCATION — $ARIFOS_CONSENT_LEDGER_PATH. No guessed fallback; absent env
                 is a reported dependency (reader and writer agree).
  (3) WRITER OF RECORD — F13 (Muhammad Arif bin Fazil). Agents are SCRIBES.
                 Every write requires actor + session_id + trace_id (one
                 missing → structured rejection: unattributed consent rows
                 are structurally impossible — PEACE² #3 remediation-by-
                 construction) plus an explicit `confirm_write=True` (the
                 write-side mirror of the reader's source_verified rule).
  (4) PURPOSE  — the scope row's own `purpose` string, exact-matched by the
                 reader. Unknown purpose → never ALLOW (consent_scope).
  (5) WITHDRAWAL — the scope row's existing `revoked` flag (schema field,
                 honoured by check_consent → DENY_REVOKED). Withdrawal flips
                 the flag in place; the row is never deleted, so the fact of
                 former consent stays auditable while all use is blocked.
  (6) CONCURRENCY — fcntl.flock around the whole read-modify-write; two
                 concurrent writers serialise, no lost rows.
  (7) AUTH LIMIT (v2, declared) — API-level actor authentication is NOT in
                 this module. The enforcement boundary is the filesystem:
                 the ledger file must be 0600 and writable only by the organ
                 service identity. Kernel-verb-level auth remains the kernel's
                 job. This limit is stated, not hidden.

Floors engaged: F6 · F11 · DITEMPA BUKAN DIBERI 🔥🌎🧠🪙
"""

from __future__ import annotations

import fcntl
import json
import os
from datetime import datetime, timezone
from typing import Any, Optional

SCHEMA_NOTE = "arifos.f6.consent_ledger.v1 — array of ConsentScope rows"
ENV_CONSENT_LEDGER_PATH = "ARIFOS_CONSENT_LEDGER_PATH"


def _ledger_path() -> Optional[str]:
    return os.environ.get(ENV_CONSENT_LEDGER_PATH) or None


def _now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def _attribution(
    actor: Optional[str],
    session_id: Optional[str],
    trace_id: Optional[str],
    on_behalf_of_f13: bool,
) -> dict[str, Any] | None:
    if not actor or not session_id or not trace_id:
        return None
    return {
        "actor": actor,
        "session_id": session_id,
        "trace_id": trace_id,
        "writer_of_record": "F13",
        "on_behalf_of_f13": bool(on_behalf_of_f13),
        "ts": _now_iso(),
    }


def _load_array(path: str) -> list[dict[str, Any]]:
    with open(path, "r", encoding="utf-8") as fh:
        raw = json.load(fh)
    if not isinstance(raw, list):
        raise ValueError(
            f"consent ledger must be a JSON array of scope rows (got {type(raw).__name__})"
        )
    return raw


def _write_locked(
    path: str,
    mutate,
    *,
    actor: str,
    session_id: str,
    trace_id: str,
    on_behalf_of_f13: bool,
    confirm_write: bool,
) -> dict[str, Any]:
    if not confirm_write:
        return {
            "status": "ERROR",
            "error_code": "CONFIRMATION_REQUIRED",
            "message": "write rejected: confirm_write=True is mandatory "
            "(write-side mirror of the reader's source_verified rule)",
        }
    attr = _attribution(actor, session_id, trace_id, on_behalf_of_f13)
    if attr is None:
        return {
            "status": "ERROR",
            "error_code": "ATTRIBUTION_REQUIRED",
            "message": "consent ledger write rejected: actor, session_id and "
            "trace_id are all mandatory — unattributed consent rows are "
            "structurally impossible",
        }
    path = _ledger_path() or ""
    if not path:
        return {
            "status": "UNKNOWN",
            "error_code": "LEDGER_PATH_UNSET",
            "message": f"${ENV_CONSENT_LEDGER_PATH} is not set — dependency "
            "reported, location never guessed",
            "dependency_missing": True,
        }
    lock_path = path + ".lock"
    try:
        os.makedirs(os.path.dirname(path), exist_ok=True)
        with open(lock_path, "w") as lock_fh:
            fcntl.flock(lock_fh, fcntl.LOCK_EX)
            rows = _load_array(path) if os.path.exists(path) else []
            result = mutate(rows, attr)
            if result.get("status") == "ERROR":
                return result
            tmp = path + ".tmp"
            with open(tmp, "w", encoding="utf-8") as fh:
                json.dump(rows, fh, ensure_ascii=False, indent=1)
            os.replace(tmp, path)
    except (OSError, ValueError, json.JSONDecodeError) as exc:
        return {"status": "ERROR", "error_code": "LEDGER_IO", "message": str(exc)}
    result["path"] = path
    result["scope_row_count"] = len(rows)
    return result


def grant_scope(
    scope_row: dict[str, Any],
    *,
    actor: Optional[str] = None,
    session_id: Optional[str] = None,
    trace_id: Optional[str] = None,
    on_behalf_of_f13: bool = False,
    confirm_write: bool = False,
) -> dict[str, Any]:
    """Insert or replace one scope row (state upsert; last write wins)."""
    if not isinstance(scope_row, dict) or not scope_row.get("scope_id"):
        return {
            "status": "ERROR",
            "error_code": "INVALID_SCOPE",
            "message": "scope row requires at least scope_id",
        }

    def mutate(rows: list[dict[str, Any]], attr: dict[str, Any]) -> dict[str, Any]:
        row = {
            **scope_row,
            "revoked": bool(scope_row.get("revoked", False)),
            "last_written_by": attr,
        }
        replaced = False
        for i, existing in enumerate(rows):
            if existing.get("scope_id") == row["scope_id"]:
                rows[i] = row
                replaced = True
                break
        if not replaced:
            rows.append(row)
        return {
            "status": "OK",
            "action": "grant",
            "scope_id": row["scope_id"],
            "replaced": replaced,
        }

    return _write_locked(
        "",
        mutate,
        actor=actor,
        session_id=session_id,
        trace_id=trace_id,
        on_behalf_of_f13=on_behalf_of_f13,
        confirm_write=confirm_write,
    )


def withdraw_scope(
    scope_id: str,
    *,
    reason: str = "",
    actor: Optional[str] = None,
    session_id: Optional[str] = None,
    trace_id: Optional[str] = None,
    on_behalf_of_f13: bool = False,
    confirm_write: bool = False,
) -> dict[str, Any]:
    """Flip the scope row's `revoked` flag — terminal for use, row kept for audit."""

    def mutate(rows: list[dict[str, Any]], attr: dict[str, Any]) -> dict[str, Any]:
        for row in rows:
            if row.get("scope_id") == scope_id:
                row["revoked"] = True
                row["revoked_reason"] = reason or row.get("revoked_reason", "")
                row["revoked_by"] = attr
                return {"status": "OK", "action": "withdraw", "scope_id": scope_id}
        return {
            "status": "ERROR",
            "error_code": "SCOPE_NOT_FOUND",
            "message": f"scope '{scope_id}' not present — nothing to withdraw",
        }

    return _write_locked(
        "",
        mutate,
        actor=actor,
        session_id=session_id,
        trace_id=trace_id,
        on_behalf_of_f13=on_behalf_of_f13,
        confirm_write=confirm_write,
    )
