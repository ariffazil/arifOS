"""
arifosmcp/runtime/ditempa.py — DITEMPA Constitutional Signature Primitive
═════════════════════════════════════════════════════════════════════════

Forged 2026-08-02 by F13 SOVEREIGN directive. Extracted from tools/session.py
to eliminate the duplicated _compute_signature definition (was at lines 103
and 160 of the source). Single source of truth for the constitutional
signature primitive.

The motto "DITEMPA, BUKAN DIBERI" (Forged, Not Given) is the forge doctrine
echoed on every session manifest. Even HOLD responses are signed — failure is
constitutionally anchored.

Reversibility: git revert <sha> restores prior state.
"""

from __future__ import annotations

import hashlib
from typing import Any

# ─── Constants (canonical, single source) ─────────────────────────────────────

DITEMPA_MOTTO: str = "DITEMPA, BUKAN DIBERI"

# State emoji — load-bearing cognitive signal, not decoration.
# Humans read state faster through symbols; agents read state through structured fields.
_STATE_EMOJI: dict[str, str] = {
    "OK": "🔥",  # forged, alive, ignition complete
    "HOLD": "🔒",  # locked, awaiting human input or co-signature
    "FAILURE": "❌",  # denied or unrecoverable failure
    "DEGRADED": "🧩",  # partial, fragmented session
    "REVOKED": "🛑",  # permanently withdrawn
    "PARTIAL": "🟡",  # mixed state — some capabilities bound, others not
    "UNKNOWN": "⚪",  # indeterminate
}

_MODE_EMOJI: dict[str, str] = {
    "init": "🔥",
    "light": "⚡",
    "ping": "💓",
    "discover": "🔍",
    "resume": "🔄",
    "validate": "✅",
    "epoch_open": "📂",
    "epoch_seal": "📦",
    "challenge": "🔐",
    "cleanup": "🧹",
    "full": "🌐",
    "opt_out": "🚪",
}


# ─── Canonical signature primitive ────────────────────────────────────────────


def compute_signature(status: str, mode: str, session_id: str, ts: float) -> str:
    """Deterministic constitutional signature. Even HOLD responses are signed.

    Forged 2026-08-02 (extracted from tools/session.py — was duplicated at
    lines 103 and 160 of the source). Single source of truth.
    """
    payload = f"{DITEMPA_MOTTO}|{status}|{mode}|{session_id}|{ts:.6f}"
    return f"sha256:{hashlib.sha256(payload.encode()).hexdigest()[:16]}"


def state_emoji(status: str) -> str:
    """Lookup state emoji by status string. UNKNOWN → ⚪."""
    return _STATE_EMOJI.get(str(status), "⚪")


def mode_emoji(mode: str) -> str:
    """Lookup mode emoji by mode string. Empty mode → empty string."""
    if not mode:
        return ""
    return _MODE_EMOJI.get(mode, "")


__all__ = [
    "DITEMPA_MOTTO",
    "compute_signature",
    "state_emoji",
    "mode_emoji",
]