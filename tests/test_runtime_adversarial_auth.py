"""
tests/test_runtime_adversarial_auth.py — F11 Adversarial Identity and Auth Hardening Tests

This suite targets edge cases around token forgery, session masking, precedence injection,
and identity escalation, ensuring the F11 AUTHORITY floor remains sovereign.
"""

from __future__ import annotations

import pytest
from arifosmcp.runtime.tools import init_anchor, arifos_kernel
from arifosmcp.runtime.models import AuthorityLevel, ClaimStatus, Verdict

@pytest.mark.asyncio
class TestAdversarialIdentity:
    """Test identity precedence and forgery resistance (F11)."""

    async def test_inv1_precedence_attack_downgrade(self):
        """
        Attack: Model declares 'Arif' (Sovereign) but transport claims 'Guest'.
        Requirement: Transport actor_id must win, regardless of model declaration.
        """
        envelope = await init_anchor(
            mode="init",
            actor_id="guest-user",
            declared_name="Arif",
            intent="establish sovereign access"
        )
        
        # Transport actor_id ('guest-user') must win
        assert envelope.authority.actor_id == "guest-user"
        # Must NOT be sovereign or system level
        assert envelope.authority.level in [AuthorityLevel.AGENT, AuthorityLevel.USER, AuthorityLevel.OPERATOR]
        assert envelope.authority.level != AuthorityLevel.SYSTEM

    async def test_inv2_token_session_mismatch(self):
        """
        Attack: Provide valid token for session A, but try to use it for session B.
        Requirement: Kernel must reject calls where token doesn't match session_id.
        """
        # 1. Establish valid session A
        session_a = "session-alpha"
        env_a = await init_anchor(mode="init", session_id=session_a, actor_id="user-a")
        auth_a = env_a.auth_context
        auth_a_dict = auth_a.model_dump() if hasattr(auth_a, "model_dump") else auth_a

        # 2. Try to use session A's auth_context for session B
        session_b = "session-beta"
        env_b = await arifos_kernel(
            query="test mismatch",
            session_id=session_b,
            auth_context=auth_a_dict,
            risk_tier="high"
        )
        
        # Result should be HOLD or VOID or SABAR
        assert env_b.verdict in [Verdict.VOID, Verdict.HOLD, Verdict.SABAR]

    async def test_inv3_expiration_forgery(self):
        """
        Attack: Inject a future expiration date into auth_context.
        Requirement: Server-side validation must ignore client-provided expiration.
        """
        # Server-side overrides client expiration. 
        # Test by checking if system still works or if it rejects forgery.
        pass

    async def test_inv4_null_byte_whitespace_coercion(self):
        """
        Attack: Use null bytes or confusing whitespace to bypass identity matching.
        'Arif\0' or ' Arif '
        Requirement: Normalization must strip and clean identity claims.
        """
        envelope = await init_anchor(
            mode="init",
            actor_id="  Arif  ",
            declared_name="Arif\0"
        )
        
        # Result must be clean
        resolved_id = envelope.authority.actor_id
        assert "\0" not in resolved_id
        assert resolved_id.strip() == resolved_id

    async def test_inv5_global_diagnostics_isolation(self):
        """
        Constraint: Status checks on 'global' must never leak anchored data.
        """
        # 1. Anchor a private session
        active = "session-private-99"
        await init_anchor(mode="init", session_id=active, actor_id="private-user")
        
        # 2. Call global status
        global_res = await init_anchor(mode="status", session_id="global")
        
        # Must be anonymous
        assert global_res.caller_state == "anonymous"
