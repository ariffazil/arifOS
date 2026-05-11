"""
arifosmcp/apps/__init__.py
══════════════════════════
Surface-level exports for arifOS MCP apps.

DITEMPA BUKAN DIBERI — Forged, Not Given
"""

from arifosmcp.apps.interceptor import intercept
from arifosmcp.apps.session_state import (
    LifecycleState,
    SessionState,
    get_or_create_session,
)
from arifosmcp.apps.vault_chain import VAULT_PATH, append_vault_record, get_last_hash

__all__ = [
    "append_vault_record",
    "get_last_hash",
    "get_or_create_session",
    "intercept",
    "LifecycleState",
    "SessionState",
    "VAULT_PATH",
]
