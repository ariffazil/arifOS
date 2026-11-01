"""arifosmcp/runtime/f6/consent_ledger.py — read-only file-backed ConsentLedger (G2).

HUMAN_RASA P0 remediation, gap G2. Three components:

(1) ENV_CONSENT_LEDGER_PATH: env var NAME holding the ledger file path.
    There is NO default path — an absent env var is a reported dependency,
    never a guessed location.
(2) read_consent_ledger(): READ-ONLY loader. Absent env / absent file /
    unparseable content -> {"status": "UNKNOWN", ...} with the dependency
    named. Never writes, never invents scopes.
(3) check_consent_from_ledger(): fail-closed composition over
    consent_scope.check_consent. Any lookup problem resolves to UNKNOWN —
    never ALLOW. A verified ALLOW additionally requires the CALLER to assert
    source_verified=True (default False).

KNOWN LIMIT / TODO (sovereign wiring NOT done here by design): this reader is
NOT yet called from arifosmcp/memory/ingestion_service.py — ingestion still
passes consent_level through without checking it. Wiring requires ARIF's
decision on the ledger file's location + writer of record.

Floors engaged: F6 · DITEMPA BUKAN DIBERI 🔥🌎🧠🪙
"""

from __future__ import annotations

import json
import logging
import os
from datetime import datetime, timezone
from typing import Any, Optional

from arifosmcp.runtime.f6.consent_scope import (
    ConsentDecision,
    ConsentScope,
    check_consent,
)

logger = logging.getLogger(__name__)

SCHEMA = "arifos.f6.consent_ledger.v1"
ENV_CONSENT_LEDGER_PATH = "ARIFOS_CONSENT_LEDGER_PATH"

_SCOPE_FIELDS = {f for f in ConsentScope.__dataclass_fields__}


def _scope_from_dict(d: dict[str, Any]) -> ConsentScope:
    """Build a ConsentScope from a ledger record (nested parent_scope allowed)."""
    clean = {k: v for k, v in d.items() if k in _SCOPE_FIELDS}
    parent = clean.get("parent_scope")
    if isinstance(parent, dict):
        clean["parent_scope"] = _scope_from_dict(parent)
    return ConsentScope(**clean)


def read_consent_ledger() -> dict[str, Any]:
    """Read the consent ledger file. READ-ONLY — this function never writes.

    Returns {"status": "OK", "path", "scopes", "scope_ids"} on success or
    {"status": "UNKNOWN", "path", "reason", "dependency_missing": True} when
    the env var, file, or content is unavailable/unparseable.
    """
    path = os.environ.get(ENV_CONSENT_LEDGER_PATH)
    if not path:
        return {
            "status": "UNKNOWN",
            "path": None,
            "reason": (
                f"DEPENDENCY REPORTED: env var {ENV_CONSENT_LEDGER_PATH} not set — "
                "no default location is assumed; lookup resolves to UNKNOWN, never ALLOW"
            ),
            "dependency_missing": True,
        }
    if not os.path.isfile(path):
        return {
            "status": "UNKNOWN",
            "path": path,
            "reason": f"DEPENDENCY REPORTED: consent ledger file absent at {path}",
            "dependency_missing": True,
        }
    try:
        with open(path, encoding="utf-8") as fh:
            raw = json.load(fh)
    except (OSError, json.JSONDecodeError) as exc:
        logger.debug("consent ledger unreadable: %s", exc)
        return {
            "status": "UNKNOWN",
            "path": path,
            "reason": f"DEPENDENCY REPORTED: consent ledger unparseable — {exc}",
            "dependency_missing": True,
        }
    if not isinstance(raw, list):
        return {
            "status": "UNKNOWN",
            "path": path,
            "reason": "DEPENDENCY REPORTED: consent ledger must be a JSON array of scopes",
            "dependency_missing": True,
        }
    scopes: list[ConsentScope] = []
    for entry in raw:
        if isinstance(entry, dict) and entry.get("scope_id"):
            try:
                scopes.append(_scope_from_dict(entry))
            except TypeError as exc:
                logger.debug("consent ledger entry skipped: %s", exc)
    return {
        "status": "OK",
        "path": path,
        "scopes": scopes,
        "scope_ids": [s.scope_id for s in scopes],
    }


def lookup_ledger_scope(scope_id: str) -> tuple[Optional[ConsentScope], dict[str, Any]]:
    """Find one scope by id. Returns (scope, info); (None, info) when not found."""
    info = read_consent_ledger()
    if info["status"] != "OK":
        return None, info
    for scope in info["scopes"]:
        if scope.scope_id == scope_id:
            return scope, info
    return None, {
        "status": "UNKNOWN",
        "path": info["path"],
        "reason": f"scope '{scope_id}' not present in consent ledger — never ALLOW",
        "dependency_missing": True,
    }


def check_consent_from_ledger(
    scope_id: str,
    want_access: bool = False,
    want_use: bool = False,
    want_disclose: bool = False,
    now: Optional[datetime] = None,
    source_verified: bool = False,
    requested_subject: Optional[str] = None,
    requested_recipient: Optional[str] = None,
    requested_purpose: Optional[str] = None,
    requested_modality: Optional[str] = None,
    model_confidence: Optional[float] = None,
) -> dict[str, Any]:
    """Ledger-backed consent evaluation. Fail-closed: every lookup problem is UNKNOWN."""
    scope, info = lookup_ledger_scope(scope_id)
    if scope is None:
        return {
            "schema": SCHEMA,
            "decision": ConsentDecision.UNKNOWN,
            "reason": info.get("reason", "consent ledger lookup failed — never ALLOW"),
            "ledger_path": info.get("path"),
            "dependency_missing": True,
        }
    result = check_consent(
        scope,
        want_access=want_access,
        want_use=want_use,
        want_disclose=want_disclose,
        now=now or datetime.now(timezone.utc),
        source_verified=source_verified,
        requested_subject=requested_subject,
        requested_recipient=requested_recipient,
        requested_purpose=requested_purpose,
        requested_modality=requested_modality,
        model_confidence=model_confidence,
    )
    result["schema"] = SCHEMA
    result["ledger_path"] = info.get("path")
    return result
