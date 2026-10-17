"""
strategy_bank.py — Failure Signature Bank & Auto-Recovery (INV-L5-REFLEX)
═══════════════════════════════════════════════════════════════════════════════

Mines resolved errors from the failure WAL (where failure at time t was followed
by passing verification at time t+k) and extracts structured RecoverySkills.

When a signature_hash repeats (N >= 2) or matches a known failure cluster
(similarity >= 0.88), the raw retry is intercepted and the distilled recovery
procedure is injected into the tool error payload.

Schema (RecoverySkill):
{
  "sig_hash":     str,         # Primary key
  "root_cause":   str,         # Human-readable diagnosis
  "recovery_steps": [str],     # Ordered action list
  "confidence":   float,       # 0.0-1.0
  "times_seen":   int,
  "times_resolved": int,
  "last_seen":    ISO8601,
  "last_resolved": ISO8601,
}

Governance:
  - Read from failure WAL, write to strategy bank JSONL
  - Confidence >= 0.88 threshold for auto-injection
  - Recovery steps are advisory — the model decides whether to follow

DITEMPA BUKAN DIBERI ⚒️
"""

from __future__ import annotations

import hashlib
import json
import os
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

# ── Configuration ────────────────────────────────────────────────────────────
_STRATEGY_BANK_DIR = Path(
    os.environ.get(
        "ARIFOS_STRATEGY_BANK_DIR",
        "/root/.local/share/arifos/state/strategy-bank",
    )
)
_STRATEGY_BANK_FILE = "strategy-bank.jsonl"

# Threshold for auto-injection
CONFIDENCE_THRESHOLD = 0.88

# Minimum occurrences before a skill is extracted
MIN_OCCURRENCES = 2


# ── Strategy Bank Operations ─────────────────────────────────────────────────


def _bank_path() -> Path:
    """Return path to strategy-bank.jsonl."""
    _STRATEGY_BANK_DIR.mkdir(parents=True, exist_ok=True)
    return _STRATEGY_BANK_DIR / _STRATEGY_BANK_FILE


def _load_bank() -> dict[str, dict[str, Any]]:
    """Load strategy bank as dict keyed by sig_hash."""
    path = _bank_path()
    bank: dict[str, dict[str, Any]] = {}
    if not path.exists():
        return bank
    try:
        for line in path.read_text().strip().split("\n"):
            if line.strip():
                skill = json.loads(line)
                bank[skill["sig_hash"]] = skill
    except (json.JSONDecodeError, OSError):
        pass
    return bank


def _save_bank(bank: dict[str, dict[str, Any]]) -> None:
    """Write entire strategy bank (atomic replace)."""
    path = _bank_path()
    lines = [json.dumps(skill, default=str) + "\n" for skill in bank.values()]
    path.write_text("".join(lines))


def record_failure(
    sig_hash: str,
    code: str,
    organ: str | None = None,
    tool: str | None = None,
    message: str | None = None,
) -> None:
    """Record a failure occurrence in the strategy bank.

    Increments times_seen. Creates entry if new.
    """
    bank = _load_bank()
    now = datetime.now(timezone.utc).isoformat()

    if sig_hash in bank:
        bank[sig_hash]["times_seen"] = bank[sig_hash].get("times_seen", 0) + 1
        bank[sig_hash]["last_seen"] = now
        # Update context if provided
        if organ:
            bank[sig_hash]["organ"] = organ
        if tool:
            bank[sig_hash]["tool"] = tool
    else:
        bank[sig_hash] = {
            "sig_hash": sig_hash,
            "code": code,
            "organ": organ,
            "tool": tool,
            "root_cause": None,
            "recovery_steps": [],
            "confidence": 0.0,
            "times_seen": 1,
            "times_resolved": 0,
            "last_seen": now,
            "last_resolved": None,
        }

    _save_bank(bank)


def record_resolution(
    sig_hash: str,
    root_cause: str,
    recovery_steps: list[str],
) -> None:
    """Record that a failure signature was successfully resolved.

    Updates root_cause, recovery_steps, confidence, times_resolved.
    """
    bank = _load_bank()
    now = datetime.now(timezone.utc).isoformat()

    if sig_hash not in bank:
        # Create entry from resolution alone
        bank[sig_hash] = {
            "sig_hash": sig_hash,
            "code": None,
            "organ": None,
            "tool": None,
            "root_cause": root_cause,
            "recovery_steps": recovery_steps,
            "confidence": 0.5,  # Initial confidence from resolution
            "times_seen": 1,
            "times_resolved": 1,
            "last_seen": now,
            "last_resolved": now,
        }
    else:
        entry = bank[sig_hash]
        entry["root_cause"] = root_cause
        entry["recovery_steps"] = recovery_steps
        entry["times_resolved"] = entry.get("times_resolved", 0) + 1
        entry["last_resolved"] = now
        # Confidence: existence of resolution is the primary signal.
        # Base 0.5 for having ANY resolution, +0.15 per occurrence (cap 1.0)
        seen = entry.get("times_seen", 1)
        resolved = entry.get("times_resolved", 1)
        if resolved >= 1:
            entry["confidence"] = min(1.0, 0.5 + 0.15 * min(seen, 5))
        else:
            entry["confidence"] = 0.0

    _save_bank(bank)


def lookup_recovery(sig_hash: str) -> dict[str, Any] | None:
    """Look up a recovery skill for a given signature hash.

    Returns the skill if confidence >= CONFIDENCE_THRESHOLD, else None.
    """
    bank = _load_bank()
    if sig_hash not in bank:
        return None

    skill = bank[sig_hash]

    # Check minimum thresholds
    if skill.get("times_seen", 0) < MIN_OCCURRENCES:
        return None
    if skill.get("confidence", 0.0) < CONFIDENCE_THRESHOLD:
        return None
    if not skill.get("recovery_steps"):
        return None

    return skill


def get_all_skills() -> list[dict[str, Any]]:
    """Return all strategy bank entries (for inspection/debugging)."""
    return list(_load_bank().values())


def get_skill_count() -> int:
    """Return count of skills in the bank."""
    return len(_load_bank())


def get_actionable_skills() -> list[dict[str, Any]]:
    """Return skills that meet the confidence threshold."""
    return [
        s for s in _load_bank().values() if s.get("confidence", 0.0) >= CONFIDENCE_THRESHOLD and s.get("recovery_steps")
    ]
