"""
arifOS Golden Path — Assumption Bridge
═══════════════════════════════════════

Cross-session learning: 999_SEAL writes, 000_INIT reads.

The assumption ledger is the memory that compounds across sessions.
Each assumption carries: statement, implication if wrong, session origin,
invalidation status.

When a new session starts, 000_INIT reads the last session's assumptions.
If any were invalidated, the new session knows not to repeat them.

The recursion is memory. The improvement is compounding evidence.

DITEMPA BUKAN DIBERI 🔥⚒️
"""

from __future__ import annotations

import json
from pathlib import Path

from .session_state import Assumption, SessionState


# ── VAULT999 paths ──────────────────────────────────────────────────────────

DEFAULT_VAULT_DIR = Path("/var/lib/arifos/vault")
ASSUMPTIONS_FILE = "assumptions.jsonl"


def _get_assumptions_path(vault_dir: Path | None = None) -> Path:
    """Get the path to the assumptions ledger file."""
    vault = vault_dir or DEFAULT_VAULT_DIR
    return vault / ASSUMPTIONS_FILE


# ── Write assumptions ────────────────────────────────────────────────────────

def write_assumptions(
    session_state: SessionState,
    vault_dir: Path | None = None,
) -> Path:
    """Write the session's assumption ledger to VAULT999.

    Called by 999_SEAL at session close.
    Appends to assumptions.jsonl (append-only, like all VAULT999 writes).

    Returns the path written to.
    """
    path = _get_assumptions_path(vault_dir)
    path.parent.mkdir(parents=True, exist_ok=True)

    with open(path, "a", encoding="utf-8") as f:
        for assumption in session_state.assumption_ledger:
            record = {
                "id": assumption.id,
                "statement": assumption.statement,
                "implication_if_wrong": assumption.implication_if_wrong,
                "session_id": assumption.session_id or session_state.session_id,
                "stage": assumption.stage,
                "invalidated": assumption.invalidated,
                "invalidated_in_session": assumption.invalidated_in_session,
                "sealed_at": session_state.sealed_at,
                "seal_hash": session_state.compute_seal_hash(),
            }
            f.write(json.dumps(record, ensure_ascii=False) + "\n")

    return path


# ── Read prior assumptions ───────────────────────────────────────────────────

def load_prior_assumptions(
    prior_session_id: str | None = None,
    vault_dir: Path | None = None,
    limit: int = 50,
) -> list[Assumption]:
    """Load assumptions from prior sessions.

    Called by 000_INIT at session start.
    If prior_session_id is specified, loads only that session's assumptions.
    Otherwise loads the most recent assumptions.

    Returns list of Assumption objects.
    """
    path = _get_assumptions_path(vault_dir)

    if not path.exists():
        return []

    assumptions: list[Assumption] = []

    with open(path, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            try:
                record = json.loads(line)
                if prior_session_id and record.get("session_id") != prior_session_id:
                    continue
                assumptions.append(Assumption(
                    id=record.get("id", ""),
                    statement=record.get("statement", ""),
                    implication_if_wrong=record.get("implication_if_wrong", ""),
                    session_id=record.get("session_id", ""),
                    stage=record.get("stage", ""),
                    invalidated=record.get("invalidated", False),
                    invalidated_in_session=record.get("invalidated_in_session"),
                ))
            except json.JSONDecodeError:
                continue

    # Return most recent N
    return assumptions[-limit:]


def load_latest_assumptions(
    vault_dir: Path | None = None,
    limit: int = 20,
) -> list[Assumption]:
    """Load the most recent assumptions across all sessions.

    Used when no prior_session_id is known (fresh session with memory).
    """
    path = _get_assumptions_path(vault_dir)

    if not path.exists():
        return []

    assumptions: list[Assumption] = []

    with open(path, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            try:
                record = json.loads(line)
                assumptions.append(Assumption(
                    id=record.get("id", ""),
                    statement=record.get("statement", ""),
                    implication_if_wrong=record.get("implication_if_wrong", ""),
                    session_id=record.get("session_id", ""),
                    stage=record.get("stage", ""),
                    invalidated=record.get("invalidated", False),
                    invalidated_in_session=record.get("invalidated_in_session"),
                ))
            except json.JSONDecodeError:
                continue

    return assumptions[-limit:]


def format_assumptions_for_context(assumptions: list[Assumption]) -> str:
    """Format assumptions as a context string for 000_INIT injection.

    This is what gets injected into the prompt:
    "From prior session [id], these assumptions were made..."
    """
    if not assumptions:
        return "No prior session assumptions found. Fresh start."

    lines = [
        "PRIOR SESSION ASSUMPTIONS (cross-session memory):",
        "",
    ]

    for i, a in enumerate(assumptions, 1):
        status = "❌ INVALIDATED" if a.invalidated else "✓ active"
        lines.append(f"  {i}. [{status}] {a.statement}")
        lines.append(f"     → If wrong: {a.implication_if_wrong}")
        if a.invalidated and a.invalidated_in_session:
            lines.append(f"     → Invalidated in session: {a.invalidated_in_session}")
        lines.append("")

    invalidated = [a for a in assumptions if a.invalidated]
    if invalidated:
        lines.append(
            f"⚠️  {len(invalidated)} assumption(s) have been invalidated. "
            f"Do not repeat these mistakes."
        )

    return "\n".join(lines)


__all__ = [
    "write_assumptions",
    "load_prior_assumptions",
    "load_latest_assumptions",
    "format_assumptions_for_context",
]
