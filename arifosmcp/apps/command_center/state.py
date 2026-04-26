"""Shared runtime state for arifOS Command Center.

v0.1 uses in-memory state only. No persistence. No secrets stored.
"""

from __future__ import annotations

from dataclasses import dataclass


@dataclass
class RuntimeState:
    """Ephemeral state container. Reset on server restart."""

    session_count: int = 0
    judge_calls: int = 0
    forge_dry_runs: int = 0
    gateway_handshakes: int = 0
    vault_dry_seals: int = 0
    ops_reads: int = 0
    # Intentionally no secrets, no credentials, no persistent data.


# Global singleton for v0.1. In production this would be injected via lifespan.
_state: RuntimeState = RuntimeState()


def get_state() -> RuntimeState:
    """Return the current runtime state."""
    return _state


def reset_state() -> None:
    """Reset runtime state. Used in tests."""
    global _state
    _state = RuntimeState()
