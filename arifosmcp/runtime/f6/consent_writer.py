"""arifosmcp/runtime/f6/consent_writer.py — attribution-enforced ConsentLedger writer.

HUMAN_RASA G2 sovereign wiring (2026-11-02, F13 "finish off all"). The G2
reader (consent_ledger.py) is READ-ONLY by design; the naming left open was
the ledger file location + writer of record. Named here:

  (1) LOCATION  — $ARIFOS_CONSENT_LEDGER_PATH (deploy default:
                  /var/lib/arifos/consent_ledger.json). The env var remains
                  the single source of the path; no guessed fallback.
  (2) WRITER OF RECORD — F13 (Muhammad Arif bin Fazil). Agents are SCRIBES:
                  they append entries, never author scopes. Every append
                  MUST carry actor + session_id + trace_id; a write without
                  all three is REJECTED — trc-canon-unattributed is
                  structurally impossible in this ledger (PEACE² #3
                  remediation-by-construction).
  (3) PURPOSE   — canonical purpose = the scope's own `purpose` string,
                  matched exactly by the reader. Unknown purpose resolves
                  DENY/UNKNOWN fail-closed by consent_scope.check_consent;
                  no central enum to drift.
  (4) WITHDRAWAL — append-only tombstone: {"action": "withdraw",
                  "scope_id", ts, attribution}. Readers (check_consent_
                  from_ledger) treat a tombstone as terminal for that
                  scope_id. Nothing is ever deleted.

Floors engaged: F6 · F11 · DITEMPA BUKAN DIBERI 🔥🌎🧠🪙
"""

from __future__ import annotations

import json
import os
from datetime import datetime, timezone
from typing import Any, Optional

SCHEMA = "arifos.f6.consent_ledger.v1"


def _ledger_path() -> Optional[str]:
    return os.environ.get("ARIFOS_CONSENT_LEDGER_PATH") or None


def append_consent_entry(
    entry: dict[str, Any],
    *,
    actor: Optional[str] = None,
    session_id: Optional[str] = None,
    trace_id: Optional[str] = None,
    on_behalf_of_f13: bool = False,
) -> dict[str, Any]:
    """Append one entry to the consent ledger with mandatory attribution.

    REJECTS (never guesses) when the env path is unset, the file/parent is
    unusable, or any of actor/session_id/trace_id is missing. Scribes may
    append only with on_behalf_of_f13=True, which records the delegation
    explicitly — the writer of record remains F13.
    """
    if not actor or not session_id or not trace_id:
        return {
            "status": "ERROR",
            "error_code": "ATTRIBUTION_REQUIRED",
            "message": "consent ledger write rejected: actor, session_id and "
            "trace_id are all mandatory — unattributed consent entries are "
            "structurally impossible",
        }
    path = _ledger_path()
    if not path:
        return {
            "status": "UNKNOWN",
            "error_code": "LEDGER_PATH_UNSET",
            "message": f"${'ARIFOS_CONSENT_LEDGER_PATH'} is not set — "
            "dependency reported, location never guessed",
            "dependency_missing": True,
        }
    stamped = {
        **entry,
        "attribution": {
            "actor": actor,
            "session_id": session_id,
            "trace_id": trace_id,
            "writer_of_record": "F13",
            "on_behalf_of_f13": bool(on_behalf_of_f13),
        },
        "ts": datetime.now(timezone.utc).isoformat(),
    }
    try:
        os.makedirs(os.path.dirname(path), exist_ok=True)
        existing: dict[str, Any] = {"schema": SCHEMA, "scopes": [], "events": []}
        if os.path.exists(path):
            with open(path, "r", encoding="utf-8") as fh:
                existing = json.load(fh)
        if existing.get("schema") != SCHEMA:
            return {
                "status": "ERROR",
                "error_code": "SCHEMA_MISMATCH",
                "message": f"ledger schema {existing.get('schema')!r} != {SCHEMA!r}",
            }
        existing.setdefault("events", []).append(stamped)
        tmp = path + ".tmp"
        with open(tmp, "w", encoding="utf-8") as fh:
            json.dump(existing, fh, ensure_ascii=False, indent=1)
        os.replace(tmp, path)
    except (OSError, json.JSONDecodeError) as exc:
        return {
            "status": "ERROR",
            "error_code": "LEDGER_IO",
            "message": str(exc),
        }
    return {
        "status": "OK",
        "path": path,
        "entry": stamped,
        "event_count": len(existing.get("events", [])),
    }


def withdraw_scope(
    scope_id: str,
    *,
    actor: str,
    session_id: str,
    trace_id: str,
    reason: str = "",
) -> dict[str, Any]:
    """Append a withdrawal tombstone — terminal for the scope_id, never a delete."""
    return append_consent_entry(
        {"action": "withdraw", "scope_id": scope_id, "reason": reason},
        actor=actor,
        session_id=session_id,
        trace_id=trace_id,
    )
