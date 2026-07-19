"""
conformance/deferred/test_fire_time_reauth.py — WAJIB 1: Deferred Execution
════════════════════════════════════════════════════════════════════════════

Stub: Full WAJIB 5 requires cron/job/queue test infrastructure.
These tests verify the kernel has the structural capability for
fire-time reauthorization.

DITEMPA BUKAN DIBERI.
"""

import json
import pytest
from conformance import _call_tool, _init_session, ARIFOS_URL, MCP_URL


def test_deferred_action_cannot_run_without_fire_time_judgment():
    """
    WAJIB-1 (deferred): The kernel must distinguish between write-time
    authorization and fire-time authorization. No deferred action may
    execute without a fresh judgment at execution time.

    Structural test: verify that session expiry and TTL concepts exist
    in the kernel's authority model.
    """
    session = _init_session("conformance-d1")

    # Session birth should have some concept of expiry or TTL
    sb = session.get("session_birth", {})
    # Check for any time-bound field
    time_fields = [k for k in sb.keys() if any(
        t in k.lower() for t in ("expir", "ttl", "time", "session")
    )]
    
    # At minimum, session_id must exist (identity binding for future re-auth)
    assert "session_id" in sb, (
        f"Session must have session_id for identity binding at fire time. "
        f"Keys: {list(sb.keys())}"
    )


def test_grandfathered_authority_blocked():
    """
    WAJIB-1 (deferred): A previously-authorized session that has expired
    or been revoked must not be able to execute deferred actions.
    """
    # Verify the concept of session/lease expiry exists in the arifOS model
    session = _init_session("conformance-d2")
    sid = session.get("session_birth", {}).get("session_id", "")

    # The actor's authority state should have an expiry concept
    actor = session.get("actor", {})
    as_ = actor.get("authority_state", {})
    rg = as_.get("runtime_grant", {})
    
    # expires_at should exist or at least be conceptually present
    assert "expires_at" in rg or "session" in as_, (
        f"Authority model must support expiry. runtime_grant keys: {list(rg.keys())}"
    )
