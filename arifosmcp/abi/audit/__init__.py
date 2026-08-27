"""
arifOS Governance Audit Trail — Append-only JSONL with chain hashing.

Tamper-evident: each entry contains chain_hash (SHA-256 of this entry)
and previous_hash (SHA-256 of prior entry). Rust sidecar can verify
integrity by replaying the chain.

DITEMPA BUKAN DIBERI — Forged, not given.
"""

from __future__ import annotations

import hashlib
import json
import os
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

AUDIT_DIR = Path(__file__).resolve().parent
AUDIT_FILE = AUDIT_DIR / "mcp-governance-audit.jsonl"
CHAIN_FILE = AUDIT_DIR / ".chain_state.json"

_SCHEMA_VERSION = "1.0.0"


def _hash_entry(entry: dict[str, Any]) -> str:
    """SHA-256 of the entry JSON (deterministic, sorted keys)."""
    payload = json.dumps(entry, sort_keys=True, separators=(",", ":"), default=str)
    return f"sha256:{hashlib.sha256(payload.encode()).hexdigest()}"


def _load_chain_state() -> dict[str, str]:
    """Load previous hash from chain state file."""
    if CHAIN_FILE.exists():
        return json.loads(CHAIN_FILE.read_text(encoding="utf-8"))
    return {"last_hash": ""}


def _save_chain_state(state: dict[str, str]) -> None:
    """Persist chain state."""
    CHAIN_FILE.write_text(json.dumps(state), encoding="utf-8")


def write_audit_event(
    event: str,
    tool: str,
    capability_id: str,
    agent_id: str,
    verdict: str,
    reason: str,
    governance: dict[str, Any],
    session_id: str | None = None,
    opa_verdict: str | None = None,
    impact_radius: int = 0,
    is_reversible: bool = False,
    requires_888_hold: bool = False,
) -> dict[str, Any]:
    """
    Append a governance audit event to the JSONL trail.

    Returns the written entry (with chain_hash populated).
    """
    chain_state = _load_chain_state()

    entry = {
        "v": _SCHEMA_VERSION,
        "ts": datetime.now(timezone.utc).isoformat(),
        "event": event,
        "agent_id": agent_id,
        "session_id": session_id,
        "tool": tool,
        "capability_id": capability_id,
        "impact_radius": impact_radius,
        "is_reversible": is_reversible,
        "requires_888_hold": requires_888_hold,
        "verdict": verdict,
        "reason": reason,
        "governance": governance,
        "opa_verdict": opa_verdict,
        "previous_hash": chain_state["last_hash"],
    }

    # Compute chain hash (after previous_hash is set)
    entry["chain_hash"] = _hash_entry(entry)

    # Append to JSONL
    with AUDIT_FILE.open("a", encoding="utf-8") as f:
        f.write(json.dumps(entry, default=str) + "\n")

    # Update chain state
    _save_chain_state({"last_hash": entry["chain_hash"]})

    return entry
